from contextlib import contextmanager

import pytest
import transaction
from sqlalchemy import func

from nextgisweb.env import DBSession

from nextgisweb.auth import Group, User

from .. import Resource, ResourceACLRule, ResourceGroup


def test_disable_resources(
    ngw_env, ngw_webtest_app,
    ngw_auth_administrator, ngw_resource_group
):
    def create_resource_group(display_name, expected_status):
        ngw_webtest_app.post_json('/api/resource/', dict(resource=dict(
            cls='resource_group', parent=dict(id=ngw_resource_group),
            display_name=display_name)
        ), status=expected_status)

    with ngw_env.resource.options.override({'disable.resource_group': True}):
        create_resource_group('disable.resource_group', 422)

    with ngw_env.resource.options.override({'disabled_cls': ['resource_group', ]}):
        create_resource_group('diabled_cls', 422)


@pytest.fixture(scope='module')
def resource(ngw_resource_group):
    with transaction.manager:
        obj = ResourceGroup(
            parent_id=ngw_resource_group, display_name='Test Юникод Symbols ~%',
            keyname='Test-Keyname',
            owner_user=User.by_keyname('administrator'),
        ).persist()

        DBSession.flush()
        DBSession.expunge(obj)

    yield obj

    with transaction.manager:
        DBSession.delete(ResourceGroup.filter_by(id=obj.id).one())


def test_resource_search(resource, ngw_webtest_app, ngw_auth_administrator):
    api_url = '/api/resource/search/'

    resp = ngw_webtest_app.get(api_url, dict(
        display_name='Test Юникод Symbols ~%'), status=200)
    assert len(resp.json) == 1

    resp = ngw_webtest_app.get(api_url, dict(
        display_name='Test Юникод Symbols ~%', keyname='other'), status=200)
    assert len(resp.json) == 0

    resp = ngw_webtest_app.get(api_url, dict(
        display_name__ilike='test юни%'), status=200)
    assert len(resp.json) == 1
    assert resp.json[0]['resource']['display_name'] == resource.display_name


@pytest.fixture(scope='module')
def resources(ngw_resource_group):
    # R - A
    #   - B - C
    #       - D
    with transaction.manager:
        admin = User.by_keyname('administrator')
        res_R = ResourceGroup(
            parent_id=ngw_resource_group, display_name='Test resource ROOT',
            keyname='test_res_R', owner_user=admin,
        ).persist()
        res_A = ResourceGroup(
            parent=res_R, display_name='Test resource A',
            keyname='test_res_A', owner_user=admin,
        ).persist()
        res_B = ResourceGroup(
            parent=res_R, display_name='Test resource B',
            keyname='test_res_B', owner_user=admin,
        ).persist()
        res_C = ResourceGroup(
            parent=res_B, display_name='Test resource C',
            keyname='test_res_C', owner_user=admin,
        ).persist()
        res_D = ResourceGroup(
            parent=res_B, display_name='Test resource D',
            keyname='test_res_D', owner_user=admin,
        ).persist()
        DBSession.flush()

    yield

    with transaction.manager:
        DBSession.delete(res_D)
        DBSession.delete(res_C)
        DBSession.delete(res_B)
        DBSession.delete(res_A)
        DBSession.delete(res_R)


@pytest.mark.parametrize('root_keyname, keynames_expected', (
    ('test_res_R', {'test_res_R', 'test_res_A', 'test_res_B', 'test_res_C', 'test_res_D'}),
    ('test_res_B', {'test_res_B', 'test_res_C', 'test_res_D'}),
))
def test_resource_search_parent_id_recursive(
    resources, root_keyname, keynames_expected, ngw_webtest_app,
    ngw_auth_administrator
):
    response = ngw_webtest_app.get('/api/resource/search/', dict(keyname=root_keyname))
    root_id = response.json[0]['resource']['id']

    data = ngw_webtest_app.get('/api/resource/search/', dict(parent_id__recursive=root_id)).json
    keynames = {item['resource']['keyname'] for item in data}

    assert keynames == keynames_expected


@pytest.fixture
def resource_stat():
    with DBSession.no_autoflush:
        cls_count = dict(
            (cls, count) for cls, count in DBSession.query(
                Resource.cls, func.count(Resource.id)
            ).group_by(Resource.cls))
    total = sum(cls_count.values())
    yield total, cls_count


