import json
import os
import time
import unittest
from time import sleep

import requests
from extensions.aproc.proc.ingest.directory_ingest_process import InputDirectoryIngestProcess
from utils import AIRS_URL, APROC_ENDPOINT, setUpTest, COLLECTION, THEIA_DIR

from aproc.core.models.ogc.job import StatusCode, StatusInfo
from aproc.core.processes.processes import Processes
from extensions.aproc.proc.ingest.ingest_process import InputIngestProcess
from aproc.core.models.ogc import (Conforms, ExceptionType, Execute)

BATCH_ROOT_SIZE = 31

class Tests(unittest.TestCase):

    def setUp(self):
        setUpTest()
        if not os.path.exists(os.path.join("test", THEIA_DIR)):
            with open("test/inputs/template_theia.json") as json_file:
                d = json.load(json_file)
                id = d["hits"][0]["md"]["id"]
                for i in range(0, BATCH_ROOT_SIZE):
                    for j in range(0, BATCH_ROOT_SIZE):
                        target = os.path.join("test", THEIA_DIR, str(i), str(j))
                        os.makedirs(target)
                        d["hits"][0]["md"]["id"] = "{}_{}_{}".format(id, i, j)
                        with open(os.path.join(target, "item.json"), "w") as theia_file:
                            json.dump(d, theia_file)
                    
    def test_ingest_directory(self):
        inputs = InputDirectoryIngestProcess(directory="theia", collection=COLLECTION, catalog="theia", annotations="")
        execute = Execute(inputs=inputs.model_dump())
        r = requests.post("/".join([APROC_ENDPOINT, "processes/directory_ingest/execution"]), data=json.dumps(execute.model_dump()), headers={"Content-Type": "application/json"})
        self.assertTrue(r.ok, str(r.status_code)+": "+str(r.content))
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        while status.status not in [StatusCode.failed, StatusCode.dismissed, StatusCode.successful]:
            sleep(1)
            status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
            print(status.model_dump_json())
        self.assertEqual(status.status, StatusCode.successful)
        r = requests.get("/".join([APROC_ENDPOINT, "jobs"]))
        self.assertTrue(r.ok, str(r.status_code)+": "+str(r.content))
        print(r.json())

if __name__ == '__main__':
    unittest.main()
