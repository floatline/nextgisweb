from nextgisweb.env.cli import EnvCommand, cli


@cli.group()
class audit:
    pass


@audit.command()
def collect(self: EnvCommand):
    from .database import collect
    collect()
