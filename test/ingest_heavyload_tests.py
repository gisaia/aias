import json
import os
import time
import unittest
from time import sleep

import requests
from utils import AIRS_URL, APROC_ENDPOINT, setUpTest

from aproc.core.models.ogc.job import StatusCode, StatusInfo
from aproc.core.processes.processes import Processes
from extensions.aproc.proc.ingest.ingest_process import InputIngestProcess
from aproc.core.models.ogc import (Conforms, ExceptionType, Execute)

BATCH_SIZE = 10

class Tests(unittest.TestCase):

    def setUp(self):
        setUpTest()

    def test_async_ingest_theia(self):

        start = time.time()
        r = requests.get("https://catalogue.theia-land.fr/arlas/explore/theia/_search?f=metadata.ObservationContext.processusUsed.platform_fr%3Aeq%3ASENTINEL%202&f=metadata.core.description.processingLevel_fr%3Aeq%3ANIVEAU%202A&include=data.metadata.core.identity.identifier&righthand=false&pretty=false&flat=false&&&size={}&max-age-cache=120".format(BATCH_SIZE), verify=False)
        self.assertTrue(r.ok)
        hits = json.loads(r.content)["hits"]
        status = None
        print("submitting {} archives".format(BATCH_SIZE))
        for hit in hits:
            url = "https://catalogue.theia-land.fr/arlas/explore/theia/_search?f=metadata.core.identity.identifier%3Aeq%3A{}&righthand=false&pretty=false&flat=false&&&size=1&max-age-cache=120".format(hit["md"]["id"])
            inputs = InputIngestProcess(url=url, collection="main_collection", catalog="theia")
            execute = Execute(inputs=inputs.model_dump())
            r = requests.post("/".join([APROC_ENDPOINT, "processes/ingest/execution"]), data=execute.model_dump_json(), headers={"Content-Type": "application/json"})
            self.assertTrue(r.ok)
            status: StatusInfo = StatusInfo(**json.loads(r.content))
        end = time.time()
        print("{} archives submitted in {} s".format(BATCH_SIZE, end - start))

        start = time.time()
        status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        while status.status not in [StatusCode.dismissed, StatusCode.failed, StatusCode.dismissed, StatusCode.successful]:
            sleep(1)
            status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        end = time.time()
        print("{} archives registered in {} s".format(BATCH_SIZE, end - start))
        print("Checking that the {} archives are registered ...".format(BATCH_SIZE))
        for hit in hits:
            url = AIRS_URL+"/collections/main_collection/items/{}".format(hit["md"]["id"])
            r = requests.get(url)
            print(".", end="")
            self.assertTrue(r.ok, url+" not found")


if __name__ == '__main__':
    unittest.main()
