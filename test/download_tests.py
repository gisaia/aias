import unittest
from time import sleep
import requests
import json
from aproc.core.models.ogc.process import ProcessList, ProcessDescription

from utils import AIRS_URL, APROC_ENDPOINT, setUpTest

from aproc.core.models.ogc.job import StatusCode, StatusInfo
from aproc.core.processes.processes import Processes
from aproc.core.models.ogc import (Conforms, ExceptionType, Execute)


class Tests(unittest.TestCase):

    def setUp(self):
        setUpTest()

    def test_processes_list(self):
        r = requests.get("/".join([APROC_ENDPOINT, "processes"]))
        self.assertTrue(r.ok)
        processes: ProcessList = ProcessList(**json.loads(r.content))
        self.assertEqual(len(processes.processes), 1)
        self.assertIn("download", list(map(lambda p: p.id, processes.processes)))

if __name__ == '__main__':
    unittest.main()
