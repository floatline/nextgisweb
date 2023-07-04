from nextgisweb.env import Component

from .model import Base


class TilesetComponent(Component):
    identity = 'tileset'
    metadata = Base.metadata

    def setup_pyramid(self, config):
        from . import view
        view.setup_pyramid(self, config)
