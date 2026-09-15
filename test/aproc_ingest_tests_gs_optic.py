import os
import unittest
from airs.core.models.model import AssetFormat, Role
from aproc.core.models.ogc.enums import StatusCode

from test.aproc_ingest_tests import (AXELGLOBE, GEOSAT_JP2, SPOT6, GEOSAT, IKONOS, PNEOMS, PNEOPAN,
                                     RAPID_EYE, SATELLOGIC, SUPERVIEW, SUPERVIEW3_4, WYVERN, LANDSAT9,
                                     SENTINEL2, SKYSAT, SPOT5,
                                     WORLDVIEW, IngestTests)
from test.utils import CATALOG, COLLECTION, SENTINEL2_BANDS

ROOT = "gs://gisaia-public/test-aias"


class Tests(IngestTests):

    def test_async_ingest_spot6(self):  # Driver DIMAP
        url = os.path.join(ROOT, SPOT6)
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], check_epsg=False, enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_dimap_driver_include(self):  # Driver DIMAP
        url = os.path.join(ROOT, SPOT6)
        self.ingest(url, COLLECTION, CATALOG, include_drivers=["dimap"], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_dimap_driver_include_fail(self):  # Driver DIMAP
        url = os.path.join(ROOT, SPOT6)
        self.ingest(url, COLLECTION, CATALOG, include_drivers=["spot5"], expected=StatusCode.failed)

    def test_async_ingest_dimap_driver_exclude(self):  # Driver DIMAP
        url = os.path.join(ROOT, SPOT6)
        self.ingest(url, COLLECTION, CATALOG, exclude_drivers=["spot5"])

    def test_async_ingest_dimap_driver_exclude_fail(self):  # Driver DIMAP
        url = os.path.join(ROOT, SPOT6)
        self.ingest(url, COLLECTION, CATALOG, exclude_drivers=["dimap"], expected=StatusCode.failed)

    def test_async_ingest_ikonos(self):  # Driver GEOEYE
        url = os.path.join(ROOT, IKONOS)
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_wv(self):  # Driver DIGITALGLOBE
        url = os.path.join(ROOT, WORLDVIEW)
        self.async_ingest(url, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False, enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_rapideye(self):  # Driver RAPIDEYE
        url = os.path.join(ROOT, RAPID_EYE)
        self.async_ingest(url, ["data", "metadata", "extent", "airs_item", "thumbnail", "overview"], archive=False, enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_sentinel2(self):  # Driver Sentinel 2
        url = os.path.join(ROOT, SENTINEL2)
        self.async_ingest(url, [Role.data.value, Role.metadata.value, Role.airs_item.value, *SENTINEL2_BANDS], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value, AssetFormat.all_bands_cog.value])

    def test_async_ingest_skysat(self):  # Driver SKYSAT
        url = os.path.join(ROOT, SKYSAT)
        self.async_ingest(url, [Role.thumbnail.value, Role.data.value, "UDM2", "visual", Role.metadata.value, Role.airs_item.value], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_spot5(self):  # Driver SPOT5
        url = os.path.join(ROOT, SPOT5)
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, Role.data.value, Role.metadata.value, Role.airs_item.value], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_geosat(self):  # Driver Geosat
        url = os.path.join(ROOT, GEOSAT)
        self.async_ingest(url, [Role.thumbnail.value, Role.data.value, Role.metadata.value, Role.airs_item.value], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_geosat_jp2(self):  # Driver Geosat
        url = os.path.join(ROOT, GEOSAT_JP2)
        self.async_ingest(url, [Role.thumbnail.value, Role.data.value, Role.metadata.value, Role.airs_item.value], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_wyvern(self):  # Driver Wyvern
        url = os.path.join(ROOT, WYVERN)
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, Role.data.value, Role.metadata.value, Role.airs_item.value], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_landsat9(self):  # Driver Landsat for landsat9 product
        url = os.path.join(ROOT, LANDSAT9)
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, Role.pan.value, Role.metadata.value, Role.airs_item.value], data_key=Role.pan.value, enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value, AssetFormat.all_bands_cog.value])

    def test_async_ingest_satellogic(self):  # Driver SATELLOGIC
        url = os.path.join(ROOT, SATELLOGIC)
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, Role.data.value, Role.visual.value, Role.cloud.value, Role.metadata.value, Role.airs_item.value], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_pneo_ms(self):  # Driver DIMAP for PNEO MS
        url = os.path.join(ROOT, PNEOMS)
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, Role.data.value, Role.metadata.value, Role.airs_item.value], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_pneo_pan(self):  # Driver DIMAP for PNEO PAN
        url = os.path.join(ROOT, PNEOPAN)
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, Role.data.value, Role.metadata.value, Role.airs_item.value], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_superview(self):  # Driver SUPERVIEW
        url = os.path.join(ROOT, SUPERVIEW)
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, Role.data.value, Role.metadata.value, Role.airs_item.value], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_superview_mux(self):  # Driver SUPERVIEW
        url = os.path.join(ROOT, SUPERVIEW + "_MUX/")
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, Role.data.value, Role.metadata.value, Role.airs_item.value, Role.archive.value, Role.multispectral.value, Role.overview.value + "-mux", Role.rpc.value + "-mux", Role.metadata.value + "-mux"], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_superview_mux_pan(self):  # Driver SUPERVIEW
        url = os.path.join(ROOT, SUPERVIEW + "_MUX_PAN")
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, Role.data.value, Role.metadata.value, Role.airs_item.value, Role.archive.value, Role.multispectral.value, Role.pan.value, Role.overview.value + "-mux", Role.rpc.value + "-mux", Role.metadata.value + "-mux", Role.overview.value + "-pan", Role.rpc.value + "-pan", Role.metadata.value + "-pan"], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_superview_pan(self):  # Driver SUPERVIEW
        url = os.path.join(ROOT, SUPERVIEW + "_PAN")
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, Role.data.value, Role.metadata.value, Role.airs_item.value, Role.archive.value, Role.pan.value, Role.overview.value + "-pan", Role.rpc.value + "-pan", Role.metadata.value + "-pan"], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_superview_psh(self):  # Driver SUPERVIEW
        url = os.path.join(ROOT, SUPERVIEW + "_PSH")
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, Role.data.value, Role.metadata.value, Role.airs_item.value, Role.archive.value, Role.pan_sharpened.value, Role.overview.value + "-psh", Role.rpc.value + "-psh", Role.metadata.value + "-psh"], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_superview_product_info(self):  # Driver SUPERVIEW
        url = os.path.join(ROOT, SUPERVIEW + "_MUX_ProductInfo")
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, Role.data.value, Role.metadata.value, Role.airs_item.value, Role.archive.value, Role.multispectral.value, Role.overview.value + "-mux", Role.rpc.value + "-mux", Role.metadata.value + "-mux"], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_superview3_4_mux(self):  # Driver SUPERVIEW
        url = os.path.join(ROOT, SUPERVIEW3_4 + "_MUX/")
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, Role.data.value, Role.metadata.value, Role.airs_item.value, Role.archive.value, Role.multispectral.value, Role.overview.value + "-mux", Role.rpc.value + "-mux", Role.metadata.value + "-mux"], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_superview3_4_mux_pan(self):  # Driver SUPERVIEW
        url = os.path.join(ROOT, SUPERVIEW3_4 + "_MUX_PAN")
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, Role.data.value, Role.metadata.value, Role.airs_item.value, Role.archive.value, Role.multispectral.value, Role.pan.value, Role.overview.value + "-mux", Role.rpc.value + "-mux", Role.metadata.value + "-mux", Role.overview.value + "-pan", Role.rpc.value + "-pan", Role.metadata.value + "-pan"], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_superview3_4_pan(self):  # Driver SUPERVIEW
        url = os.path.join(ROOT, SUPERVIEW3_4 + "_PAN")
        self.async_ingest(url, [Role.thumbnail.value, Role.overview.value, Role.data.value, Role.metadata.value, Role.airs_item.value, Role.archive.value, Role.pan.value, Role.overview.value + "-pan", Role.rpc.value + "-pan", Role.metadata.value + "-pan"], enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value])

    def test_async_ingest_axelglobe(self):  # Driver SUPERVIEW
        url = os.path.join(ROOT, AXELGLOBE)
        self.async_ingest(url, ["data_00000000-0000-4000-8000-000000000000", "data_00000000-0000-4000-8000-000000000011", Role.airs_item.value, Role.archive.value, Role.overview.value, Role.metadata.value, Role.thumbnail.value], data_key=None, check_secondary_id=False)  # No visual data for cog generation.


if __name__ == '__main__':
    unittest.main()
