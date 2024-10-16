import smart_open
import zipfile
import re
from pathlib import Path
from boto3 import Session
from osgeo import gdal
import os

s3_url_src = "http://localhost:9000"
s3_bucket_src = "sentinel-2"
archive_name = "cnes_S2A_MSIL1C_20240827T105021_N0511_R051_T30TYP_20240827T132431.zip"
archive_url = s3_url_src + "/" + s3_bucket_src + "/" + archive_name
s3_url_dst = "http://localhost:9000"
s3_bucket_dst = "cog"
aws_access_key_id = "admin"
aws_secret_access_key = "admin"
write_folder = "/tmp/"
__session = None

def get_session() -> Session:
    global __session
    if __session is None:
        __session = Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=None
        )
    return __session

def get_client():
    return get_session().client("s3", endpoint_url=s3_url_dst)


s3_client_dst = get_client()
with smart_open.open(archive_url, "rb") as fb:
    with zipfile.ZipFile(fb) as raster_zip:
        file_names = raster_zip.namelist()
        raster_files = list(filter(lambda f: re.match(r".*/IMG_DATA/.*" + r"_TCI.jp2", f), file_names))
        raster_zip.extract(raster_files[0], write_folder)
        kwargs = {'format': 'COG', 'dstSRS': 'EPSG:3857'}
        gdal.Warp(write_folder + Path(raster_files[0]).stem + '.tif', write_folder + raster_files[0], **kwargs)
        with open(write_folder + Path(raster_files[0]).stem + '.tif', "rb") as cog:
            s3_client_dst.upload_fileobj(cog, s3_bucket_dst, Path(archive_name).stem + '.tif')
        os.remove(write_folder + Path(raster_files[0]).stem + '.tif')
        os.remove(write_folder + raster_files[0])

