import os
import unittest
from test.aproc_ingest_tests import (AST, CSK, DIMAP, ICEYE, IKONOS, JP2000,
                                     RADARSAT2, RAPID_EYE, SENTINEL1_GRDH,
                                     SENTINEL1_SLC, SENTINEL2, SKYSAT, SPOT5,
                                     TERRASARX, TIF, WORLDVIEW, IngestTests)
from test.utils import CATALOG, COLLECTION, SENTINEL2_BANDS

ROOT = "gs://gisaia-public/test-aias"


class Tests(IngestTests):

    def test_async_ingest_dimap_cloud(self):  # Driver DIMAP
        url = os.path.join(ROOT, DIMAP)
        item_id = "9c74339d7d73e441e61d1b61b660d92713a163f3c212bf7dca261e4bc1e03601"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])

    def test_async_ingest_ikonos_cloud(self):  # Driver GEOEYE
        url = os.path.join(ROOT, IKONOS)
        item_id = "26fc0091ed9d5b0f53769ecaf2a0cef26b0007e477be9b4c94f198a26b2e00d1"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])

    def test_async_ingest_wv_cloud(self):  # Driver DIGITALGLOBE
        url = os.path.join(ROOT, WORLDVIEW)
        item_id = "03f59a67eb3309e0a05135a8c047c364b469cae7691fa98f22026d18f5bf24d7"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_ast_cloud(self):  # Driver AST
        url = os.path.join(ROOT, AST)
        item_id = "17e377bf0c44c3a7cc8ec70e1ff9c73852454bb1a86e64f3a61545138b89b08b"
        self.async_ingest(url, item_id, ["data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_terrasarx_cloud(self):  # Driver TERRASRX
        url = os.path.join(ROOT, TERRASARX)
        item_id = "650cbc54a5554720fa3290473f0db93888ecae701c602539018927292277ab46"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_rapideye_cloud(self):  # Driver RAPIDEYE - No thumbnail nor overview.
        url = os.path.join(ROOT, RAPID_EYE)
        item_id = "a4afb6d08ca248639d359ad529b84bea9afa58db4f68aab47995c46f81c3318c"
        self.async_ingest(url, item_id, ["data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_tif_cloud(self):  # Driver TIF
        url = os.path.join(ROOT, TIF)
        item_id = "03bc217a7894c34abc42d292a270a3f194096507d2a86a3365092631769ff525"
        self.async_ingest(url, item_id, ["data", "airs_item"], archive=False)

    def test_async_ingest_jpg2000_cloud(self):  # Driver JPEG2000
        url = os.path.join(ROOT, JP2000)
        item_id = "95d6803989b40dd72fc642e51477cd9ed0cb4432218711246aaa447c1a3bc046"
        self.async_ingest(url, item_id, ["data", "airs_item"], archive=False)

    def test_ingest_directory_cloud(self):  # Test Folder in cloud ingestion
        self.ingest_directory(ROOT + "/", collection=COLLECTION, catalog=CATALOG)

    def test_async_ingest_sentinel2(self):  # Driver Sentinel 2
        url = os.path.join(ROOT, SENTINEL2)
        item_id = "eee16f1452c0ff3897d2a3b6595348bd151993aedc95104246accec3a00f05d1"
        self.async_ingest(url, item_id, ["overview", "metadata", "data", "airs_item", *SENTINEL2_BANDS])

    def test_async_ingest_csk(self):  # Driver CSK h5
        url = os.path.join(ROOT, CSK)
        item_id = "5b1dbff1eaa5117872abc8f2612fb672b194a61d21c532191a13a7d5f062b12f"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "airs_item"], check_epsg=False)

    def test_async_ingest_sentinel1_grdh(self):  # Driver Sentinel 1
        url = os.path.join(ROOT, SENTINEL1_GRDH)
        item_id = "36c5e88bffde5ab72c50e94f43b40a6f938a6c3bf92f7c889d95879756da76a8"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "iw grd vh", "iw grd vv", "metadata", "airs_item"], data_key=None)

    def test_async_ingest_sentinel1_slc(self):  # Driver Sentinel 1
        url = os.path.join(ROOT, SENTINEL1_SLC)
        item_id = "cee7d7833c946cc37062698a382a863ac1c3272d1e8ca115f846b55871fd7834"
        self.async_ingest(url, item_id, ["thumbnail", "overview", *[f"iw{i} slc {pol}" for i in range(1, 4) for pol in ["vh", "vv"]], "metadata", "airs_item"], data_key=None)

    def test_async_ingest_iceye(self):  # Driver ICEYE
        url = os.path.join(ROOT, ICEYE)
        item_id = "7d999733dbcf3fe6afdf7fca6da1dcd87184bbad10ddaa6c5126dd34247f5501"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "airs_item"])

    def test_async_ingest_radarsat2(self):  # Driver RADARSAT 2
        url = os.path.join(ROOT, RADARSAT2)
        item_id = "81fde97a25a2611b3806f314a73bdca6c59d655a74c0a58d6470bbe50247feab"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "Polarization HH", "metadata", "airs_item"], data_key="Polarization HH")

    def test_async_ingest_skysat(self):  # Driver SKYSAT
        url = os.path.join(ROOT, SKYSAT)
        item_id = "66fc9856b9120c2d04c4ea4886368726bc0577bfb6bd79107d877005a9a46024"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "UDM2", "visual", "metadata", "airs_item"])

    def test_async_ingest_spot5(self):  # Driver SPOT5
        url = os.path.join(ROOT, SPOT5)
        item_id = "e3753718ee48324000b50a457444d0efd0881a8589da5bce4b9f3bc8d7648873"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "airs_item"])


if __name__ == '__main__':
    unittest.main()
