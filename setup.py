import io
import os
import os.path
import sys
from setuptools import find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from stat import S_IXGRP, S_IXOTH, S_IXUSR
from subprocess import CalledProcessError, check_output

with io.open('VERSION', 'r') as fd:
    VERSION = fd.read().rstrip()

try:
    gv = check_output(['gdal-config', '--version'], universal_newlines=True).strip()
except CalledProcessError:
    gv = None

requires = [
    'affine==2.4.0',
    'attrs==23.1.0',
    'babel==2.12.1',
    'cachetools==5.3.1',
    'docstring-parser==0.15',
    'elasticsearch>=7.0.0,<8.0.0',
    'elasticsearch-dsl>=7.1.0,<8.0.0',
    'flatdict==4.0.1',
    'geoalchemy2==0.13.3',
    'httpx[http2]==0.24.1',
    'humanize==4.6.0',
    'importlib_metadata; python_version<"3.10"',
    'lxml==4.9.2',
    'msgspec==0.16.0',
    'numpy',
    'networkx',
    'orjson==3.8.14',
    'OWSLib==0.29.2',
    'passlib==1.7.4',
    'pillow==9.5.0',
    'poeditor',
    'psutil==5.9.5',
    'psycopg2==2.9.6',
    'pygdal' + (f'=={gv}.*,' if gv else '') + '>=3',
    'pyproj==3.4.1',
    'pyramid==2.0.1',
    'pyramid-mako==1.1.0',
    'pyramid-tm==2.5',
    'python-magic==0.4.27',
    'python-ulid==1.1.0',
    'requests==2.31.0',
    'sentry-sdk==1.9.10',
    'shapely==1.8.5',
    'SQLAlchemy==1.4.48',
    'transaction==3.1.0',
    'ua-parser==0.16.1',
    'waitress==2.1.2',
    'zipstream-new==1.1.8',
    'zope.sqlalchemy==1.6',
    'zope.interface==5.5.2',
    'zope.event==4.6',
]

extras_require = dict(development=[
    'coverage',
    'flake8-future-import',
    'flake8',
    'freezegun',
    'pyramid-debugtoolbar==4.10',
    'pytest-flake8',
    'pytest-watch',
    'pytest==7.3.*',
    'ruff',
    'webtest',
])

entry_points = {
    'paste.app_factory': [
        'main = nextgisweb:main'
    ],

    'babel.extractors': [
        'hbs = nextgisweb.i18n.hbs:extract',
    ],

    'pytest11': [
        'nextgisweb = nextgisweb.pytest',
        'nextgisweb.core = nextgisweb.core.test',
        'nextgisweb.pyramid = nextgisweb.pyramid.test',
        'nextgiswev.auth = nextgisweb.auth.test',
        'nextgiswev.resource = nextgisweb.resource.test',
    ],

    'nextgisweb.packages': ['nextgisweb = nextgisweb:pkginfo', ],
}


class DevelopCommand(develop):
    def run(self):
        develop.run(self)

        # Builtin console_scripts entrypoint scripts are very slow because of
        # checking package requirement. So we use generated wrapper scripts.

        bin_dir, _ = os.path.split(sys.executable)
        for name, module, func in (
            ('nextgisweb', 'nextgisweb.script', 'main'),
            ('nextgisweb-config', 'nextgisweb.script', 'config'),
            ('nextgisweb-i18n', 'nextgisweb.i18n.script', 'main'),
        ):
            sf = os.path.join(bin_dir, name)
            with open(sf, 'w') as fd:
                fd.write("#!{}\n".format(sys.executable))
                fd.write("from {} import {} as main\n".format(module, func))
                fd.write("if __name__ == '__main__': main()\n")

            st = os.stat(sf)
            os.chmod(sf, st.st_mode | S_IXUSR | S_IXGRP | S_IXOTH)


class InstallCommand(install):
    def run(self):
        raise RuntimeError(
            "Only development mode installation "
            "(pip install -e ...) is supported!")
        install.run(self)


setup(
    name='nextgisweb',
    version=VERSION,
    description='NextGIS Web main package',
    author='NextGIS',
    author_email='info@nextgis.com',
    url='https://nextgis.com/nextgis-web',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8,<4",
    install_requires=requires,
    extras_require=extras_require,
    entry_points=entry_points,
    cmdclass=dict(
        develop=DevelopCommand,
        install=InstallCommand,
    )
)
