import os
import re
import sqlite3
from functools import lru_cache
from io import BytesIO
from shutil import copyfile
from typing import Optional
from tempfile import NamedTemporaryFile
from zipfile import ZipFile, is_zipfile

from osgeo import ogr, osr
from PIL import Image, ImageStat
from zope.interface import implementer

from nextgisweb.env import _, Base, COMP_ID, env
from nextgisweb.lib import db
from nextgisweb.lib.osrhelper import sr_from_epsg
from nextgisweb.lib.registry import list_registry

from nextgisweb.core import KindOfData
from nextgisweb.core.exception import ValidationError
from nextgisweb.file_storage import FileObj
from nextgisweb.layer import IBboxLayer, SpatialLayerMixin
from nextgisweb.render import IExtentRenderRequest, IRenderableStyle, ITileRenderRequest
from nextgisweb.resource import (
    DataScope,
    DataStructureScope,
    Resource,
    ResourceGroup,
    SerializedProperty,
    SerializedRelationship,
    Serializer,
)

from nextgisweb.tmsclient.util import render_zoom, crop_box, toggle_tms_xyz_y
from nextgisweb.render.util import pack_color, unpack_color


def imgcolor(img):
    extrema = ImageStat.Stat(img).extrema
    rgba = img.mode == 'RGBA'

    if rgba:
        alpha = extrema[3]
        if alpha[0] == 0 and alpha[1] == 0:
            return (0, 0, 0, 0)

    for comp in extrema:
        if comp[0] != comp[1]:
            return None

    if not rgba:
        extrema = ImageStat.Stat(img.convert('RGBA')).extrema

    return [c[0] for c in extrema]


def transform_extent(extent, src_osr, dst_osr):
    ct = osr.CoordinateTransformation(src_osr, dst_osr)

    def transform_point(x, y):
        p = ogr.Geometry(ogr.wkbPoint)
        p.AddPoint(x, y)
        p.Transform(ct)
        return p.GetX(), p.GetY()

    return transform_point(*extent[0:2]) + transform_point(*extent[2:4])


Base.depends_on('resource')

tilesize = 256


class TilesetData(KindOfData):
    identity = 'tileset'
    display_name = _("Tilesets")


@implementer(IExtentRenderRequest, ITileRenderRequest)
class RenderRequest:
    def __init__(self, style, srs):
        self.style = style
        self.srs = srs

    def render_extent(self, extent, size):
        zoom = render_zoom(self.srs, extent, size, tilesize)
        zoom = min(max(zoom, self.style.minzoom), self.style.maxzoom)
        return self.style.render_image(extent, size, self.srs, zoom)

    def render_tile(self, tile, size):
        zoom = tile[0]
        if not (self.style.minzoom <= zoom <= self.style.maxzoom):
            return None
        extent = self.srs.tile_extent(tile)
        return self.style.render_image(extent, (size, size), self.srs, zoom)


@lru_cache(maxsize=32)
def get_tile_db(db_path):
    return sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)


