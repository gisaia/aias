import datetime
import json
from time import sleep
import time
import unittest
from airs.core.models import mapper
from airs.core.models.model import Item
from airs.core.models.model import RGB, Band, ChunkingStrategy, CommonBandName, Indicators, ItemGroup, ItemReference, MimeType
from aproc.core.models.ogc.enums import StatusCode
from aproc.core.models.ogc.job import StatusInfo
from extensions.aproc.proc.dc3build.dc3build_process import AprocProcess
from extensions.aproc.proc.dc3build.model.dc3build_input import InputDC3BuildProcess
from extensions.aproc.proc.processes.arlas_services_helper import ARLASServicesHelper
from aproc.core.settings import Configuration as AprocConfiguration

from test.utils import (
    AIRS_URL,
    APROC_ENDPOINT,
    COLLECTION,
    SENTINEL_2_ID,
    SENTINEL_2_ITEM,
    TOKEN,
    setUpTest,
    add_item,
)

import requests

from aproc.core.models.ogc import Execute


class Tests(unittest.TestCase):
    def setUp(self):
        setUpTest()

    def test_build_cube(self):
        item = self.ingest_sentinel()
        time.sleep(2)
        inputs = InputDC3BuildProcess(
            target_collection="cubes",
            target_catalog="sentinel_cubes",
            composition=[
                ItemGroup(
                    dc3__datetime=datetime.date(2022, 8, 25),
                    dc3__references=[
                        ItemReference(
                            dc3__alias="s2",
                            dc3__collection=COLLECTION,
                            dc3__id=SENTINEL_2_ID,
                        )
                    ],
                    dc3__quality_indicators=Indicators()
                )
            ],
            overview=True,
            bands=[Band(
                index=1,
                asset="data",
                variable_value_alias={},
                name="B01",
                eo__common_name=CommonBandName.green.name,
                description="Green band",
                dc3_expression="B01/10.0",
                dc3_rgb=RGB.GREEN
            )],
            roi=json.dumps(item.geometry),
            target_resolution=10,
            target_projection=4326,
            chunking_strategy=ChunkingStrategy.POTATO,
            title="My test cube",
            description="My test cube with 5 temporal slices",
            keywords=["cube", "sentinel 2", "5 slices"],
        )

        execute = Execute(inputs=inputs.model_dump(exclude_none=True, exclude_unset=True))
        r = requests.post(
            "/".join([APROC_ENDPOINT, "processes/dc3build/execution"]),
            data=json.dumps(execute.model_dump(exclude_none=True, exclude_unset=True), default=mapper.serialize_datetime),
            headers={"Content-Type": MimeType.JSON.value, "Authorization": TOKEN}
        )
        self.assertTrue(r.ok)
        status = StatusInfo(**json.loads(r.content))
        while status.status not in [
            StatusCode.failed,
            StatusCode.dismissed,
            StatusCode.successful,
        ]:
            sleep(1)
            status = StatusInfo(
                **json.loads(
                    requests.get(
                        "/".join([APROC_ENDPOINT, "jobs", status.jobID])
                    ).content
                )
            )
        self.assertEqual(status.status, StatusCode.successful)
        result = json.loads(status.message)
        item: Item = ARLASServicesHelper.get_item_from_airs(airs_endpoint=AIRS_URL, collection=result["collection"], item_id=result["id"])
        self.assertListEqual(AprocProcess.check_item(item, check_asset_exists=False), [])
        self.assertIsNotNone(item.assets.get("cube").href)
        self.assertTrue(ARLASServicesHelper.asset_in_airs(airs_endpoint=AIRS_URL, collection=result["collection"], item_id=result["id"], asset_name="cube"))

    def ingest_sentinel(self) -> Item:
        return add_item(self, SENTINEL_2_ITEM, SENTINEL_2_ID)


if __name__ == "__main__":
    unittest.main()
