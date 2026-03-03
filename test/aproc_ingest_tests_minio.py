import os
import unittest
from test.aproc_ingest_tests import (AST, DIMAP, IKONOS, JP2000, RAPID_EYE,
                                     SATELLOGIC, TERRASARX, TIF, WORLDVIEW,
                                     IngestTests)
from test.utils import CATALOG, COLLECTION

ROOT = "http://minio:9000/archives/inputs"  # NOSONAR


class Tests(IngestTests):

    def test_async_ingest_tif_minio(self):  # Driver TIF
        url = os.path.join(ROOT, TIF)
        self.async_ingest(url, ["data", "airs_item"], archive=False)

    def test_ingest_directory(self):  # Test Folder ingestion
        self.ingest_directory("/".join([ROOT, "images/"]), collection=COLLECTION, catalog=CATALOG)

    def test_async_ingest_satellogic_minio(self):  # Driver SATELLOGIC
        url = os.path.join(ROOT, SATELLOGIC)
        self.async_ingest(url, ["thumbnail", "overview", "data", "visual", "cloud", "metadata", "airs_item"])


if __name__ == '__main__':
    unittest.main()