@pytest.fixture
def override(ngw_env):
    comp = ngw_env.resource
    @contextmanager
    def wrapped(**kw):
        options = dict(
            limit=None, resource_cls=None, resource_by_cls=dict(),
        )
        options.update(kw)

        mem = dict()
        for k, v in options.items():
            attr = f'quota_{k}'
            mem[attr] = getattr(comp, attr)
            setattr(comp, attr, v)
        try:
            yield
        finally:
            for k, v in mem.items():
                setattr(comp, k, v)
    return wrapped


def test_quota(
    ngw_resource_group, resource_stat, override, ngw_webtest_app, ngw_auth_administrator
):
    total, cls_count = resource_stat

    def create_resource_group(display_name, expected_status):
        resp = ngw_webtest_app.post_json('/api/resource/', dict(resource=dict(
            cls='resource_group', parent=dict(id=ngw_resource_group),
            display_name=display_name)
        ), status=expected_status)

        if resp.status_code == 201:
            resource_id = resp.json['id']
            ngw_webtest_app.delete(f'/api/resource/{resource_id}')

    def check_quota(data, expected_status, expected_result=None):
        resp = ngw_webtest_app.post_json(
            '/api/component/resource/check_quota', data, status=expected_status)
        if expected_result is not None:
            assert expected_result.items() <= resp.json.items()

    with override():
        check_quota(dict(resource_group=999), 200)
        create_resource_group("No quota", 201)

    with override(limit=total):
        check_quota(dict(resource_group=0), 200)
        check_quota(dict(resource_group=1), 402, dict(cls=None, required=1, available=0))
        create_resource_group("Quota exceeded", 402)

    rg_count = cls_count.get('resource_group', 0)

    with override(limit=rg_count, resource_cls=['resource_group']):
        check_quota(dict(resource_group=0), 200)
        check_quota(dict(resource_group=1), 402, dict(
            cls=None, required=1, available=0))
        create_resource_group("Quota exceeded resource_group", 402)

    with override(limit=rg_count, resource_cls=['another_resource_cls']):
        check_quota(dict(resource_group=999), 200)
        create_resource_group("Quota exceeded another cls", 201)

    with override(resource_by_cls=dict(resource_group=rg_count)):
        check_quota(dict(resource_group=0), 200)
        check_quota(dict(resource_group=1), 402, dict(
            cls='resource_group', required=1, available=0))
        create_resource_group("Quota by cls exceeded", 402)

    with override(resource_by_cls=dict(another_resource_cls=rg_count)):
        check_quota(dict(resource_group=999), 200)
        create_resource_group("Quota by cls exceeded another cls", 201)

    with override(limit=total + 5):
        check_quota(dict(resource_group=5), 200)
        check_quota(dict(resource_group=6), 402, dict(cls=None, required=6, available=5))

    with override(limit=rg_count + 5, resource_cls=['resource_group']):
        check_quota(dict(resource_group=5), 200)
        check_quota(dict(resource_group=7), 402, dict(cls=None, required=7, available=5))


@pytest.fixture
def admin():
    with transaction.manager:
        admin = User(
            keyname='test_admin',
            display_name="Test admin",
            member_of=[Group.filter_by(keyname='administrators').one()],
        ).persist()
    try:
        yield admin.id
    finally:
        with transaction.manager:
            ResourceACLRule.filter_by(principal_id=admin.id).delete()
            DBSession.delete(User.filter_by(id=admin.id).one())


def test_admin_permissions(admin, ngw_webtest_app, ngw_auth_administrator, ngw_resource_group):

    permissions = ngw_webtest_app.get('/api/resource/0').json['resource']['permissions']

    def check_perm_change(data, status_expected, *, resource_id=0):
        perm_data = dict(
            action='deny', identity='', permission='',
            principal=dict(id=admin), propagate=False, scope='')
        perm_data.update(data)
        ngw_webtest_app.put_json(f'/api/resource/{resource_id}', dict(
            resource=dict(permissions=permissions + [perm_data])
        ), status=status_expected)

    check_perm_change(dict(), 422)
    check_perm_change(dict(), 200, resource_id=ngw_resource_group)
    check_perm_change(dict(permission='manage_children'), 200)
    check_perm_change(dict(scope='metadata', permission='read'), 200)
    check_perm_change(dict(scope='resource', permission='read'), 422)
    check_perm_change(dict(scope='resource', permission='update'), 422)
    check_perm_change(dict(scope='resource', permission='change_permissions'), 422)
