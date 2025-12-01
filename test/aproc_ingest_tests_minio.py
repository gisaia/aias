import os
import unittest
from test.aproc_ingest_tests import (AST, DIMAP, IKONOS, JP2000, RAPID_EYE,
                                     TERRASARX, TIF, WORLDVIEW, IngestTests)
from test.utils import CATALOG, COLLECTION

ROOT = "http://minio:9000/archives/inputs"  # NOSONAR


class Tests(IngestTests):

    def test_async_ingest_dimap_minio(self):  # Driver DIMAP
        url = os.path.join(ROOT, DIMAP)
        item_id = "a75c9fc5a9fee985be7bd967ef713a20df65e7163f660bf6607436845fb48f4b"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])

    def test_async_ingest_ikonos_minio(self):  # Driver GEOEYE
        url = os.path.join(ROOT, IKONOS)
        item_id = "7a315977cc4dfa9809514e994e5f921f13ad0e56df6e6eec172ecf6771174970"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])

    def test_async_ingest_wv_minio(self):  # Driver DIGITALGLOBE
        url = os.path.join(ROOT, WORLDVIEW)
        item_id = "8ae23c4168a65926d6b898e548910635d5f299ddf1e711fa873d1c552a269bb6"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_ast_minio(self):  # Driver AST
        url = os.path.join(ROOT, AST)
        item_id = "9de1896cad5ffaa490f2c38dbca2e19fb6db486350a6408364bccbc4d020f5b5"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_terrasarx_minio(self):  # Driver TERRASRX
        url = os.path.join(ROOT, TERRASARX)
        item_id = "71bc30f00c55474b9266c422a1ffdd00b0f2fa7b086d7674c5e3b0c2f62f55b8"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_rapideye_minio(self):  # Driver RAPIDEYE - No thumbnail nor overview.
        url = os.path.join(ROOT, RAPID_EYE)
        item_id = "c70e4c74cc2f403f13bc1bebd953433203e346fc76d2ed248a2fc1e3bfa80154"
        self.async_ingest(url, item_id, ["data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_tif_minio(self):  # Driver TIF
        url = os.path.join(ROOT, TIF)
        item_id = "dbe4de0187fb0aeaf4fddd76ff7237a160109e0bcc280952d7fc4334b30992d9"
        self.async_ingest(url, item_id, ["data", "airs_item"], archive=False)

    def test_async_ingest_jpg2000_minio(self):  # Driver JPEG2000
        url = os.path.join(ROOT, JP2000)
        item_id = "7d0a49ed64306fa310b723788df1b5d43ef00c5367003007020aff1be436546f"
        self.async_ingest(url, item_id, ["data", "airs_item"], archive=False)

    def test_ingest_directory(self):  # Test Folder ingestion
        self.ingest_directory("/".join([ROOT, "DIMAP/"]), collection=COLLECTION, catalog=CATALOG)


if __name__ == '__main__':
    unittest.main()