@implementer(IRenderableStyle, IBboxLayer)
class Tileset(Base, Resource, SpatialLayerMixin):
    identity = 'tileset'
    cls_display_name = _("Tileset")

    __scope__ = (DataStructureScope, DataScope)

    fileobj_id = db.Column(db.ForeignKey(FileObj.id), nullable=False)
    minzoom = db.Column(db.Integer, nullable=False)
    maxzoom = db.Column(db.Integer, nullable=False)
    minx = db.Column(db.Float, nullable=False)
    miny = db.Column(db.Float, nullable=False)
    maxx = db.Column(db.Float, nullable=False)
    maxy = db.Column(db.Float, nullable=False)

    fileobj = db.relationship(FileObj, cascade='all')

    @classmethod
    def check_parent(cls, parent):
        return isinstance(parent, ResourceGroup)

    def render_request(self, srs, cond=None):
        return RenderRequest(self, srs)

    def render_image(self, extent, size, srs, zoom):
        assert srs.id == self.srs.id == 3857

        xtile_from, ytile_from, xtile_to, ytile_to = self.srs.extent_tile_range(extent, zoom)

        width = (xtile_to + 1 - xtile_from) * tilesize
        height = (ytile_to + 1 - ytile_from) * tilesize

        image = None

        db_path = env.file_storage.filename(self.fileobj)
        connection = get_tile_db(db_path)
        for x, y, color, data in connection.execute('''
            SELECT x, y, color, data
            FROM tile
            WHERE z = ? AND (x BETWEEN ? AND ?) AND (y BETWEEN ? AND ?)
        ''', (zoom, xtile_from, xtile_to, ytile_from, ytile_to)):
            if color is not None:
                tile_image = Image.new('RGBA', (tilesize, tilesize), unpack_color(color))
            else:
                tile_image = Image.open(BytesIO(data))
            if image is None:
                image = Image.new('RGBA', (width, height))
            image.paste(tile_image, ((x - xtile_from) * tilesize, (y - ytile_from) * tilesize))

        if image is not None:
            a0x, a1y, a1x, a0y = self.srs.tile_extent((zoom, xtile_from, ytile_from))
            b0x, b1y, b1x, b0y = self.srs.tile_extent((zoom, xtile_to, ytile_to))
            box = crop_box((a0x, b1y, b1x, a0y), extent, width, height)
            image = image.crop(box)

            if image.size != size:
                image = image.resize(size)

        return image

    @property
    def extent(self):
        extent = transform_extent(
            (self.minx, self.miny, self.maxx, self.maxy),
            self.srs.to_osr(), sr_from_epsg(4326))
        return dict(
            minLon=extent[0],
            maxLon=extent[2],
            minLat=extent[1],
            maxLat=extent[3],
        )


@list_registry
class FileFormat:
    pattern: re.Pattern
    group_z: int
    group_x: int
    group_y: int
    offset_z: Optional[int] = 0

    def __init_subclass__(cls):
        cls.pattern = re.compile(cls.pattern, re.IGNORECASE)

    @classmethod
    def get_tile(cls, filename):
        if match := cls.pattern.match(filename):
            return (
                int(match[cls.group_z]) + cls.offset_z,
                int(match[cls.group_x]),
                int(match[cls.group_y]),
            )


class XYZ(FileFormat):
    pattern = r'^(.*/)?(\d+)/(\d+)/(\d+)\.(png|jpe?g)$'
    group_z = 2
    group_x = 3
    group_y = 4


class SASPlanet(FileFormat):
    pattern = r'^(.*/)?z(\d+)/\d+/x(\d+)/\d+/y(\d+)\.png$'
    group_z = 2
    group_x = 3
    group_y = 4
    offset_z = -1


def read_file(fn):
    if is_zipfile(fn):
        fmt = None
        with ZipFile(fn) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                filename = info.filename.replace('\\', '/')  # Fix wrong separator issues
                if fmt is None:
                    for candidate in FileFormat.registry:
                       if candidate.pattern.match(filename):
                           fmt = candidate
                           break
                    else:
                        continue
                if tile := fmt.get_tile(filename):
                    z, x, y = tile
                    data = zf.read(info)
                    yield z, x, y, data
        return

    try:
        connection = sqlite3.connect(f'file:{fn}?mode=ro', uri=True)
    except sqlite3.OperationalError:
        pass
    else:
        try:
            sql_tiles = 'SELECT zoom_level, tile_column, tile_row, tile_data FROM tiles'
            cursor = connection.cursor()
            try:
                row = cursor.execute(sql_tiles + ' LIMIT 1').fetchone()
            except sqlite3.OperationalError:
                pass
            else:
                if row is not None:
                    try:
                        Image.open(BytesIO(row[3]))
                    except IOError:
                        raise ValidationError(message=_("Unsupported data format."))

                for z, x, y, data in cursor.execute(sql_tiles):
                    yield z, x, toggle_tms_xyz_y(z, y), data
                return
        except sqlite3.OperationalError:
            raise ValidationError(message="Error reading SQLite DB.")
        finally:
            connection.close()

    raise ValidationError(message=_("Unknown data format."))


