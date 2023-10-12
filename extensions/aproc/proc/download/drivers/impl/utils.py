import pyproj
import rasterio.mask
import shapely.wkt
from osgeo import osr
from rasterio.warp import calculate_default_transform
from shapely.ops import transform


def setup_gdal():
    from osgeo import gdal
    gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN', 'YES')
    gdal.UseExceptions()
    gdal.PushErrorHandler('CPLQuietErrorHandler')
    gdal.VSICurlClearCache()

def extract(crop_wkt, file, driver_target, epsg_target, target_directory, target_file_name,
             target_projection):
    with rasterio.open(file) as src:
        epsg_4326 = pyproj.Proj('EPSG:4326')
        epsg_src = pyproj.Proj(src.crs)
        if not not crop_wkt:
            raw = shapely.wkt.loads(crop_wkt)
            project = pyproj.Transformer.from_proj(epsg_4326, epsg_src, always_xy=True)
            geom = transform(project.transform, raw)
        else:
            from shapely.geometry import box
            raw = shapely.wkt.loads(box(*src.bounds).wkt)
            project = pyproj.Transformer.from_proj(epsg_src, epsg_src, always_xy=True)
            geom = transform(project.transform, raw)
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(int(str(src.crs).split(":")[1]))
        out_image, out_transform = rasterio.mask.mask(src, [geom], crop=crop_wkt is not None)
        out_meta = src.meta.copy()
        default_transform, width, height = calculate_default_transform(epsg_src.crs, epsg_target.crs,
                                                                       out_image.shape[2], out_image.shape[1],
                                                                       *geom.bounds)
        out_meta.update(
            {"driver": driver_target, "nodata": 0, "height": height, "width": width, "transform": default_transform,
             "crs": {'init': target_projection}})
        with rasterio.open(target_directory + "/" + target_file_name, "w", **out_meta) as dest:
            dest.write(out_image)