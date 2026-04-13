import json
import os
from time import sleep
import unittest
from airs.core.models import mapper
from airs.core.models.model import Item
from aproc.core.models.ogc.enums import StatusCode
from aproc.core.models.ogc.job import StatusInfo
from test.aproc_ingest_tests import PNEOMS, GEOSAT, IKONOS, WYVERN, PNEOPAN
from test.aproc_tests import AprocTests
from test.utils import (AIRS_URL, APROC_ENDPOINT, CATALOG, COLLECTION, SENTINEL_2_ID, SENTINEL_2_ITEM, SENTINEL_2_ZIP_ID, MAX_ITERATIONS,
                        SENTINEL_2_ZIP_ITEM, add_item)
import requests

from aproc.core.models.ogc import Execute
from extensions.aproc.proc.enrich.enrich_process import InputEnrichProcess
from test.aproc_ingest_tests_gs import ROOT, Tests as IngestionTests

class Tests(AprocTests):

    def __enrich_cog(self, id: str):
        inputs: InputEnrichProcess = InputEnrichProcess(requests=[{"collection": COLLECTION, "item_id": id}], asset_type="cog")
        execute = Execute(inputs=inputs.model_dump(exclude_none=True, exclude_unset=True))
        r = requests.post("/".join([APROC_ENDPOINT, "processes/enrich/execution"]), data=json.dumps(execute.model_dump(exclude_none=True, exclude_unset=True)), headers={"Content-Type": "application/json"})
        self.assertTrue(r.ok)
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        i: int = 0
        while status.status not in [StatusCode.failed, StatusCode.dismissed, StatusCode.successful] and i < MAX_ITERATIONS:
            sleep(1)
            i = i + 1
            status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        self.assertEqual(status.status, StatusCode.successful, status.model_dump_json())

        # check that the item has the new asset
        item: Item = mapper.item_from_dict(requests.get("/".join([AIRS_URL, "collections", COLLECTION, "items", id])).json())
        self.assertIsNotNone(item.assets.get("cog"))
        return item

    def test_enrich_s2_cog_from_zip(self):
        add_item(self, SENTINEL_2_ZIP_ITEM, SENTINEL_2_ZIP_ID)
        self.__enrich_cog(SENTINEL_2_ZIP_ID)

    def test_enrich_s2_cog_from_folder(self):
        add_item(self, SENTINEL_2_ITEM, SENTINEL_2_ID)
        item: Item = self.__enrich_cog(SENTINEL_2_ID)
        self.assertIsNotNone(item.assets.get("all_bands_cog"))

    def test_enrich_archive_cog(self, url):
        r = IngestionTests().ingest_no_wait(url, COLLECTION, CATALOG)
        status = StatusInfo(**json.loads(r.content))
        status = IngestionTests().wait_for(status)
        result = json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID, "results"])).content)
        item = mapper.item_from_json(requests.get(result["item_location"]).content)
        item: Item = self.__enrich_cog(item.id)

    def test_enrich_pneomsms_cog(self):
        url = os.path.join(ROOT, PNEOMS)
        self.test_enrich_archive_cog(url)

    def test_enrich_pneopan_cog(self):
        url = os.path.join(ROOT, PNEOPAN)
        self.test_enrich_archive_cog(url)

    def test_enrich_geosat_cog(self):
        url = os.path.join(ROOT, GEOSAT)
        self.test_enrich_archive_cog(url)

    def test_enrich_ikonos_cog(self):
        url = os.path.join(ROOT, IKONOS)
        self.test_enrich_archive_cog(url)

    def test_enrich_wyvern_cog(self):
        url = os.path.join(ROOT, WYVERN)
        self.test_enrich_archive_cog(url)


if __name__ == '__main__':
    unittest.main()
