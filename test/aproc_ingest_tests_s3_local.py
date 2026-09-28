import os
import unittest

from test.aproc_ingest_tests import (TIF, IngestTests)
from test.utils import CATALOG, COLLECTION

ROOT = "http://seaweedfs:8333/archives/inputs"  # NOSONAR


class Tests(IngestTests):

    def test_async_ingest_tif_s3_local(self):  # Driver TIF
        url = os.path.join(ROOT, TIF)
        self.async_ingest(url, ["data", "airs_item"], archive=False)

    def test_ingest_directory(self):  # Test Folder ingestion
        self.ingest_directory("/".join([ROOT, "images/"]), collection=COLLECTION, catalog=CATALOG)


if __name__ == '__main__':
    unittest.main()
