import requests
import os
import json
from aproc.proc.ingest.ingest_services import ProcServices, TaskState
from celery import states
import time
import unittest

from utils import setUpTest, AIRS_URL

BATCH_SIZE = 1000
class Tests(unittest.TestCase):

    def setUp(self):
        ProcServices.init(os.environ.get("APROC_CONFIGURATION_FILE"))
        setUpTest()

    def test_async_ingest_theia(self):

        start = time.time()
        r = requests.get("https://catalogue.theia-land.fr/arlas/explore/theia/_search?f=metadata.ObservationContext.processusUsed.platform_fr%3Aeq%3ASENTINEL%202&f=metadata.core.description.processingLevel_fr%3Aeq%3ANIVEAU%202A&include=data.metadata.core.identity.identifier&righthand=false&pretty=false&flat=false&&&size={}&max-age-cache=120".format(BATCH_SIZE), verify=False)
        self.assertTrue(r.ok)
        hits=json.loads(r.content)["hits"]
        task_id=None
        print("submitting {} archives".format(BATCH_SIZE))
        for hit in hits:
            url="https://catalogue.theia-land.fr/arlas/explore/theia/_search?f=metadata.core.identity.identifier%3Aeq%3A{}&righthand=false&pretty=false&flat=false&&&size=1&max-age-cache=120".format(hit["md"]["id"])
            task_id=ProcServices.async_register(url)
        end = time.time()
        print("{} archives submitted in {} s".format(BATCH_SIZE, end - start))

        start = time.time()
        ts:TaskState=ProcServices.get_state(task_id=task_id)
        while ts.state not in [states.SUCCESS, states.FAILURE, states.REJECTED, states.REVOKED, states.IGNORED, states.EXCEPTION_STATES]:
            time.sleep(1)
            ts:TaskState=ProcServices.get_state(task_id=task_id)
        end = time.time()
        print("{} archives registered in {} s".format(BATCH_SIZE, end - start))
        print("Checking that the {} archives are registered ...".format(BATCH_SIZE))
        for hit in hits:
            url=AIRS_URL+"/collections/main_catalog/items/{}".format(hit["md"]["id"])
            r = requests.get(url)
            self.assertTrue(r.ok, url+" not found")


if __name__ == '__main__':
    unittest.main()
