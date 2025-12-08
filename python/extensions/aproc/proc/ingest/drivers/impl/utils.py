import hashlib
import os
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


def get_geom_bbox_centroid(ul_lon: float, ul_lat: float, ur_lon: float, ur_lat: float, lr_lon: float, lr_lat: float, ll_lon: float, ll_lat: float):
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
            bands_list = [3, 2, 1]

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
        ...
    return None


def get_epsg_from_gdal_info(path: str):
    from osgeo import gdal

    info = AccessManager.get_gdal_info(path, gdal.InfoOptions(format="json"))
    return get_epsg(info["gcps"]["coordinateSystem"]["wkt"])


def downsample_image(image_path: str, downsampled_image_path: str, block_size: int):
    """
    Downsamples an image by the given block_size factor
    """
    import numpy as np
    from PIL import Image
    from skimage.measure import block_reduce

    image = Image.open(image_path)
    image_data = np.asarray(image)
    reduced_image = block_reduce(image_data, block_size=block_size, func=np.average)

    Image.fromarray(np.asarray(reduced_image, image_data.dtype), image.mode).save(downsampled_image_path)
