import json
import os
import shutil
import unittest
from test.utils import APROC_ENDPOINT, CATALOG, COLLECTION

import requests
from aproc.core.models.ogc.job import StatusCode, StatusInfo
from test.aproc_ingest_tests import (AST, DIMAP, IKONOS, JP2000, RAPID_EYE,
                                     SATELLOGIC, TERRASARX, TIF, WORLDVIEW,
                                     IngestTests)

ROOT = "/inputs"


class Tests(IngestTests):

    def setUp(self) -> None:
        shutil.rmtree(os.path.join("test", "inputs", "many"), ignore_errors=True)

    def test_async_ingest_tif(self):  # Driver TIF
        url = os.path.join(ROOT, TIF)
        self.async_ingest(url, ["data", "airs_item"], archive=False)

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
        url = os.path.join(ROOT, TIF)
        status: StatusInfo = self.async_ingest(url, ["data", "airs_item"], archive=False)
        status2: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        self.assertEqual(status.jobID, status2.jobID)
        self.assertEqual(status2.processID, "ingest")

    def test_get_jobs_by_resource_id(self):
        url = os.path.join(ROOT, TIF)
        status: StatusInfo = self.async_ingest(url, ["data", "airs_item"], archive=False)
        resource_status: list = json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs/resources", status.resourceID])).content)
        self.assertGreaterEqual(len(resource_status), 1)
        self.assertEqual(resource_status[0]["resourceID"], status.resourceID)

    def test_async_ingest_satellogic(self):  # Driver SATELLOGIC
        url = os.path.join(ROOT, SATELLOGIC)
        self.async_ingest(url, ["thumbnail", "overview", "data", "visual", "cloud", "metadata", "airs_item"])


if __name__ == '__main__':
    unittest.main()
