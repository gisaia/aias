import hashlib
import os
import xml.etree.ElementTree as ET
from typing import Callable

from aias_common.access.manager import AccessManager
from extensions.aproc.proc.ingest.settings import Configuration


def setup_gdal():
    from osgeo import gdal
    gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN', 'YES')
    gdal.UseExceptions()
    gdal.PushErrorHandler('CPLQuietErrorHandler')
    gdal.VSICurlClearCache()


def get_id(url: str):
    url_id = str(url.replace("/", "-").replace(" ", "_"))
    if url_id[0] == "-":
        return url_id[1:]
    return url_id


def get_geom_bbox_centroid_from_coordinates(coordinates: list[list[float, float]]):
    from shapely.geometry import Polygon

    geometry = {
        "type": "Polygon",
        "coordinates": [coordinates]
    }

    polygon = Polygon(coordinates)
    bbox = list(polygon.bounds)
    centroid = [polygon.centroid.x, polygon.centroid.y]
    return geometry, bbox, centroid


def get_geom_bbox_centroid_from_corners(ul_lon: float, ul_lat: float, ur_lon: float, ur_lat: float, lr_lon: float, lr_lat: float, ll_lon: float, ll_lat: float):
    coordinates = [[ul_lon, ul_lat],
                   [ur_lon, ur_lat],
                   [lr_lon, lr_lat],
                   [ll_lon, ll_lat]]
    bbox = get_bbox(coordinates)

    # Define geometry
    coordinates.append(coordinates[0])
    geometry = {
        "type": "Polygon",
        "coordinates": [coordinates]
    }

    return geometry, bbox, get_centroid(geometry)


def compute_simplified_polygon(gcp_list)->list[list[float]]:
    from scipy.spatial import ConvexHull
    import numpy as np
    # Extract (x, y) coordinates
    points = np.array([[gcp["x"], gcp["y"]] for gcp in gcp_list])

    # Compute convex hull
    hull = ConvexHull(points)
    hull_points = points[hull.vertices]

    englobing_polygon = np.append(hull_points, [hull_points[0]], axis=0)
    return englobing_polygon.tolist()


def get_bbox(coordinates: list[list[float]]):
    return [min([xy[0] for xy in coordinates]),
            min([xy[1] for xy in coordinates]),
            max([xy[0] for xy in coordinates]),
            max([xy[1] for xy in coordinates])]


def get_centroid(geometry):
    """
    Computes the centroid of a GeoJSON Polygon
    """
    import json

    from osgeo import ogr

    geom = ogr.CreateGeometryFromJson(json.dumps(geometry))
    centroid_geom = geom.Centroid()
    centroid_geom_list = str(centroid_geom).replace("(", "").replace(")", "").split(" ")
    # Define centroid
    centroid = [float(centroid_geom_list[1]), float(centroid_geom_list[2])]

    return centroid


def get_hash_url(url: str) -> str:
    tohash = url
    components = url.split(os.path.sep)
    if Configuration.settings.resource_id_hash_starts_at > 1 and len(components) > Configuration.settings.resource_id_hash_starts_at:
        tohash = "/".join(url.split(os.path.sep)[Configuration.settings.resource_id_hash_starts_at:])
    return hashlib.sha256(tohash.encode("utf-8")).hexdigest()


def geotiff_to_jpg(input_path: str, width_pct: float, height_pct: float, output_path=None, bands_list=None, stretch=False):
    """
    Converts a GeoTIFF to a JPG. Compatible with all AccessManager compatible object storages
    """
    from osgeo import gdal

    # Open input file
    dataset = AccessManager.get_gdal_src(input_path)
    output_types = [gdal.GDT_Byte, gdal.GDT_UInt16, gdal.GDT_Float32]
    if bands_list is None:
        bands_list = [1]
        if dataset.RasterCount == 3:
            bands_list = [1, 2, 3]

    scale_params = None
    if stretch:
        scale_params = []
        for idx in bands_list:
            band_min, band_max = dataset.GetRasterBand(idx).ComputeRasterMinMax(approx_ok=True)
            scale_params.append([band_min, band_max])

    # Define output format and options
    options = gdal.TranslateOptions(format='JPEG', bandList=bands_list, widthPct=width_pct, heightPct=height_pct, creationOptions=['WORLDFILE=YES'],
                                    outputType=output_types[0], scaleParams=scale_params)

    # Translate to JPEG
    if output_path is not None:
        gdal.Translate(output_path, dataset, options=options)


def get_epsg(proj):
    """
    Returns the EPSG code of an archive from its archive's projection
    """
    try:
        from osgeo import osr
        proj = osr.SpatialReference(wkt=proj)
        return int(proj.GetAttrValue('AUTHORITY', 1))
    except Exception:
        return None


def get_epsg_from_gdal_info_gcps(path: str) -> int | None:
    try:
        from osgeo import gdal
        info = AccessManager.get_gdal_info(path, gdal.InfoOptions(format="json"))
        return get_epsg(info.get("gcps", {}).get("coordinateSystem", {}).get("wkt", None))
    except Exception:
        return None


def downsample_image(image_path: str, out_path: str, factor: int):
    """
    Downsamples an image by the given factor
    """
    from PIL import Image

    if not AccessManager.is_local(image_path):
        raise PermissionError(f"Image downsample can only be done on local images; {image_path} is not")

    with Image.open(image_path) as im:
        im_new = im.reduce(factor)
        im_new.save(out_path)


def find_or_none(root: ET.Element, key: str, process: Callable = None, ns: dict[str, str] = {}, alt_keys: list[str] = []):
    """
    Tries to find the key in the given element. If found, returns its text value, optionally processed
    """
    value = root.find(key, ns)
    if value is None and alt_keys:
        for alt_key in alt_keys:
            value = root.find(alt_key, ns)
            if value:
                break

    if value is not None:
        if process is not None:
            return process(value.text)
        return value.text

    return None