class _source_attr(SerializedProperty):

    def setter(self, srlzr, value):
        if srlzr.obj.id is None:
            srlzr.obj.fileobj = env.file_storage.fileobj(component=COMP_ID)
            dstfile = env.file_storage.filename(srlzr.obj.fileobj, makedirs=True)
        else:
            dstfile = env.file_storage.filename(srlzr.obj.fileobj)
            size = os.stat(dstfile).st_size
            env.core.reserve_storage(
                COMP_ID, TilesetData, value_data_volume=-size, resource=srlzr.obj)

        fn, fn_meta = env.file_upload.get_filename(value['id'])
        stat = dict()
        with NamedTemporaryFile() as tf:
            with sqlite3.connect(tf.name) as connection:
                cursor = connection.cursor()
                cursor.execute('PRAGMA page_size = 8192')
                cursor.execute('PRAGMA journal_mode = OFF')
                cursor.execute('PRAGMA synchronous = OFF')
                cursor.execute('''
                    CREATE TABLE tile (
                        z INTEGER, x INTEGER, y INTEGER,
                        color INTEGER, data BLOB,
                        PRIMARY KEY (z, x, y),
                        CHECK ((color IS NULL) != (data IS NULL))
                    ) WITHOUT ROWID
                ''')

                for z, x, y, img_data in read_file(fn):
                    img = Image.open(BytesIO(img_data))
                    color = imgcolor(img)
                    if color is not None:
                        cursor.execute('''
                            INSERT INTO tile (z, x, y, color) VALUES (?, ?, ?, ?)
                        ''', (z, x, y, pack_color(color)))
                    else:
                        cursor.execute('''
                            INSERT INTO tile (z, x, y, data) VALUES (?, ?, ?, ?)
                        ''', (z, x, y, img_data))

                    if z not in stat:
                        stat[z] = [x, x, y, y]
                    else:
                        stat_zoom = stat[z]
                        if x < stat_zoom[0]:
                            stat_zoom[0] = x
                        elif x > stat_zoom[1]:
                            stat_zoom[1] = x
                        if y < stat_zoom[2]:
                            stat_zoom[2] = y
                        elif y > stat_zoom[3]:
                            stat_zoom[3] = y

                if len(stat) == 0:
                    raise ValidationError(message=_("No tiles found in source."))

                connection.commit()
                cursor.execute('VACUUM')

            copyfile(tf.name, dstfile)

            size = os.stat(dstfile).st_size
            env.core.reserve_storage(
                COMP_ID, TilesetData, value_data_volume=size, resource=srlzr.obj)

        minzoom = maxzoom = None
        for z in stat.keys():
            if minzoom is None:
                minzoom = maxzoom = z
            else:
                if z < minzoom:
                    minzoom = z
                elif z > maxzoom:
                    maxzoom = z
        srlzr.obj.minzoom = minzoom
        srlzr.obj.maxzoom = maxzoom

        minx = maxx = miny = maxy = None
        srs = srlzr.obj.srs
        for z, (xtile_min, xtile_max, ytile_min, ytile_max) in stat.items():
            _minx, _miny, _nvm1, _nvm2 = srs.tile_extent((z, xtile_min, ytile_min))
            _nvm1, _nvm2, _maxx, _maxy = srs.tile_extent((z, xtile_max, ytile_max))
            if minx is None:
                minx, maxx, miny, maxy = _minx, _maxx, _miny, _maxy
            else:
                if _minx < minx:
                    minx = _minx
                if _maxx > maxx:
                    maxx = _maxx
                if _miny < miny:
                    miny = _miny
                if _maxy > maxy:
                    maxy = _maxy
        srlzr.obj.minx = minx
        srlzr.obj.maxx = maxx
        srlzr.obj.miny = miny
        srlzr.obj.maxy = maxy


class TilesetSerializer(Serializer):
    identity = Tileset.identity
    resclass = Tileset

    srs = SerializedRelationship(read=DataStructureScope.read, write=DataStructureScope.write)
    source = _source_attr(write=DataScope.write)
