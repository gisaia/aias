
def setup_gdal():
    from osgeo import gdal
    gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN', 'YES')
    gdal.UseExceptions()
    gdal.PushErrorHandler('CPLQuietErrorHandler')
    gdal.VSICurlClearCache()