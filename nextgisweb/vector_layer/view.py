from nextgisweb.resource import Widget

from .model import VectorLayer


class VectorLayerWidget(Widget):
    resource = VectorLayer
    operation = ('create', 'update')
    amdmod = 'ngw-vector-layer/Widget'
