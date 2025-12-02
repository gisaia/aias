import hashlib
import os
import re
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
    import json

    from osgeo import ogr
    coordinates = [[ul_lon, ul_lat],
                   [ur_lon, ur_lat],
                   [lr_lon, lr_lat],
                   [ll_lon, ll_lat]]
    bbox = [min(map(lambda xy: xy[0], coordinates)),
            min(map(lambda xy: xy[1], coordinates)),
            max(map(lambda xy: xy[0], coordinates)),
            max(map(lambda xy: xy[1], coordinates))]
    coordinates.append(coordinates[0])
    # Define geometry
    geometry = {
        "type": "Polygon",
        "coordinates": [coordinates]
    }
    geom = ogr.CreateGeometryFromJson(json.dumps(geometry))
    centroid_geom = geom.Centroid()
    centroid_geom_list = str(centroid_geom).replace("(", "").replace(")", "").split(" ")
    # Define centroid
    centroid = [float(centroid_geom_list[1]), float(centroid_geom_list[2])]
    return geometry, bbox, centroid


def get_hash_url(url: str) -> str:
    tohash = url
    components = url.split(os.path.sep)
    if Configuration.settings.resource_id_hash_starts_at > 1 and len(components) > Configuration.settings.resource_id_hash_starts_at:
        tohash = "/".join(url.split(os.path.sep)[Configuration.settings.resource_id_hash_starts_at:])
    return hashlib.sha256(tohash.encode("utf-8")).hexdigest()


def geotiff_to_jpg(input_path: str, width_pct: float, height_pct: float, output_path=None, bands_list=None):
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
    # Define output format and options
    options = gdal.TranslateOptions(format='JPEG', bandList=bands_list, widthPct=width_pct, heightPct=height_pct, creationOptions=['WORLDFILE=YES'],
                                    outputType=output_types[0])

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


def get_epsg_from_gdal_info(path: str):
    from osgeo import gdal
    info = AccessManager.get_gdal_info(path, gdal.InfoOptions(format="json"))
    return get_epsg(info["gcps"]["coordinateSystem"]["wkt"])


#Level-1 Product Family Summary Table Dictionary
level1_summary = {
    'SM': {
        'SLC': {'resolution': '1.7–3.6 m × 4.3–4.9 m', 'pixel_spacing': '1.5–3.1 m × 3.6–4.1 m', 'looks': '1 × 1', 'ENL': 1},
        'GRD_FR': {'resolution': '9 × 9 m', 'pixel_spacing': '3.5 × 3.5 m', 'looks': '2 × 2', 'ENL': 3.7},
        'GRD_HR': {'resolution': '23 × 23 m', 'pixel_spacing': '10 × 10 m', 'looks': '6 × 6', 'ENL': 29.7},
        'GRD_MR': {'resolution': '84 × 84 m', 'pixel_spacing': '40 × 40 m', 'looks': '22 × 22', 'ENL': 398.4},
    },
    'IW': {
        'SLC': {'resolution': '2.7–3.5 m × 22 m', 'pixel_spacing': '2.3 m × 14.1 m', 'looks': '1 × 1', 'ENL': 1},
        'GRD_HR': {'resolution': '20 × 22 m', 'pixel_spacing': '10 × 10 m', 'looks': '5 × 1', 'ENL': 4.4},
        'GRD_MR': {'resolution': '88 × 87 m', 'pixel_spacing': '40 × 40 m', 'looks': '22 × 5', 'ENL': 81.8},
    },
    'EW': {
        'SLC': {'resolution': '7.9–15 m × 43 m', 'pixel_spacing': '5.9 × 19.9 m', 'looks': '1 × 1', 'ENL': 1},
        'GRD_HR': {'resolution': '50 × 50 m', 'pixel_spacing': '25 × 25 m', 'looks': '3 × 1', 'ENL': 2.8},
        'GRD_MR': {'resolution': '93 × 87 m', 'pixel_spacing': '40 × 40 m', 'looks': '6 × 2', 'ENL': 10.7},
    },
    'WV': {
        'SLC': {'resolution': '2.0–3.1 m × 4.8 m', 'pixel_spacing': '1.7–2.7 m × 4.1 m', 'looks': '1 × 1', 'ENL': 1},
        'GRD_MR': {'resolution': '52 × 51 m', 'pixel_spacing': '25 × 25 m', 'looks': '13 × 13', 'ENL': 123.7},
    }
}

def parse_sentinel1_filename(filename):
    base = filename.split('/')[-1]
    parts = base.split('_')

    if len(parts) < 3:
        raise ValueError("Invalid name File")

    satellite = parts[0]  # S1A, S1B, S1C
    mode = parts[1]       # SM, IW, EW, WV
    product_type = parts[2]  # SLC, GRD

    res_pol = parts[3] if len(parts) > 3 else ''

    return satellite, mode, product_type, res_pol

def extract_pixel_spacing_numbers(pixel_spacing_str):
    """
    Extracts the numerical values ​​of the pixel spacing (range × azimuth)
    """
    # Remove the units and separate by ×
    nums = re.findall(r'[\d\.]+', pixel_spacing_str)
    if len(nums) >= 2:
        return float(nums[0]), float(nums[1])
    else:
        return float(nums[0]), float(nums[0])  # if only one number, we repeat

def get_product_values(filename):
    sat, mode, prod_type, res_pol = parse_sentinel1_filename(filename)

    if prod_type.startswith('GRD'):
        if 'FR' in filename:
            prod_key = 'GRD_FR'
        elif 'HR' in filename:
            prod_key = 'GRD_HR'
        elif 'MR' in filename:
            prod_key = 'GRD_MR'
        else:
            prod_key = 'GRD_MR'
    else:
        prod_key = prod_type

    try:
        values = level1_summary[mode][prod_key]
    except KeyError:
        raise ValueError(f"Mode {mode} or type {prod_key} unknown in the Level-1 array.")

    range_ps, azimuth_ps = extract_pixel_spacing_numbers(values['pixel_spacing'])
    max_pixel_spacing = max(range_ps, azimuth_ps)

    result = {
        'satellite': sat,
        'mode': mode,
        'product_type': prod_type,
        'resolution': values['resolution'],
        'pixel_spacing': values['pixel_spacing'],
        'looks': values['looks'],
        'ENL': values['ENL'],
        'max_pixel_spacing': max_pixel_spacing
    }

    return result
