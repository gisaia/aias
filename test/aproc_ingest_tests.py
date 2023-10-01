import unittest
from time import sleep
import requests
import json
from aproc.core.models.ogc.process import ProcessList, ProcessDescription
from extensions.aproc.proc.ingest.ingest_process import AprocProcess

from utils import AIRS_URL, APROC_ENDPOINT, setUpTest

from aproc.core.models.ogc.job import StatusCode, StatusInfo
from aproc.core.processes.processes import Processes
from extensions.aproc.proc.ingest.ingest_process import InputIngestProcess
from aproc.core.models.ogc import (Conforms, ExceptionType, Execute)


class Tests(unittest.TestCase):

    def setUp(self):
        setUpTest()

    def ingest(self, url, collection, catalog):
        inputs = InputIngestProcess(url=url, collection=collection, catalog=catalog)
        execute = Execute(inputs=inputs.model_dump())
        r = requests.post("/".join([APROC_ENDPOINT, "processes/ingest/execution"]), data=execute.model_dump_json(), headers={"Content-Type": "application/json"})
        self.assertTrue(r.ok)
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        while status.status not in [StatusCode.failed, StatusCode.dismissed, StatusCode.successful]:
            sleep(1)
            status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        self.assertEqual(status.status, StatusCode.successful)
        self.assertEqual(status.resourceID, AprocProcess.get_resource_id(inputs))

    def test_async_ingest_theia(self):
        url = "https://catalogue.theia-land.fr/arlas/explore/theia/_search?f=metadata.core.identity.identifier%3Aeq%3ASENTINEL2A_20230604-105902-526_L2A_T31TCJ_D&righthand=false&pretty=false&flat=false&&&size=1&max-age-cache=120"
        self.ingest(url, "main_collection", "theia")

    def test_async_ingest_dimap(self):
        url = "/inputs/DIMAP/PROD_SPOT6_001/VOL_SPOT6_001_A/IMG_SPOT6_MS_001_A/"
        self.ingest(url, "main_collection", "spot6")

    def test_processes_list(self):
        r = requests.get("/".join([APROC_ENDPOINT, "processes"]))
        self.assertTrue(r.ok)
        processes: ProcessList = ProcessList(**json.loads(r.content))
        self.assertGreater(len(processes.processes), 0)
        self.assertIn("ingest", list(map(lambda p: p.id, processes.processes)))

    def test_conformance(self):
        r = requests.get("/".join([APROC_ENDPOINT, "conformance"]))
        self.assertTrue(r.ok)

    def test_jobs(self):
        r = requests.get("/".join([APROC_ENDPOINT, "jobs"]))
        self.assertTrue(r.ok)

    def __ingest_theia(self) -> StatusInfo:
        url = "https://catalogue.theia-land.fr/arlas/explore/theia/_search?f=metadata.core.identity.identifier%3Aeq%3ASENTINEL2A_20230604-105902-526_L2A_T31TCJ_D&righthand=false&pretty=false&flat=false&&&size=1&max-age-cache=120"
        collection = "main_collection"
        catalog = "theia"
        inputs = InputIngestProcess(url=url, collection=collection, catalog=catalog)
        execute = Execute(inputs=inputs.model_dump())
        r = requests.post("/".join([APROC_ENDPOINT, "processes/ingest/execution"]), data=execute.model_dump_json(), headers={"Content-Type": "application/json"})
        self.assertTrue(r.ok)
        return StatusInfo(**json.loads(r.content))

    def test_job_by_id(self):
        status: StatusInfo = self.__ingest_theia()
        status2: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        self.assertEqual(status.jobID, status2.jobID)
        self.assertEqual(status2.processID, "ingest")

    def test_job_result(self):
        status: StatusInfo = self.__ingest_theia()
        while status.status not in [StatusCode.failed, StatusCode.dismissed, StatusCode.successful]:
            sleep(1)
            status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        result = json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID, "results"])).content)
        self.assertEqual(result["item_location"], "http://airs-server:8000/arlas/airs/collections/main_collection/items/SENTINEL2A_20230604-105902-526_L2A_T31TCJ_D", result["item_location"])

    def test_get_jobs_by_resource_id(self):
        status: StatusInfo = self.__ingest_theia()
        resource_status: list = json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs/resources", status.resourceID])).content)
        self.assertGreaterEqual(len(resource_status), 1)
        self.assertEqual(resource_status[0]["resourceID"], status.resourceID)

    def test_landing_page(self):
        landing_page = json.loads(requests.get(APROC_ENDPOINT).content)
        self.assertIsNotNone(landing_page.get("title"))
        self.assertIsNotNone(landing_page.get("description"))
        self.assertIsNotNone(landing_page.get("links"))

    def test_process_by_id(self):
        process: ProcessDescription = ProcessDescription(**json.loads(requests.get("/".join([APROC_ENDPOINT, "processes", "ingest"])).content))
        self.assertEqual(process.id, "ingest")

if __name__ == '__main__':
    unittest.main()
