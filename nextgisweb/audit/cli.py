from nextgisweb.env.cli import EnvCommand, cli

from .component import AuditComponent


@cli.group()
class audit:
    pass


@audit.command()
def collect(self: EnvCommand, *, comp: AuditComponent):
    from .intdb.collector import collect
    collect(comp.intdb_sink_path, comp.intdb_storage_path)
