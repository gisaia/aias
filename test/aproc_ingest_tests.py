import json
import threading
import unittest
from test.aproc_tests import AprocTests
from test.utils import APROC_ENDPOINT, CATALOG, COLLECTION, MAX_ITERATIONS
from time import sleep

import requests
import uvicorn
from airs.core.models import mapper
from airs.core.models.model import Item, Role
from aproc.core.models.ogc import Execute
from aproc.core.models.ogc.execute import Subscriber
from aproc.core.models.ogc.job import StatusCode, StatusInfo
from aproc.core.models.ogc.process import ProcessDescription, ProcessList
from extensions.aproc.proc.ingest.directory_ingest_process import \
    InputDirectoryIngestProcess
from extensions.aproc.proc.ingest.ingest_process import InputIngestProcess
from fastapi import FastAPI, Request

AST = "ast/"
CSK = "csk/3155919-2167789/CSKS4_SCS_B_WR_03_VV_RA_SF_20141001061215_20141001061230.h5"
SPOT6 = "spot6/PROD_SPOT6_001/VOL_SPOT6_001_A/IMG_SPOT6_MS_001_A/"
PNEOMS = "pneo/WO_000194876_1_1_SAL24178537-1_ACQ_PNEO4_03432708887687/000194876_1_1_STD_A/IMG_01_PNEO4_MS-FS/"
PNEOPAN = "pneo/WO_000194876_1_1_SAL24178537-1_ACQ_PNEO4_03432708887687/000194876_1_1_STD_A/IMG_01_PNEO4_PAN/"
ICEYE = "iceye/ICEYE-Scan-mode/2631255"
IKONOS = "geoeye/IK2_OPER_OSA_GEO_1P_20080715T105300_N43-318_E003-351_0001.SIP/20081014210521_po_2624415_0000000/po_2624415_blu_0000000.tif"
JP2000 = "images/jpeg2000.jpg2"
GEOSAT = "geosat/DE01_SL6_22S_1R_20220829T063018_20220829T063109_DMI_0_bb31/"
RADARSAT2 = "radarsat2/RS2_OK153952_PK1408404_DK1372523_F21F_20231123_052042_HH_SGF"
RAPID_EYE = "rapideye/3159120_2020-03-11_RE1_3A/"
SENTINEL1_GRDH = "sentinel1/S1C_IW_GRDH_1SDV_20251118T052605_20251118T052630_005064_00A084_DD79.SAFE"
SENTINEL1_SLC = "sentinel1/S1C_IW_SLC__1SDV_20251201T074918_20251201T074945_005255_00A6EB_46D8.SAFE"
SATELLOGIC = "satellogic/SYNTHETIC_20260101_120000_000_SN01_L1D_SR_MS_999999"
SENTINEL2 = "sentinel2/S2A_MSIL1C_20240827T105021_N0511_R051_T30TYN_20240827T132431.SAFE"
SKYSAT = "skysat/"
SPOT5 = "spot5/"
PNEOMS = "pneo/WO_000194876_1_1_SAL24178537-1_ACQ_PNEO4_03432708887687/000194876_1_1_STD_A/IMG_01_PNEO4_MS-FS/"
PNEOPAN = "pneo/WO_000194876_1_1_SAL24178537-1_ACQ_PNEO4_03432708887687/000194876_1_1_STD_A/IMG_01_PNEO4_PAN/"
TERRASARX = "terrasarx/TDX1_SAR__MGD_SE___HS_S_SRA_20210824T165400_20210824T165401/"
TIF = "images/cog.tiff"
WORLDVIEW = "digitalglobe/WorldView_3_sample_infrared_data_View_ready_2A_infrared/"
WYVERN = "wyvern/f3aa9cc0-3622-4711-a729-41e573a316f3/wyvern_dragonette-001_20250101T072826_f3aa9cc0/"
LANDSAT9 = "landsat/LC09_L1TP_201035_20251030_20251103_02_T1/"
UMBRA_STAC = "umbra/2025-12-17-21-31-57_UMBRA-10"
CAPELLA1 = "capella/CAPELLA_C11_SM_SLC_VV_20251031191104_20251031191109/"
CAPELLA2 = "capella/CAPELLA_C13_SM_GEC_VV_20251031014908_20251031014913/"
CAPELLA3 = "capella/CAPELLA_C13_SP_GEO_HH_20251031120350_20251031120428/"
SUPERVIEW = "spacewill/superview/SPACEWILL_SUPERVIEW_TIFF_MANUAL_TASKING_SYNTHETIC/SVN1-01_20260101_L2A0000000001_0000000000000001_01"
SUBSCRIBER = Subscriber(successUri="http://somewhere:8080/subscriber/" + StatusCode.successful + "/{jobID}", failedUri="http://somewhere:8080/subscriber/" + StatusCode.failed + "/{jobID}", inProgressUri="http://somewhere:8080/subscriber/progress/{jobID}")   # NOSONAR

callback_job_status = {}

app = FastAPI()


@app.post("/subscriber/{status}/{id}")
async def callback(status, id, request: Request):
    await request.json()
    callback_job_status[id] = status


def run_server(port=8080):
    uvicorn.run(app, host="0.0.0.0", port=port)


# Start the server in a separate thread
threading.Thread(target=run_server, daemon=True).start()


