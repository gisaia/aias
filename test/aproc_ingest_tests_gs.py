import os
import unittest
from test.aproc_ingest_tests import (AST, DIMAP, IKONOS, JP2000, RAPID_EYE,
                                     SENTINEL2, TERRASARX, TIF, WORLDVIEW,
                                     IngestTests)
from test.utils import CATALOG, COLLECTION, SENTINEL2_BANDS

ROOT = "gs://gisaia-public"


class Tests(IngestTests):

    def test_async_ingest_dimap_cloud(self):  # Driver DIMAP
        url = os.path.join(ROOT, "test-aias", DIMAP)
        item_id = "9c74339d7d73e441e61d1b61b660d92713a163f3c212bf7dca261e4bc1e03601"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])

    def test_async_ingest_ikonos_cloud(self):  # Driver GEOEYE
        url = os.path.join(ROOT, "test-aias", IKONOS)
        item_id = "26fc0091ed9d5b0f53769ecaf2a0cef26b0007e477be9b4c94f198a26b2e00d1"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])

    def test_async_ingest_wv_cloud(self):  # Driver DIGITALGLOBE
        url = os.path.join(ROOT, "test-aias", WORLDVIEW)
        item_id = "03f59a67eb3309e0a05135a8c047c364b469cae7691fa98f22026d18f5bf24d7"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_ast_cloud(self):  # Driver AST
        url = os.path.join(ROOT, "test-aias", AST)
        item_id = "17e377bf0c44c3a7cc8ec70e1ff9c73852454bb1a86e64f3a61545138b89b08b"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_terrasarx_cloud(self):  # Driver TERRASRX
        url = os.path.join(ROOT, "test-aias", TERRASARX)
        item_id = "650cbc54a5554720fa3290473f0db93888ecae701c602539018927292277ab46"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_rapideye_cloud(self):  # Driver RAPIDEYE - No thumbnail nor overview.
        url = os.path.join(ROOT, "test-aias", RAPID_EYE)
        item_id = "a4afb6d08ca248639d359ad529b84bea9afa58db4f68aab47995c46f81c3318c"
        self.async_ingest(url, item_id, ["data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_tif_cloud(self):  # Driver TIF
        url = os.path.join(ROOT, "test-aias", TIF)
        item_id = "03bc217a7894c34abc42d292a270a3f194096507d2a86a3365092631769ff525"
        self.async_ingest(url, item_id, ["data", "airs_item"], archive=False)

    def test_async_ingest_jpg2000_cloud(self):  # Driver JPEG2000
        url = os.path.join(ROOT, "test-aias", JP2000)
        item_id = "95d6803989b40dd72fc642e51477cd9ed0cb4432218711246aaa447c1a3bc046"
        self.async_ingest(url, item_id, ["data", "airs_item"], archive=False)

    def test_ingest_directory_cloud(self):  # Test Folder in cloud ingestion
        self.ingest_directory(os.path.join(ROOT, "test-aias/"), collection=COLLECTION, catalog=CATALOG)

    def test_async_ingest_sentinel2(self):  # Driver Sentinel 2
        url = os.path.join(ROOT, "test-aias", SENTINEL2)
        item_id = "8377d47a086d935e0573db7affa2a0bbd4fba50f458fb9f0fbeae30b6043c3e5"
        self.async_ingest(url, item_id, ["overview", "metadata", "data", "airs_item", *SENTINEL2_BANDS], archive=False)


if __name__ == '__main__':
    unittest.main()
