import json
import os
import random
import shutil
import unittest
from test.utils import APROC_ENDPOINT, CATALOG, COLLECTION

import requests
from aproc.core.models.ogc.job import StatusCode, StatusInfo
from test.aproc_ingest_tests import (AST, DIMAP, IKONOS, JP2000, RAPID_EYE,
                                     TERRASARX, TIF, WORLDVIEW, SENTINEL2, IngestTests)
from test.utils import SENTINEL2_BANDS

ROOT = "/inputs"


class Tests(IngestTests):

    def setUp(self) -> None:
        shutil.rmtree(os.path.join("test", "inputs", "many"), ignore_errors=True)

    def test_async_ingest_dimap(self):  # Driver DIMAP
        url = os.path.join(ROOT, DIMAP)
        item_id = "148ddaaa431bdd2ff06b823df1e3725d462f668bd95188603bfff443ff055c71"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])

    def test_async_ingest_dimap_driver_include(self):  # Driver DIMAP
        url = os.path.join(ROOT, DIMAP)
        self.ingest(url, COLLECTION, CATALOG, include_drivers=["dimap"])

    def test_async_ingest_dimap_driver_include_fail(self):  # Driver DIMAP
        url = os.path.join(ROOT, DIMAP)
        self.ingest(url, COLLECTION, CATALOG, include_drivers=["spot5"], expected=StatusCode.failed)

    def test_async_ingest_dimap_driver_exclude(self):  # Driver DIMAP
        url = os.path.join(ROOT, DIMAP)
        self.ingest(url, COLLECTION, CATALOG, exclude_drivers=["spot5"])

    def test_async_ingest_dimap_driver_exclude_fail(self):  # Driver DIMAP
        url = os.path.join(ROOT, DIMAP)
        self.ingest(url, COLLECTION, CATALOG, exclude_drivers=["dimap"], expected=StatusCode.failed)

    def test_async_ingest_ikonos(self):  # Driver GEOEYE
        url = os.path.join(ROOT, IKONOS)
        item_id = "0e73667ac0bd10b5f18bcb5ee40518db973b2946fe8b40d2b4cb988724ac9507"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])

    def test_async_ingest_wv(self):  # Driver DIGITALGLOBE
        url = os.path.join(ROOT, WORLDVIEW)
        item_id = "22785c0db31d772b6ba2f685ab7b9fbfec8931b37394b53a0a7d7e519ec9aa3a"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_ast(self):  # Driver AST
        url = os.path.join(ROOT, AST)
        item_id = "af129ada4336f27a532950d43eaf4fa3802f82ea87b4cb339199e2562ef10f2c"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_terrasarx(self):  # Driver TERRASRX
        url = os.path.join(ROOT, TERRASARX)
        item_id = "53b302d1f1877f7509fbdd619b2071b024aa54604fdd1d85718059dfb88aac2c"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_rapideye(self):  # Driver RAPIDEYE - No thumbnail nor overview.
        url = os.path.join(ROOT, RAPID_EYE)
        item_id = "bb2ddbcc86e90a95afa61b7cd7dccc7eb6335f6a40052e49213cb404d0baf17a"
        self.async_ingest(url, item_id, ["data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_tif(self):  # Driver TIF
        url = os.path.join(ROOT, TIF)
        item_id = "36f978ad9fe1e9b4ea8064c893140012a967e1a7a5d1ac65a589a16566f03ccd"
        self.async_ingest(url, item_id, ["data", "airs_item"], archive=False)

    def test_async_ingest_jpg2000(self):  # Driver JPEG2000
        url = os.path.join(ROOT, JP2000)
        item_id = "e2614a12233e3f859a4083b54d2b7e4e4615055013af13c73b6c7e427548785c"
        self.async_ingest(url, item_id, ["data", "airs_item"], archive=False)

    def test_async_ingest_invalid_tif(self):  # Test Driver error handling
        url = "/inputs/empty.tiff"
        status = self.ingest(url, COLLECTION, CATALOG, StatusCode.failed)
        self.assertGreaterEqual(status.message.index("Exception while ingesting"), 0)

    def test_async_ingest_nogeo_tif(self):  # Test Driver error handling
        url = "/inputs/nogeo.tiff"
        status = self.ingest(url, COLLECTION, CATALOG, StatusCode.failed)
        self.assertGreaterEqual(status.message.index("Exception while ingesting"), 0)

    def test_ingest_directory(self):  # Test Folder ingestion
        self.ingest_directory(os.path.join(ROOT, DIMAP), collection=COLLECTION, catalog=CATALOG)

    def test_async_ingest_many(self):  # Many COGs
        local_dir = os.path.join("test", "inputs", "many")
        local_source = os.path.join("test", "inputs", TIF)
        os.makedirs(local_dir, exist_ok=True)
        NB_ITERATIONS = 10
        for i in range(0, NB_ITERATIONS):
            url = os.path.join(ROOT, "many", str(i) + ".tiff")
            local_url = os.path.join(local_dir, str(i) + ".tiff")
            shutil.copyfile(local_source, local_url)
            shutil.copyfile(local_source + ".aux.xml", local_url + ".aux.xml")
        statuses = []
        for i in range(0, NB_ITERATIONS):
            url = os.path.join(ROOT, "many", str(i) + ".tiff")
            r = self.ingest_no_wait(url, COLLECTION, CATALOG, StatusCode.failed)
            status: StatusInfo = StatusInfo(**json.loads(r.content))
            statuses.append(status)

        for status in statuses:
            status = self.wait_for(status)
            self.assertEqual(status.status, StatusCode.successful, status.model_dump_json())

    def test_job_by_id(self):
        url = os.path.join(ROOT, DIMAP)
        item_id = "148ddaaa431bdd2ff06b823df1e3725d462f668bd95188603bfff443ff055c71"
        status: StatusInfo = self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])
        status2: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        self.assertEqual(status.jobID, status2.jobID)
        self.assertEqual(status2.processID, "ingest")

    def test_get_jobs_by_resource_id(self):
        url = os.path.join(ROOT, DIMAP)
        item_id = "148ddaaa431bdd2ff06b823df1e3725d462f668bd95188603bfff443ff055c71"
        status: StatusInfo = self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])
        resource_status: list = json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs/resources", status.resourceID])).content)
        self.assertGreaterEqual(len(resource_status), 1)
        self.assertEqual(resource_status[0]["resourceID"], status.resourceID)


if __name__ == '__main__':
    unittest.main()
