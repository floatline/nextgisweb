from nextgisweb.env import Component, require


class ResMetaComponent(Component):

    @require('resource')
    def setup_pyramid(self, config):
        from . import view  # NOQA
        view.setup_pyramid(self, config)
