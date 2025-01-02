import hashlib
import os

from extensions.aproc.proc.ingest.settings import Configuration


def setup_gdal():
    from osgeo import gdal
    gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN', 'YES')
    gdal.UseExceptions()
    gdal.PushErrorHandler('CPLQuietErrorHandler')
    gdal.VSICurlClearCache()


def get_id(url):
    id = str(url.replace("/", "-").replace(" ","_"))
    if id[0] == "-":
        return id[1:]
    return id


def get_geom_bbox_centroid(ul_lon, ul_lat, ur_lon, ur_lat, lr_lon, lr_lat, ll_lon, ll_lat):
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


def geotiff_to_jpg(input_path, widthPct, heightPct, output_path=None):
    from osgeo import gdal
    # Open input file
    dataset = gdal.Open(input_path)
    output_types = [gdal.GDT_Byte, gdal.GDT_UInt16, gdal.GDT_Float32]
    bands_list = [1]
    if dataset.RasterCount == 3:
        bands_list = [3, 2, 1]
    # Define output format and options
    options = gdal.TranslateOptions(format='JPEG', bandList=bands_list, widthPct=widthPct, heightPct=heightPct, creationOptions=['WORLDFILE=YES'],
                                    outputType=output_types[0])

    # Translate to JPEG
    if output_path is not None:
        gdal.Translate(output_path, dataset, options=options)


def get_file_size(file: str):
    try:
        if file and os.path.exists(file) and os.path.isfile(file):
            return os.stat(file).st_size
    except:
        ...
    return None


def get_epsg(src):
    try:
        from osgeo import osr
        proj = osr.SpatialReference(wkt=src.GetProjection())
        return int(proj.GetAttrValue('AUTHORITY',1))
    except:
        ...
    return None
