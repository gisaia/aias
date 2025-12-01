import json
import unittest
from test.utils import (APROC_ENDPOINT, CATALOG, COLLECTION, MAX_ITERATIONS,
                        setUpTest)
from time import sleep

import requests
from airs.core.models import mapper
from airs.core.models.model import Item
from aproc.core.models.ogc import Execute
from aproc.core.models.ogc.job import StatusCode, StatusInfo
from aproc.core.models.ogc.process import ProcessDescription, ProcessList
from extensions.aproc.proc.ingest.directory_ingest_process import \
    InputDirectoryIngestProcess
from extensions.aproc.proc.ingest.ingest_process import InputIngestProcess

DIMAP = "DIMAP/PROD_SPOT6_001/VOL_SPOT6_001_A/IMG_SPOT6_MS_001_A/"
IKONOS = "IK2_OPER_OSA_GEO_1P_20080715T105300_N43-318_E003-351_0001.SIP/20081014210521_po_2624415_0000000/po_2624415_blu_0000000.tif"
WORLDVIEW = "WorldView_3_sample_infrared_data_View_ready_2A_infrared/"
AST = "ast/"
TERRASARX = "TDX1_SAR__MGD_SE___HS_S_SRA_20210824T165400_20210824T165401/"
RAPID_EYE = "3159120_2020-03-11_RE1_3A/"
TIF = "cog.tiff"
JP2000 = "jpeg2000.jpg2"
SENTINEL2 = "S2A_MSIL1C_20240827T105021_N0511_R051_T30TYN_20240827T132431.SAFE"

CSK = "3155919-2167789/CSKS4_SCS_B_WR_03_VV_RA_SF_20141001061215_20141001061230.h5"
SENTINEL1_GRDH = "S1C_IW_GRDH_1SDV_20251118T052605_20251118T052630_005064_00A084_DD79.SAFE"
SENTINEL1_SLC = "S1C_IW_SLC__1SDV_20251201T074918_20251201T074945_005255_00A6EB_46D8.SAFE"
ICEYE = "ICEYE-Scan-mode/2631255"


