import unittest
from time import sleep

from utils import setUpTest

from aproc.core.models.ogc.job import StatusCode, StatusInfo
from aproc.core.processes.processes import Processes
from extensions.aproc.proc.ingest.ingest_process import InputIngestProcess


class Tests(unittest.TestCase):

    def setUp(self):
        setUpTest()

    def test_async_ingest_theia(self):
        status: StatusInfo = Processes.execute(
            "ingest",
            InputIngestProcess(url="https://catalogue.theia-land.fr/arlas/explore/theia/_search?f=metadata.core.identity.identifier%3Aeq%3ASENTINEL2A_20230604-105902-526_L2A_T31TCJ_D&righthand=false&pretty=false&flat=false&&&size=1&max-age-cache=120",
                               collection="main_collection",
                               catalog="theia"))
        while status.status not in [StatusCode.failed, StatusCode.dismissed, StatusCode.successful]:
            sleep(1)
            status: StatusInfo = Processes.status(status.jobID)
        self.assertTrue(status.status == StatusCode.successful, status.status)

    def test_async_ingest_dimap(self):
        status: StatusInfo = Processes.execute(
            "ingest",
            InputIngestProcess(url="/DIMAP/PROD_SPOT6_001/VOL_SPOT6_001_A/IMG_SPOT6_MS_001_A/",
                               collection="main_collection",
                               catalog="spot6"))
        while status.status not in [StatusCode.failed, StatusCode.dismissed, StatusCode.successful]:
            sleep(1)
            status: StatusInfo = Processes.status(status.jobID)
        self.assertTrue(status.status == StatusCode.successful, status.status)


if __name__ == '__main__':
    unittest.main()
