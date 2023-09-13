from aproc.proc.ingest.ingest_services import ProcServices, TaskState
from celery import states
from time import sleep
import unittest
from utils import setUpTest


class Tests(unittest.TestCase):

    def setUp(self):
        ProcServices.init("test/conf/aproc.yaml")
        setUpTest()

    def test_async_ingest_theia(self):
        task_id = ProcServices.async_register("https://catalogue.theia-land.fr/arlas/explore/theia/_search?f=metadata.core.identity.identifier%3Aeq%3ASENTINEL2A_20230604-105902-526_L2A_T31TCJ_D&righthand=false&pretty=false&flat=false&&&size=1&max-age-cache=120",
                                              "main_catalog", "theia")
        ts: TaskState = ProcServices.get_state(task_id=task_id)        
        while ts.state not in [states.SUCCESS, states.FAILURE, states.REJECTED, states.REVOKED, states.IGNORED, states.EXCEPTION_STATES]:
            print(ts.model_dump_json())
            sleep(1)
            ts: TaskState = ProcServices.get_state(task_id=task_id)
        self.assertTrue(ts.state == states.SUCCESS, ts.state)

    def test_sync_ingest_theia(self):
        r = ProcServices.sync_register("https://catalogue.theia-land.fr/arlas/explore/theia/_search?f=metadata.core.identity.identifier%3Aeq%3ASENTINEL2A_20230604-105902-526_L2A_T31TCJ_D&righthand=false&pretty=false&flat=false&&&size=1&max-age-cache=120",
                                       "main_catalog", "theia")
        self.assertTrue(r["state"] == states.SUCCESS)

    def test_async_ingest_dimap(self):
        task_id = ProcServices.async_register("/DIMAP/PROD_SPOT6_001/VOL_SPOT6_001_A/IMG_SPOT6_MS_001_A/", "main_catalog", "spot6")
        ts: TaskState = ProcServices.get_state(task_id=task_id)        
        while ts.state not in [states.SUCCESS, states.FAILURE, states.REJECTED, states.REVOKED, states.IGNORED, states.EXCEPTION_STATES]:
            print(ts.model_dump_json())
            sleep(1)
            ts: TaskState = ProcServices.get_state(task_id=task_id)
        self.assertTrue(ts.state == states.SUCCESS, ts.state)
        print(ts.info["item"])

#    SYNC TEST NOT DONE FOR DIMAP SINCE IT REQUIRES GDAL
#    def test_sync_ingest_dimap(self):
#        r = ProcServices.sync_register("/DIMAP/PROD_SPOT6_001/VOL_SPOT6_001_A/IMG_SPOT6_MS_001_A/", "main_catalog", "spot6")
#        self.assertTrue(r["state"] == states.SUCCESS)


if __name__ == '__main__':
    unittest.main()
