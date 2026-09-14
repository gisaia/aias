import os
import unittest
from airs.core.models.model import AssetFormat, Role
from aproc.core.models.ogc.enums import StatusCode

from test.aproc_ingest_tests import (AST, AXELGLOBE, CAPELLA1, CAPELLA2, CAPELLA3, CSK, CSK2, GEOSAT_JP2, SPOT6, GEOSAT, ICEYE, IKONOS, JP2000, PNEOMS, PNEOPAN,
                                     RADARSAT2, RAPID_EYE, SATELLOGIC, SENTINEL1_GRDH, SUPERVIEW, SUPERVIEW3_4, WYVERN, LANDSAT9,
                                     SENTINEL1_SLC, SENTINEL2, SKYSAT, SPOT5,
                                     TERRASARX, TERRASARX_PAZ, TIF, WORLDVIEW, UMBRA_STAC, IngestTests)
from test.utils import CATALOG, COLLECTION, SENTINEL2_BANDS

ROOT = "gs://gisaia-public/test-aias"


class Tests(IngestTests):

    def test_async_ingest_invalid_tif(self):  # Test Driver error handling
        url = os.path.join(ROOT, "images/empty.tiff")
        status = self.ingest(url, COLLECTION, CATALOG, StatusCode.failed)
        self.assertGreaterEqual(status.message.find("Exception while ingesting"), 0)

    def test_async_ingest_nogeo_tif(self):  # Test Driver error handling
        url = os.path.join(ROOT, "images/nogeo.tiff")
        status = self.ingest(url, COLLECTION, CATALOG, StatusCode.failed)
        self.assertGreaterEqual(status.message.find("Exception while ingesting"), 0)

    def test_async_ingest_ast(self):  # Driver AST
        url = os.path.join(ROOT, AST)
        self.async_ingest(url, ["data", "metadata", "extent", "airs_item"], archive=False, enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_terrasarx(self):  # Driver TERRASRX
        url = os.path.join(ROOT, TERRASARX)
        self.async_ingest(url, ["data", "metadata", "extent", "airs_item"], archive=False, enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_terrasarx_paz(self):  # Driver TERRASRX
        url = os.path.join(ROOT, TERRASARX_PAZ)
        self.async_ingest(url, ["data", "metadata", "airs_item"], archive=False, enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_tif(self):  # Driver TIF
        url = os.path.join(ROOT, TIF)
        self.async_ingest(url, ["data", "airs_item"], archive=False, enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_jpg2000(self):  # Driver JPEG2000
        url = os.path.join(ROOT, JP2000)
        self.async_ingest(url, ["data", "airs_item"], archive=False, enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_ingest_directory(self):  # Test Folder in cloud ingestion
        self.ingest_directory(ROOT + "/spacewill/", collection=COLLECTION, catalog=CATALOG)

    def test_async_ingest_csk_h5(self):  # Driver CSK h5
        url = os.path.join(ROOT, CSK)
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, Role.data.value, Role.airs_item.value], check_epsg=False, enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_csk_tif(self):  # Driver CSK geotiff
        url = os.path.join(ROOT, CSK2)
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, Role.data.value, Role.airs_item.value], check_epsg=False, check_secondary_id=False, enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_sentinel1_grdh(self):  # Driver Sentinel 1
        url = os.path.join(ROOT, SENTINEL1_GRDH)
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, "iw_grd_vh", "iw_grd_vv", Role.metadata.value, Role.airs_item.value], data_key=None)  # No visual data for cog generation.

    def test_async_ingest_sentinel1_slc(self):  # Driver Sentinel 1
        url = os.path.join(ROOT, SENTINEL1_SLC)
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, *[f"iw{i}_slc_{pol}" for i in range(1, 4) for pol in ["vh", "vv"]], Role.metadata.value, Role.airs_item.value], data_key=None)  # No visual data for cog generation.

    def test_async_ingest_iceye(self):  # Driver ICEYE
        url = os.path.join(ROOT, ICEYE)
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, Role.data.value, Role.metadata.value, Role.airs_item.value], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_radarsat2(self):  # Driver RADARSAT 2
        url = os.path.join(ROOT, RADARSAT2)
        self.async_ingest(url, ["Polarization HH", Role.overview.value, Role.metadata.value, Role.airs_item.value], data_key=Role.polarization.value)   # NO default visual data for cog generation.

    def test_async_ingest_umbra_stac(self):  # Driver Umbra Stac
        url = os.path.join(ROOT, UMBRA_STAC)
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, Role.data.value, Role.metadata.value, Role.airs_item.value], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_capella1(self):  # Driver CAPELLA
        url = os.path.join(ROOT, CAPELLA1)
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, Role.data.value, Role.metadata.value, Role.airs_item.value], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_capella2(self):  # Driver CAPELLA
        url = os.path.join(ROOT, CAPELLA2)
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, Role.data.value, Role.metadata.value, Role.airs_item.value], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_capella3(self):  # Driver CAPELLA
        url = os.path.join(ROOT, CAPELLA3)
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, Role.data.value, Role.metadata.value, Role.airs_item.value], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])


if __name__ == '__main__':
    unittest.main()