class IngestTests(AprocTests):

    def wait_for(self, status: StatusInfo) -> StatusInfo:
        i: int = 0
        s = status
        while s.status not in [StatusCode.failed, StatusCode.dismissed, StatusCode.successful] and i < MAX_ITERATIONS:
            print(f"Waiting for job {s.jobID} status {s.status}...", flush=True)
            sleep(1)
            i = i + 1
            s = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", s.jobID])).content))
        return s

    def ingest(self, url: str, collection: str, catalog: str, expected=StatusCode.successful, include_drivers: list[str] = [], exclude_drivers: list[str] = []):
        r = self.ingest_no_wait(url, collection, catalog, expected, include_drivers, exclude_drivers)
        status = StatusInfo(**json.loads(r.content))
        status = self.wait_for(status)
        self.assertEqual(status.status, expected, status.model_dump_json())
        sleep(2)
        self.assertEqual(status.status, callback_job_status[status.jobID])
        return status

    def ingest_no_wait(self, url: str, collection: str, catalog: str, expected=StatusCode.successful, include_drivers: list[str] = [], exclude_drivers: list[str] = []):
        inputs = InputIngestProcess(url=url, collection=collection, catalog=catalog, annotations="", include_drivers=include_drivers, exclude_drivers=exclude_drivers)
        execute = Execute(inputs=inputs.model_dump(exclude_none=True, exclude_unset=True), subscriber=SUBSCRIBER)
        r = requests.post("/".join([APROC_ENDPOINT, "processes/ingest/execution"]), data=json.dumps(execute.model_dump(exclude_none=True, exclude_unset=True)), headers={"Content-Type": "application/json"})
        self.assertTrue(r.ok, str(r.status_code) + ": " + str(r.content))
        return r

    def ingest_directory(self, url: str, collection: str, catalog: str):
        inputs = InputDirectoryIngestProcess(directory=url, collection=collection, catalog=catalog, annotations="")
        execute = Execute(inputs=inputs.model_dump(exclude_none=True, exclude_unset=True), subscriber=SUBSCRIBER)
        r = requests.post("/".join([APROC_ENDPOINT, "processes/directory_ingest/execution"]), data=json.dumps(execute.model_dump(exclude_none=True, exclude_unset=True)), headers={"Content-Type": "application/json"})
        self.assertTrue(r.ok, str(r.status_code) + ": " + str(r.content))
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        status = self.wait_for(status)
        self.assertEqual(status.status, StatusCode.successful, status.model_dump_json())
        self.assertEqual(status.status, callback_job_status[status.jobID])

    def async_ingest(self, url: str, assets: list[str], archive=True, check_epsg=True, include_drivers: list[str] = [], exclude_drivers: list[str] = [], data_key=Role.data.value):
        status = self.ingest(url, COLLECTION, CATALOG, include_drivers=include_drivers, exclude_drivers=exclude_drivers)
        result = json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID, "results"])).content)
        item = mapper.item_from_json(requests.get(result["item_location"]).content)
        self.check_result(item, assets, archive, check_epsg, data_key)
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

    def check_result(self, item: Item, assets: list, archive=True, check_epsg=True, data_key=Role.data.value):
        self.assertEqual(item.collection, COLLECTION)
        self.assertEqual(item.catalog, CATALOG)
        self.assertIsNotNone(item.id)
        self.assertIsNotNone(item.geometry)
        self.assertIsNotNone(item.geometry.get("coordinates"))
        self.assertEqual(len(item.bbox), 4)
        self.assertEqual(len(item.centroid), 2)
        if data_key is not None:
            self.assertIn(data_key, item.assets.keys())
        self.assertIsNotNone(item.properties.item_format)
        self.assertIsNotNone(item.properties.observation_type)
        self.assertIn(Role.archive.value, item.assets.keys())
        for asset in assets:
            self.assertIsNotNone(item.assets.get(asset), f"{asset} not in {item.assets.keys()}")
            self.assertIsNotNone(item.assets.get(asset).name, asset)
            if asset != "airs_item" and asset != "archive":
                self.assertIsNotNone(item.assets.get(asset).size, asset)
                self.assertGreater(item.assets.get(asset).size, 0, asset)
                self.assertIsNotNone(item.assets.get(asset).asset_format, asset)
            self.assertIsNotNone(item.assets.get(asset).href, asset)
            self.assertIsNotNone(item.assets.get(asset).type, asset)
            self.assertIsNotNone(item.assets.get(asset).description, asset)
            self.assertGreaterEqual(len(item.assets.get(asset).roles), 1, asset)
        if Role.thumbnail.value in item.assets.keys():
            self.assertTrue(item.assets.get(Role.thumbnail.value).airs__managed, f"thumbnail asset should be managed for {id}")
        if Role.overview.value in item.assets.keys():
            self.assertTrue(item.assets.get(Role.overview.value).airs__managed, f"overview asset should be managed for {id}")
        self.assertIsNotNone(item.properties.datetime, asset)
        if archive:
            self.assertIsNotNone(item.properties.item_type)
            self.assertIsNotNone(item.properties.item_format)
            self.assertIsNotNone(item.properties.observation_type)
            self.assertIsNotNone(item.properties.secondary_id)
            self.assertIsNotNone(item.properties.constellation)
            self.assertIsNotNone(item.properties.satellite)
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
