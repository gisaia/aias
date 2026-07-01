import os
import unittest
from airs.core.models.model import Role
from aproc.core.models.ogc.enums import StatusCode

from test.aproc_ingest_tests import (AST, CAPELLA1, CAPELLA2, CAPELLA3, CSK, CSK2, SPOT6, GEOSAT, ICEYE, IKONOS, JP2000, PNEOMS, PNEOPAN,
                                     RADARSAT2, RAPID_EYE, SATELLOGIC, SENTINEL1_GRDH, SUPERVIEW, SUPERVIEW3_4, WYVERN, LANDSAT9,
                                     SENTINEL1_SLC, SENTINEL2, SKYSAT, SPOT5,
                                     TERRASARX, TERRASARX_PAZ, TIF, WORLDVIEW, UMBRA_STAC, IngestTests)
from test.utils import CATALOG, COLLECTION, SENTINEL2_BANDS

ROOT = "gs://gisaia-public/test-aias"


class Tests(IngestTests):

    def test_async_ingest_invalid_tif_cloud(self):  # Test Driver error handling
        url = os.path.join(ROOT, "images/empty.tiff")
        status = self.ingest(url, COLLECTION, CATALOG, StatusCode.failed)
        self.assertGreaterEqual(status.message.find("Exception while ingesting"), 0)

    def test_async_ingest_nogeo_tif_cloud(self):  # Test Driver error handling
        url = os.path.join(ROOT, "images/nogeo.tiff")
        status = self.ingest(url, COLLECTION, CATALOG, StatusCode.failed)
        self.assertGreaterEqual(status.message.find("Exception while ingesting"), 0)

    def test_async_ingest_spot6_cloud(self):  # Driver DIMAP
        url = os.path.join(ROOT, SPOT6)
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], check_epsg=False)

    def test_async_ingest_pneoms_cloud(self):  # Driver DIMAP
        url = os.path.join(ROOT, PNEOMS)
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])

    def test_async_ingest_pneopan_cloud(self):  # Driver DIMAP
        url = os.path.join(ROOT, PNEOPAN)
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])

    def test_async_ingest_dimap_driver_include_cloud(self):  # Driver DIMAP
        url = os.path.join(ROOT, SPOT6)
        self.ingest(url, COLLECTION, CATALOG, include_drivers=["dimap"])

    def test_async_ingest_dimap_driver_include_fail_cloud(self):  # Driver DIMAP
        url = os.path.join(ROOT, SPOT6)
        self.ingest(url, COLLECTION, CATALOG, include_drivers=["spot5"], expected=StatusCode.failed)

    def test_async_ingest_dimap_driver_exclude_cloud(self):  # Driver DIMAP
        url = os.path.join(ROOT, SPOT6)
        self.ingest(url, COLLECTION, CATALOG, exclude_drivers=["spot5"])

    def test_async_ingest_dimap_driver_exclude_fail_cloud(self):  # Driver DIMAP
        url = os.path.join(ROOT, SPOT6)
        self.ingest(url, COLLECTION, CATALOG, exclude_drivers=["dimap"], expected=StatusCode.failed)

    def test_async_ingest_ikonos_cloud(self):  # Driver GEOEYE
        url = os.path.join(ROOT, IKONOS)
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])

    def test_async_ingest_wv_cloud(self):  # Driver DIGITALGLOBE
        url = os.path.join(ROOT, WORLDVIEW)
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_ast_cloud(self):  # Driver AST
        url = os.path.join(ROOT, AST)
        self.async_ingest(url, ["data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_terrasarx_cloud(self):  # Driver TERRASRX
        url = os.path.join(ROOT, TERRASARX)
        self.async_ingest(url, ["data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_terrasarx_paz_cloud(self):  # Driver TERRASRX
        url = os.path.join(ROOT, TERRASARX_PAZ)
        self.async_ingest(url, ["data", "metadata", "airs_item"], archive=False)

    def test_async_ingest_rapideye_cloud(self):  # Driver RAPIDEYE - No thumbnail nor overview.
        url = os.path.join(ROOT, RAPID_EYE)
        self.async_ingest(url, ["data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_tif_cloud(self):  # Driver TIF
        url = os.path.join(ROOT, TIF)
        self.async_ingest(url, ["data", "airs_item"], archive=False)

    def test_async_ingest_jpg2000_cloud(self):  # Driver JPEG2000
        url = os.path.join(ROOT, JP2000)
        self.async_ingest(url, ["data", "airs_item"], archive=False)

    def test_ingest_directory_cloud(self):  # Test Folder in cloud ingestion
        self.ingest_directory(ROOT + "/", collection=COLLECTION, catalog=CATALOG)

    def test_async_ingest_sentinel2(self):  # Driver Sentinel 2
        url = os.path.join(ROOT, SENTINEL2)
        self.async_ingest(url, ["metadata", "data", "airs_item", *SENTINEL2_BANDS])

    def test_async_ingest_csk_h5(self):  # Driver CSK h5
        url = os.path.join(ROOT, CSK)
        self.async_ingest(url, ["thumbnail", "overview", "data", "airs_item"], check_epsg=False)

    def test_async_ingest_csk_tif(self):  # Driver CSK h5
        url = os.path.join(ROOT, CSK2)
        self.async_ingest(url, ["thumbnail", "overview", "data", "airs_item"], check_epsg=False, check_secondary_id=False)

    def test_async_ingest_sentinel1_grdh(self):  # Driver Sentinel 1
        url = os.path.join(ROOT, SENTINEL1_GRDH)
        self.async_ingest(url, ["thumbnail", "overview", "iw_grd_vh", "iw_grd_vv", "metadata", "airs_item"], data_key=None)

    def test_async_ingest_sentinel1_slc(self):  # Driver Sentinel 1
        url = os.path.join(ROOT, SENTINEL1_SLC)
        self.async_ingest(url, ["thumbnail", "overview", *[f"iw{i}_slc_{pol}" for i in range(1, 4) for pol in ["vh", "vv"]], "metadata", "airs_item"], data_key=None)

    def test_async_ingest_iceye(self):  # Driver ICEYE
        url = os.path.join(ROOT, ICEYE)
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "airs_item"])

    def test_async_ingest_radarsat2(self):  # Driver RADARSAT 2
        url = os.path.join(ROOT, RADARSAT2)
        self.async_ingest(url, ["Polarization HH", "metadata", "airs_item"], data_key="Polarization HH")

    def test_async_ingest_skysat(self):  # Driver SKYSAT
        url = os.path.join(ROOT, SKYSAT)
        self.async_ingest(url, ["thumbnail", "data", "UDM2", "visual", "metadata", "airs_item"])

    def test_async_ingest_spot5(self):  # Driver SPOT5
        url = os.path.join(ROOT, SPOT5)
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "airs_item"])

    def test_async_ingest_geosat_cloud(self):  # Driver Geosat
        url = os.path.join(ROOT, GEOSAT)
        self.async_ingest(url, ["thumbnail", "data", "metadata", "airs_item"])

    def test_async_ingest_wyvern(self):  # Driver Wyvern
        url = os.path.join(ROOT, WYVERN)
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "airs_item"])

    def test_async_ingest_landsat9(self):  # Driver Landsat for landsat9 product
        url = os.path.join(ROOT, LANDSAT9)
        self.async_ingest(url, ["thumbnail", "overview", "pan", "metadata", "airs_item"], data_key="pan")

    def test_async_ingest_umbra_stac(self):  # Driver Umbra Stac
        url = os.path.join(ROOT, UMBRA_STAC)
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "airs_item"])

    def test_async_ingest_satellogic(self):  # Driver SATELLOGIC
        url = os.path.join(ROOT, SATELLOGIC)
        self.async_ingest(url, ["thumbnail", "overview", "data", "visual", "cloud", "metadata", "airs_item"])

    def test_async_ingest_pneo_ms(self):  # Driver DIMAP for PNEO MS
        url = os.path.join(ROOT, PNEOMS)
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "airs_item"])

    def test_async_ingest_pneo_pan(self):  # Driver DIMAP for PNEO PAN
        url = os.path.join(ROOT, PNEOPAN)
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "airs_item"])

    def test_async_ingest_capella1(self):  # Driver CAPELLA
        url = os.path.join(ROOT, CAPELLA1)
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "airs_item"])

    def test_async_ingest_capella2(self):  # Driver CAPELLA
        url = os.path.join(ROOT, CAPELLA2)
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "airs_item"])

    def test_async_ingest_capella3(self):  # Driver CAPELLA
        url = os.path.join(ROOT, CAPELLA3)
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "airs_item"])

    def test_async_ingest_superview(self):  # Driver SUPERVIEW
        url = os.path.join(ROOT, SUPERVIEW)
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "airs_item"])

    def test_async_ingest_superview_mux(self):  # Driver SUPERVIEW
        url = os.path.join(ROOT, SUPERVIEW + "_MUX/")
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "airs_item", Role.archive.value, Role.multispectral.value, Role.overview.value + "-mux", Role.rpc.value + "-mux", Role.metadata.value + "-mux"])

    def test_async_ingest_superview_mux_pan(self):  # Driver SUPERVIEW
        url = os.path.join(ROOT, SUPERVIEW + "_MUX_PAN")
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "airs_item", Role.archive.value, Role.multispectral.value, Role.pan.value, Role.overview.value + "-mux", Role.rpc.value + "-mux", Role.metadata.value + "-mux", Role.overview.value + "-pan", Role.rpc.value + "-pan", Role.metadata.value + "-pan"])

    def test_async_ingest_superview_pan(self):  # Driver SUPERVIEW
        url = os.path.join(ROOT, SUPERVIEW + "_PAN")
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "airs_item", Role.archive.value, Role.pan.value, Role.overview.value + "-pan", Role.rpc.value + "-pan", Role.metadata.value + "-pan"])

    def test_async_ingest_superview_psh(self):  # Driver SUPERVIEW
        url = os.path.join(ROOT, SUPERVIEW + "_PSH")
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "airs_item", Role.archive.value, Role.pan_sharpened.value, Role.overview.value + "-psh", Role.rpc.value + "-psh", Role.metadata.value + "-psh"])

    def test_async_ingest_superview_product_info(self):  # Driver SUPERVIEW
        url = os.path.join(ROOT, SUPERVIEW + "_MUX_ProductInfo")
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "airs_item", Role.archive.value, Role.multispectral.value, Role.overview.value + "-mux", Role.rpc.value + "-mux", Role.metadata.value + "-mux"])

    def test_async_ingest_superview3_4_mux(self):  # Driver SUPERVIEW
        url = os.path.join(ROOT, SUPERVIEW3_4 + "_MUX/")
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "airs_item", Role.archive.value, Role.multispectral.value, Role.overview.value + "-mux", Role.rpc.value + "-mux", Role.metadata.value + "-mux"])

    def test_async_ingest_superview3_4_mux_pan(self):  # Driver SUPERVIEW
        url = os.path.join(ROOT, SUPERVIEW3_4 + "_MUX_PAN")
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "airs_item", Role.archive.value, Role.multispectral.value, Role.pan.value, Role.overview.value + "-mux", Role.rpc.value + "-mux", Role.metadata.value + "-mux", Role.overview.value + "-pan", Role.rpc.value + "-pan", Role.metadata.value + "-pan"])

    def test_async_ingest_superview3_4_pan(self):  # Driver SUPERVIEW
        url = os.path.join(ROOT, SUPERVIEW3_4 + "_PAN")
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "airs_item", Role.archive.value, Role.pan.value, Role.overview.value + "-pan", Role.rpc.value + "-pan", Role.metadata.value + "-pan"])

if __name__ == '__main__':
    unittest.main()
