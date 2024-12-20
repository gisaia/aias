import hashlib
import os
import shutil
import time
from contextlib import contextmanager
from datetime import datetime

from airs.core.models.model import Item
from aproc.core.logger import Logger

LOGGER = Logger.logger


def setup_gdal():
    from osgeo import gdal
    gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN', 'YES')
    gdal.SetConfigOption('OSR_USE_ETMERC', 'YES')
    gdal.UseExceptions()
    gdal.PushErrorHandler('CPLQuietErrorHandler')
    gdal.VSICurlClearCache()


def prepare_wkt_extract(wkt: str, target_crs):
    import pyproj
    import shapely.wkt
    import shapely.ops

    epsg_4326 = pyproj.Proj('EPSG:4326')
    epsg_target = pyproj.Proj(target_crs)

    raw = shapely.wkt.loads(wkt)
    project = pyproj.Transformer.from_proj(epsg_4326, epsg_target, always_xy=True)
    geom = shapely.ops.transform(project.transform, raw)
    return geom


def extract(images, crop_wkt, file, driver_target, target_projection, target_directory, target_file_name):
    import pyproj
    import rasterio.mask
    if crop_wkt:
        with rasterio.open(file) as src:
            geom = prepare_wkt_extract(crop_wkt, src.crs)
            out_image, out_transform = rasterio.mask.mask(src, [geom], crop=True)

            out_meta = src.meta.copy()
            update_params = {"height": out_image.shape[1],
                             "width": out_image.shape[2],
                             "transform": out_transform,
                             "driver": driver_target
                             }
            out_meta.update(update_params)
            writeWorldWidefrom_transform(out_transform, target_directory + "/" + target_file_name)
            with rasterio.open(target_directory + "/" + target_file_name, "w", **out_meta, quality=100, reversible=True) as dest:
                dest.write(out_image)
    else:
        epsg_target = pyproj.Proj(target_projection)
        if images and len(images) > 1:
            for image in images:
                with reproject_raster(image[0], epsg_target.crs, driver_target) as in_mem_ds:
                    kwargs = in_mem_ds.meta.copy()
                    writeWorldWidefrom_transform(in_mem_ds.transform, target_directory + "/" + image[1])
                    with rasterio.open(target_directory + "/" + image[1], "w", **kwargs, quality=100, reversible=True) as dest:
                        dest.write(in_mem_ds.read())
        else:
            with reproject_raster(file, epsg_target.crs, driver_target) as in_mem_ds:
                kwargs = in_mem_ds.meta.copy()
                writeWorldWidefrom_transform(in_mem_ds.transform, target_directory + "/" + target_file_name)
                with rasterio.open(target_directory + "/" + target_file_name, "w", **kwargs, quality=100, reversible=True) as dest:
                    dest.write(in_mem_ds.read())


@contextmanager
def reproject_raster(in_path, crs, driver_target):
    import rasterio.mask
    from rasterio.io import MemoryFile
    from rasterio.warp import (Resampling, calculate_default_transform,
                               reproject)

    # reproject raster to project crs
    with rasterio.open(in_path) as src:
        src_crs = src.crs
        transform, width, height = calculate_default_transform(src_crs, crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()

        kwargs.update({
            "driver": driver_target,
            'crs': crs,
            'transform': transform,
            'width': width,
            'height': height})

        with MemoryFile() as memfile:
            with memfile.open(**kwargs) as dst:
                if src.crs != crs:
                    for i in range(1, src.count + 1):
                        reproject(
                            source=rasterio.band(src, i),
                            destination=rasterio.band(dst, i),
                            src_transform=src.transform,
                            src_crs=src.crs,
                            dst_transform=transform,
                            dst_crs=crs,
                            resampling=Resampling.nearest)
                else:
                    dst.write(src.read())
            with memfile.open() as dataset:  # Reopen as DatasetReader
                yield dataset  # Note yield not return as we're a contextmanager


def make_raw_archive_zip(href: str, target_directory: str):
    file_name = os.path.basename(href)
    # Get direct parent folder of href_file to zip
    dir_name = os.path.dirname(href)
    target_file_name = os.path.splitext(file_name)[0] + datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    shutil.make_archive(target_directory + "/" + target_file_name, 'zip', dir_name)
    return


def writeWorldWidefrom_transform(affine, input):
    geotransform = affine
    (fpath, fname) = os.path.split(input)
    (shortname, ext) = os.path.splitext(fname)
    wext = '.' + ext[1] + ext[-1] + 'w'
    output = os.path.join(fpath, shortname) + wext
    if geotransform is not None:
        world_file = open(output, 'w')
        x = geotransform[2]
        x_size = geotransform[0]
        x_rot = geotransform[1]
        y = geotransform[5]
        y_rot = geotransform[3]
        y_size = geotransform[4]
        x = x_size / 2 + x
        y = y_size / 2 + y
        world_file.write('%s\n' % x_size)
        world_file.write('%s\n' % x_rot)
        world_file.write('%s\n' % y_rot)
        world_file.write('%s\n' % y_size)
        world_file.write('%s\n' % x)
        world_file.write('%s\n' % y)
        world_file.close()


def get_file_name(item: Item, target_format: str):
    file_name = os.path.basename(
        item.id.replace("-", "_").replace(" ", "_")
            .replace("/", "_").replace("\\", "_").replace("@", "_")) + "." + target_format
    if os.path.exists(file_name):
        file_name = hashlib.md5(str(time.time_ns()).encode("utf-8")).hexdigest() + file_name
    return file_name
