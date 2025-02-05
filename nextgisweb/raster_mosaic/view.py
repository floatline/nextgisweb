from nextgisweb.resource import Widget

from .model import RasterMosaic


class ItemWidget(Widget):
    resource = RasterMosaic
    operation = ('create', 'update')
    amdmod = 'ngw-raster-mosaic/ItemWidget'
