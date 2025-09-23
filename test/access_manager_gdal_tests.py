import pytest
import aias_common.access.manager as manager

from test.access_manager_tests import CAN_NOT_READ, GDAL_FILES, fixture_am


###########################
# GDAL
###########################

@pytest.mark.parametrize("href", GDAL_FILES)
def test_gdal(fixture_am, href: str):
    from osgeo import gdal
    manager.AccessManager.get_gdal_src(href)
    manager.AccessManager.get_gdal_md(href)
    manager.AccessManager.get_gdal_proj(href)
    manager.AccessManager.get_gdal_info(href, gdal_options=gdal.InfoOptions(format='json'))


@pytest.mark.parametrize("href", CAN_NOT_READ)
def test_gdal_fail(fixture_am, href: str):
    from osgeo import gdal
    with pytest.raises(PermissionError):
        manager.AccessManager.get_gdal_src(href)
    with pytest.raises(PermissionError):
        manager.AccessManager.get_gdal_md(href)
    with pytest.raises(PermissionError):
        manager.AccessManager.get_gdal_proj(href)
    with pytest.raises(PermissionError):
        manager.AccessManager.get_gdal_info(href, gdal_options=gdal.InfoOptions(format='json'))


###########################
# raster io
###########################

@pytest.mark.parametrize("href", FILES)
def test_get_rasterio_session(fixture_am, href: str):
    manager.AccessManager.get_rasterio_session(href)


@pytest.mark.parametrize("href", CAN_NOT_READ)
def test_get_rasterio_session_fail(fixture_am, href: str):
    with pytest.raises(PermissionError):
        manager.AccessManager.get_rasterio_session(href)

