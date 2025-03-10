import json
from time import sleep
import unittest
from airs.core.models import mapper
from aproc.core.models.ogc.enums import StatusCode
from aproc.core.models.ogc.job import StatusInfo
from test.utils import (AIRS_URL, APROC_ENDPOINT, COLLECTION, SENTINEL_2_ID, MAX_ITERATIONS,
                        SENTINEL_2_ITEM, setUpTest, add_item)

import requests

from aproc.core.models.ogc import Execute
from extensions.aproc.proc.enrich.enrich_process import InputEnrichProcess


class Tests(unittest.TestCase):
    def setUp(self):
        setUpTest()

    def test_enrich_cog(self):
        self.ingest_sentinel()
        inputs: InputEnrichProcess = InputEnrichProcess(requests=[{"collection": COLLECTION, "item_id": SENTINEL_2_ID}], asset_type="cog")
        execute = Execute(inputs=inputs.model_dump(exclude_none=True, exclude_unset=True))
        r = requests.post("/".join([APROC_ENDPOINT, "processes/enrich/execution"]), data=json.dumps(execute.model_dump(exclude_none=True, exclude_unset=True)), headers={"Content-Type": "application/json"})
        self.assertTrue(r.ok)
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        i: int = 0
        while status.status not in [StatusCode.failed, StatusCode.dismissed, StatusCode.successful] and i < MAX_ITERATIONS:
            sleep(1)
            i = i + 1
            status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        self.assertEqual(status.status, StatusCode.successful)

        # check that the item has the new asset
        item = mapper.item_from_dict(requests.get("/".join([AIRS_URL, "collections", COLLECTION, "items", SENTINEL_2_ID])).json())
        self.assertIsNotNone(item.assets.get("cog"))

    def ingest_sentinel(self):
        add_item(self, SENTINEL_2_ITEM, SENTINEL_2_ID)


if __name__ == '__main__':
    unittest.main()