class IngestTests(unittest.TestCase):
    def setUp(self):
        setUpTest()

    def wait_for(self, status: StatusInfo) -> StatusInfo:
        i: int = 0
        s = status
        while s.status not in [StatusCode.failed, StatusCode.dismissed, StatusCode.successful] and i < MAX_ITERATIONS:
            sleep(1)
            i = i + 1
            s = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", s.jobID])).content))
        return s

    def ingest(self, url: str, collection: str, catalog: str, expected=StatusCode.successful, include_drivers: list[str] = [], exclude_drivers: list[str] = []):
        r = self.ingest_no_wait(url, collection, catalog, expected, include_drivers, exclude_drivers)
        status = StatusInfo(**json.loads(r.content))
        status = self.wait_for(status)
        self.assertEqual(status.status, expected, status.model_dump_json())
        return status

    def ingest_no_wait(self, url: str, collection: str, catalog: str, expected=StatusCode.successful, include_drivers: list[str] = [], exclude_drivers: list[str] = []):
        inputs = InputIngestProcess(url=url, collection=collection, catalog=catalog, annotations="", include_drivers=include_drivers, exclude_drivers=exclude_drivers)
        execute = Execute(inputs=inputs.model_dump(exclude_none=True, exclude_unset=True))
        r = requests.post("/".join([APROC_ENDPOINT, "processes/ingest/execution"]), data=json.dumps(execute.model_dump(exclude_none=True, exclude_unset=True)), headers={"Content-Type": "application/json"})
        self.assertTrue(r.ok, str(r.status_code) + ": " + str(r.content))
        return r

    def ingest_directory(self, url: str, collection: str, catalog: str):
        inputs = InputDirectoryIngestProcess(directory=url, collection=collection, catalog=catalog, annotations="")
        execute = Execute(inputs=inputs.model_dump(exclude_none=True, exclude_unset=True))
        r = requests.post("/".join([APROC_ENDPOINT, "processes/directory_ingest/execution"]), data=json.dumps(execute.model_dump(exclude_none=True, exclude_unset=True)), headers={"Content-Type": "application/json"})
        self.assertTrue(r.ok, str(r.status_code) + ": " + str(r.content))
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        status = self.wait_for(status)
        self.assertEqual(status.status, StatusCode.successful, status.model_dump_json())

    def async_ingest(self, url: str, id: str, assets: list[str], archive=True, check_epsg=True, include_drivers: list[str] = [], exclude_drivers: list[str] = []):
        status = self.ingest(url, COLLECTION, CATALOG, include_drivers=include_drivers, exclude_drivers=exclude_drivers)
        result = json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID, "results"])).content)
        self.assertEqual(result["item_location"], "http://airs-server:8000/arlas/airs/collections/" + COLLECTION + "/items/" + id, result["item_location"])
        item = mapper.item_from_json(requests.get(result["item_location"]).content)
        self.check_result(item, id, assets, archive, check_epsg)
        return status

    def test_processes_list(self):
        r = requests.get("/".join([APROC_ENDPOINT, "processes"]))
        self.assertTrue(r.ok, str(r.status_code) + ": " + str(r.content))
        processes: ProcessList = ProcessList(**json.loads(r.content))
        self.assertGreater(len(processes.processes), 0)
        self.assertIn("ingest", list(map(lambda p: p.id, processes.processes)))

    def test_conformance(self):
        r = requests.get("/".join([APROC_ENDPOINT, "conformance"]))
        self.assertTrue(r.ok, str(r.status_code) + ": " + str(r.content))

    def test_jobs(self):
        r = requests.get("/".join([APROC_ENDPOINT, "jobs"]))
        self.assertTrue(r.ok, str(r.status_code) + ": " + str(r.content))

    def check_result(self, item: Item, id: str, assets: list, archive=True, check_epsg=True):
        self.assertEqual(item.collection, COLLECTION)
        self.assertEqual(item.catalog, CATALOG)
        self.assertEqual(item.id, id)
        self.assertIsNotNone(item.geometry)
        self.assertIsNotNone(item.geometry.get("coordinates"))
        self.assertEqual(len(item.bbox), 4)
        self.assertEqual(len(item.centroid), 2)
        self.assertIsNotNone(item.properties.item_format)
        for asset in assets:
            self.assertIsNotNone(item.assets.get(asset), asset)
            self.assertIsNotNone(item.assets.get(asset).name, asset)
            if asset != "airs_item":
                self.assertIsNotNone(item.assets.get(asset).size, asset)
                self.assertGreater(item.assets.get(asset).size, 0, asset)
                self.assertIsNotNone(item.assets.get(asset).asset_format, asset)
            self.assertIsNotNone(item.assets.get(asset).href, asset)
            self.assertIsNotNone(item.assets.get(asset).type, asset)
            self.assertIsNotNone(item.assets.get(asset).description, asset)
            self.assertGreaterEqual(len(item.assets.get(asset).roles), 1, asset)
        self.assertIsNotNone(item.properties.datetime, asset)
        if archive:
            self.assertIsNotNone(item.properties.constellation)
            self.assertIsNotNone(item.properties.instrument)
            self.assertIsNotNone(item.properties.sensor)
            self.assertIsNotNone(item.properties.sensor_type)
            self.assertIsNotNone(item.properties.gsd)
        self.assertIsNotNone(item.properties.main_asset_format)
        self.assertIsNotNone(item.properties.main_asset_name)
        if check_epsg:
            self.assertIsNotNone(item.properties.proj__epsg)

    def test_landing_page(self):
        landing_page = json.loads(requests.get(APROC_ENDPOINT).content)
        self.assertIsNotNone(landing_page.get("title"))
        self.assertIsNotNone(landing_page.get("description"))
        self.assertIsNotNone(landing_page.get("links"))

    def test_process_by_id(self):
        process: ProcessDescription = ProcessDescription(**json.loads(requests.get("/".join([APROC_ENDPOINT, "processes", "ingest"])).content))
        self.assertEqual(process.id, "ingest")


if __name__ == '__main__':
    unittest.main()
