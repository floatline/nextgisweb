import csv
from io import StringIO
from math import ceil

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from flatdict import FlatDict
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from sqlalchemy import func

from nextgisweb.env import DBSession

from nextgisweb.pyramid import JSONType

from .model import tab_log


def audit_cget(request) -> JSONType:
    def _extract(pth):
        return tab_log.c.data.op('#>>')(sa.text("'{" + ','.join(pth.split('.')) + "}'"))

    q = sa.select(
        tab_log.c.tstamp,
        _extract('user.display_name').label('user_id'),
        _extract('request.method').label('request_method'),
    )

    if before := request.GET.get('before'):
        q = q.where(tab_log.c.tstamp < before)

    if after := request.GET.get('after'):
        q = q.where(tab_log.c.tstamp >= after)

    if limit := request.GET.get('limit'):
        q = q.limit(int(limit))

    q = q.order_by(tab_log.c.tstamp.asc())

    return [
        dict(tstamp=r['tstamp'], request_method=r['request_method'], user_id=r['user_id'])
        for r in DBSession.execute(q)
    ]


def export(request):
    request.require_administrator()

    date_from = request.params.get("date_from")
    date_to = request.params.get("date_to")
    user = request.params.get("user")

    hits = audit_cget(
        request=request,
        date_from=date_from,
        date_to=date_to,
        user=user,
    )

    hits = map(lambda h: h.to_dict(), hits)
    hits = map(lambda h: FlatDict(h, delimiter='.'), hits)
    hits = list(hits)

    if len(hits) == 0:
        raise HTTPNotFound()

    buf = StringIO()
    writer = csv.writer(buf, dialect='excel')

    headrow = (
        '@timestamp',
        'request.method',
        'request.path',
        'request.query_string',
        'request.remote_addr',
        'response.status_code',
        'response.route_name',
        'user.id',
        'user.keyname',
        'user.display_name',
        'context.id',
        'context.model',
    )
    writer.writerow(headrow)

    for hit in hits:
        datarow = map(lambda key: hit.get(key), headrow)
        writer.writerow(datarow)

    content_disposition = 'attachment; filename=audit.csv'

    return Response(
        buf.getvalue(),
        content_type='text/csv',
        content_disposition=content_disposition
    )


def setup_pyramid(comp, config):
    config.add_route('audit.query', '/api/component/audit/query').add_view(audit_cget)

    if False and comp.audit_es_enabled:
        config.add_route(
            'audit.export', '/api/component/audit/export') \
            .add_view(export, request_method='GET')
