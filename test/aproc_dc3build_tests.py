import datetime
import json
import time
import unittest
from test.utils import (AIRS_URL, APROC_ENDPOINT, COLLECTION, MAX_ITERATIONS,
                        SENTINEL_2_ID, SENTINEL_2_ITEM, TOKEN, add_item,
                        create_arlas_collection, setUpTest)
from time import sleep

import requests

from airs.core.models import mapper
from airs.core.models.model import (Band, ChunkingStrategy, CommonBandName,
                                    Item, ItemGroup, ItemReference, MimeType,
                                    Role)
from aproc.core.models.ogc import Execute
from aproc.core.models.ogc.enums import StatusCode
from aproc.core.models.ogc.job import StatusInfo
from extensions.aproc.proc.dc3build.model.dc3build_input import \
    InputDC3BuildProcess
from extensions.aproc.proc.processes.arlas_services_helper import \
    ARLASServicesHelper


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
                    ]
                ),
                ItemGroup(
                    dc3__datetime=datetime.date(2022, 9, 25),
                    dc3__references=[
                        ItemReference(
                            dc3__alias="s2",
                            dc3__collection=COLLECTION,
                            dc3__id=SENTINEL_2_ID,
                        )
                    ]
                ),
                ItemGroup(
                    dc3__datetime=datetime.date(2022, 10, 25),
                    dc3__references=[
                        ItemReference(
                            dc3__alias="s2",
                            dc3__collection=COLLECTION,
                            dc3__id=SENTINEL_2_ID,
                        )
                    ]
                ),
            ],
            overview=True,
            bands=[Band(
                index=1,
                asset="data",
                name="B02",
                eo__common_name=CommonBandName.blue.name,
                description="Blue band",
                dc3__expression="s2.B02/10.0"
            )],
            roi=json.dumps(item.geometry),
            target_resolution=10,
            target_projection=4326,
            chunking_strategy=ChunkingStrategy.POTATO,
            title="My test cube",
            description="My test cube with 3 temporal slices",
            keywords=["cube", "sentinel 2", "3 slices"],
        )

        execute = Execute(inputs=inputs.model_dump(exclude_none=True, exclude_unset=True))
        r = requests.post(
            "/".join([APROC_ENDPOINT, "processes/dc3build/execution"]),
            data=json.dumps(execute.model_dump(exclude_none=True, exclude_unset=True), default=mapper.serialize_datetime),
            headers={"Content-Type": MimeType.JSON.value, "Authorization": TOKEN}
        )
        self.assertTrue(r.ok)
        status = StatusInfo(**json.loads(r.content))
        i: int = 0
        while status.status not in [
            StatusCode.failed,
            StatusCode.dismissed,
            StatusCode.successful,
        ] and i < MAX_ITERATIONS:
            sleep(1)
            i = i + 1
            status = StatusInfo(
                **json.loads(
                    requests.get(
                        "/".join([APROC_ENDPOINT, "jobs", status.jobID])
                    ).content
                )
            )
        self.assertEqual(status.status, StatusCode.successful, status.model_dump_json())
        result = json.loads(status.message)

        item: Item = ARLASServicesHelper.get_item_from_airs(airs_endpoint=AIRS_URL, collection=result["collection"], item_id=result["id"])
#        self.assertListEqual(AprocProcess.check_item(item, check_asset_exists=False), [])
        self.assertIsNotNone(item.assets.get(Role.datacube.value).href)
        self.assertTrue(ARLASServicesHelper.asset_in_airs(airs_endpoint=AIRS_URL, collection=result["collection"], item_id=result["id"], asset_name=Role.datacube.value))

    def ingest_sentinel(self) -> Item:
        item = add_item(self, SENTINEL_2_ITEM, SENTINEL_2_ID)
        time.sleep(3)
        create_arlas_collection(self)
        return item


if __name__ == "__main__":
    unittest.main()
