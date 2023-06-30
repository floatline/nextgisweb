from pathlib import Path

from nextgisweb.env import Component
from nextgisweb.lib.config import Option


class AuditComponent(Component):
    identity = 'audit'

    def initialize(self):
        self.audit_enabled = self.options['enabled']

        self.audit_file = self.options.get('file', None)

        self.audit_es_enabled = False
        self.file_enabled = self.audit_enabled and self.audit_file is not None
        self.intdb_enabled = self.options['intdb.enabled']

        if self.file_enabled:
            self.file = open(self.options['file'], 'a')

        if self.intdb_enabled:
            from .intdb.sink import Sink
            core = self.env.core
            core.mksdir(self)

            self.intdb_sink_path = Path(core.gtsdir(self) + '/sink')
            self.intdb_storage_path = Path(core.gtsdir(self) + '/duckdb')
            # os.mkdir(self.intdb_sink_path)
            self.intdb_sink = Sink(self.intdb_sink_path)

        # Setup filters from options
        self.request_filters = request_filters = []

        if self.audit_enabled:
            request_filters.append(lambda req: not req.path_info.startswith(
                ("/static/", "/_debug_toolbar/", "/favicon.ico")))

            f_method_inc = self.options['request_method.include']
            if f_method_inc is not None:
                f_method_inc = tuple(f_method_inc)
                request_filters.append(
                    lambda req: req.method in f_method_inc)

            f_method_exc = self.options['request_method.exclude']
            if f_method_exc is not None:
                f_method_exc = tuple(f_method_exc)
                request_filters.append(
                    lambda req: req.method not in f_method_exc)

            f_path_inc = self.options['request_path.include']
            if f_path_inc is not None:
                f_path_inc = tuple(f_path_inc)
                request_filters.append(
                    lambda req: req.path_info.startswith(f_path_inc))

            f_path_exc = self.options['request_path.exclude']
            if f_path_exc is not None:
                f_path_exc = tuple(f_path_exc)
                request_filters.append(
                    lambda req: not req.path_info.startswith(f_path_exc))

    def setup_pyramid(self, config):
        from . import api, view
        api.setup_pyramid(self, config)
        view.setup_pyramid(self, config)

    option_annotations = (
        Option('enabled', bool, default=True),
        Option('elasticsearch.host'),
        Option('elasticsearch.port', int, default=9200),
        Option('elasticsearch.index.prefix', default='nextgisweb-audit'),
        Option('elasticsearch.index.suffix', default='%Y.%m'),
        Option('file', doc='Log events in ndjson format'),
        Option('intdb.enabled', bool, default=True),

        Option('request_method.include', list, default=None,
               doc="Log only given request methods"),
        Option('request_method.exclude', list, default=None,
               doc="Don't log given request methods"),

        Option('request_path.include', list, default=None,
               doc="Log only given request path prefixes"),
        Option('request_path.exclude', list, default=None,
               doc="Don't log given request path prefixes"),
    )
