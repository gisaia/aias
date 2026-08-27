import json
import threading
import unittest
from extensions.aproc.proc.enrich.enrich_process import OutputEnrichProcess
from test.aproc_tests import AprocTests
from test.utils import APROC_ENDPOINT, CATALOG, COLLECTION, MAX_ITERATIONS
from time import sleep

import requests
import uvicorn
from airs.core.models import mapper
from airs.core.models.model import AssetFormat, Item, Role
from aproc.core.models.ogc import Execute
from aproc.core.models.ogc.execute import Subscriber
from aproc.core.models.ogc.job import StatusCode, StatusInfo
from aproc.core.models.ogc.process import ProcessDescription, ProcessList
from extensions.aproc.proc.ingest.directory_ingest_process import \
    InputDirectoryIngestProcess
from extensions.aproc.proc.ingest.ingest_process import InputIngestProcess, OutputIngestProcess
from fastapi import FastAPI, Request

AST = "ast/"
CSK = "csk/3155919-2167789/"
CSK2 = "csk/3766521-2583221/"
SPOT6 = "spot6/PROD_SPOT6_001/VOL_SPOT6_001_A/IMG_SPOT6_MS_001_A/"
PNEOMS = "pneo/WO_000194876_1_1_SAL24178537-1_ACQ_PNEO4_03432708887687/000194876_1_1_STD_A/IMG_01_PNEO4_MS-FS/"
PNEOPAN = "pneo/WO_000194876_1_1_SAL24178537-1_ACQ_PNEO4_03432708887687/000194876_1_1_STD_A/IMG_01_PNEO4_PAN/"
ICEYE = "iceye/ICEYE-Scan-mode/2631255"
IKONOS = "geoeye/IK2_OPER_OSA_GEO_1P_20080715T105300_N43-318_E003-351_0001.SIP/20081014210521_po_2624415_0000000/po_2624415_blu_0000000.tif"
JP2000 = "images/jpeg2000.jpg2"
GEOSAT = "geosat/DE01_SL6_22S_1R_20220829T063018_20220829T063109_DMI_0_bb31/"
GEOSAT_JP2 = "geosat/DE01_SL6_22S_1R_20220829T063018_20220829T063109_DMI_0_bb31_jp2"
RADARSAT2 = "radarsat2/RS2_OK153952_PK1408404_DK1372523_F21F_20231123_052042_HH_SGF"
RAPID_EYE = "rapideye/3159120_2020-03-11_RE1_3A/"
SENTINEL1_GRDH = "sentinel1/S1C_IW_GRDH_1SDV_20251118T052605_20251118T052630_005064_00A084_DD79.SAFE"
SENTINEL1_SLC = "sentinel1/S1C_IW_SLC__1SDV_20251201T074918_20251201T074945_005255_00A6EB_46D8.SAFE"
SATELLOGIC = "satellogic/SYNTHETIC_20260101_120000_000_SN01_L1D_SR_MS_999999"
SENTINEL2 = "sentinel2/S2A_MSIL1C_20240827T105021_N0511_R051_T30TYN_20240827T132431.SAFE"
SKYSAT = "skysat/"
SOACOM = "soacom/S1A_OPER_SAR_EOSSP__CORE_L1D_OLVF_20190814T135724/"
SPOT5 = "spot5/"
PNEOMS = "pneo/WO_000194876_1_1_SAL24178537-1_ACQ_PNEO4_03432708887687/000194876_1_1_STD_A/IMG_01_PNEO4_MS-FS/"
PNEOPAN = "pneo/WO_000194876_1_1_SAL24178537-1_ACQ_PNEO4_03432708887687/000194876_1_1_STD_A/IMG_01_PNEO4_PAN/"
TERRASARX = "terrasarx/TDX1_SAR__MGD_SE___HS_S_SRA_20210824T165400_20210824T165401/"
TERRASARX_PAZ = "terrasarx/PAZ/PAZ1_SAR__EEC_RE___HS_S_SRA_20230708T052526_20230708T052527"
TIF = "images/cog.tiff"
WORLDVIEW = "digitalglobe/WorldView_3_sample_infrared_data_View_ready_2A_infrared/"
WYVERN = "wyvern/f3aa9cc0-3622-4711-a729-41e573a316f3/wyvern_dragonette-001_20250101T072826_f3aa9cc0/"
LANDSAT9 = "landsat/LC09_L1TP_201035_20251030_20251103_02_T1/"
UMBRA_STAC = "umbra/2025-12-17-21-31-57_UMBRA-10"
CAPELLA1 = "capella/CAPELLA_C11_SM_SLC_VV_20251031191104_20251031191109/"
CAPELLA2 = "capella/CAPELLA_C13_SM_GEC_VV_20251031014908_20251031014913/"
CAPELLA3 = "capella/CAPELLA_C13_SP_GEO_HH_20251031120350_20251031120428/"
SUPERVIEW = "spacewill/superview/SPACEWILL_SUPERVIEW_TIFF_MANUAL_TASKING_SYNTHETIC/SVN1-01_20260101_L2A0000000001_0000000000000001_01"
SUPERVIEW3_4 = "spacewill/superview/SPACEWILL_SUPERVIEW-NEO-03-04_TIFF_MANUAL_TASKING_SYNTHETIC/SVN1-04_20260101_L2A0000000001_1012600200000001"
SUBSCRIBER = Subscriber(successUri="http://somewhere:8080/subscriber/" + StatusCode.successful + "/{jobID}", failedUri="http://somewhere:8080/subscriber/" + StatusCode.failed + "/{jobID}", inProgressUri="http://somewhere:8080/subscriber/progress/{jobID}")   # NOSONAR

COG_MAX_SIZE = 500
COG_OVERVIEW_MAX_SIZE = 200
COG_ALL_BANDS_MAX_SIZE = 300

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

    def get_job_status(self, job_id: str) -> StatusInfo:
        r = requests.get("/".join([APROC_ENDPOINT, "jobs", job_id]))
        self.assertTrue(r.ok, str(r.status_code) + ": " + str(r.content))
        return StatusInfo(**json.loads(r.content))

    def wait_for(self, status: StatusInfo) -> StatusInfo:
        i: int = 0
        s = status
        print(f"Waiting for job {s.jobID} status {s.status}", flush=True, end="")
        while s.status not in [StatusCode.failed, StatusCode.dismissed, StatusCode.successful] and i < MAX_ITERATIONS:
            sleep(1)
            print(".", flush=True, end="")
            i = i + 1
            s = self.get_job_status(s.jobID)
        print("", flush=True)
        return s

    def get_ingest_job_result(self, job_id: str) -> OutputIngestProcess:
        r = requests.get("/".join([APROC_ENDPOINT, "jobs", job_id, "results"]))
        self.assertTrue(r.ok, str(r.status_code) + ": " + str(r.content))
        return OutputIngestProcess(**json.loads(r.content))

    def get_enrich_job_result(self, job_id: str) -> OutputEnrichProcess:
        r = requests.get("/".join([APROC_ENDPOINT, "jobs", job_id, "results"]))
        self.assertTrue(r.ok, str(r.status_code) + ": " + str(r.content))
        return OutputEnrichProcess(**json.loads(r.content))

    def ingest(self, url: str, collection: str, catalog: str, expected=StatusCode.successful, include_drivers: list[str] = [], exclude_drivers: list[str] = [], enrichments: list[str] = []) -> StatusInfo:
        r = self.ingest_no_wait(url, collection, catalog, expected, include_drivers, exclude_drivers, enrichments)
        status = StatusInfo(**json.loads(r.content))
        status = self.wait_for(status)
        self.assertEqual(status.status, expected, status.model_dump_json())
        self.assertEqual(status.status, callback_job_status[status.jobID])
        return status

    def ingest_no_wait(self, url: str, collection: str, catalog: str, expected=StatusCode.successful, include_drivers: list[str] = [], exclude_drivers: list[str] = [], enrichments: list[str] = []):
        inputs = InputIngestProcess(url=url, collection=collection, catalog=catalog, annotations="", include_drivers=include_drivers, exclude_drivers=exclude_drivers, enrichments=enrichments, cascade_subscriber=True)
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

    def async_ingest(self, url: str, assets: list[str], archive=True, check_epsg=True, include_drivers: list[str] = [], exclude_drivers: list[str] = [], enrichments: list[str] = [], data_key=Role.data.value, check_secondary_id=True):
        status = self.ingest(url, COLLECTION, CATALOG, include_drivers=include_drivers, exclude_drivers=exclude_drivers, enrichments=enrichments)

        resource_id = self.get_job_status(status.jobID).resourceID
        ingest_result = self.get_ingest_job_result(status.jobID)
        item = mapper.item_from_json(requests.get(ingest_result.item_location).content)
        self.check_result(item, assets, archive, check_epsg, data_key, check_secondary_id=check_secondary_id)
        self.assertEqual(ingest_result.error, "", "Expected no error, got: " + str(ingest_result.error))
        if enrichments:
            ingest_result = self.get_ingest_job_result(status.jobID)
            self.assertEqual(len(ingest_result.sub_jobs), 1, f"Expected one sub-job, got {len(ingest_result.sub_jobs)}")
            enrich_status = self.get_job_status(ingest_result.sub_jobs[0])
            self.assertEqual(enrich_status.resourceID, resource_id, f"Expected resourceID {resource_id}, got {enrich_status.resourceID}")
            enrich_status = self.wait_for(enrich_status)
            self.assertEqual(enrich_status.status, StatusCode.successful, enrich_status.model_dump_json())
            item = mapper.item_from_json(requests.get(ingest_result.item_location).content)
            for enrichment in enrichments:
                if enrichment == AssetFormat.cog.value:
                    self.check_cog(item, AssetFormat.cog.value.lower(), COG_MAX_SIZE)
                elif enrichment == AssetFormat.overview_cog.value:
                    self.check_cog(item, AssetFormat.overview_cog.value.lower(), COG_OVERVIEW_MAX_SIZE)
                elif enrichment == AssetFormat.all_bands_cog.value:
                    self.check_cog(item, AssetFormat.all_bands_cog.value.lower(), COG_ALL_BANDS_MAX_SIZE)
            self.assertEqual(enrich_status.status, callback_job_status[enrich_status.jobID])

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

    def check_result(self, item: Item, assets: list, archive=True, check_epsg=True, data_key=Role.data.value, check_secondary_id=True):
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
            if check_secondary_id:
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

    def check_cog(self, item: Item, asset_type: str, max_size: int):
        self.assertIsNotNone(item.assets.get(asset_type), f"{asset_type} asset exists")
        self.assertGreater(item.assets.get(asset_type).size, 0, f"{asset_type} size greater than 0")
        self.assertEqual(item.assets.get(asset_type).asset_format, AssetFormat.cog.value, "format is cog")
        self.assertEqual(item.assets.get(asset_type).proj__epsg, 3857, "projection is 3857")
        from osgeo import gdal
        with gdal.Open(item.assets.get(asset_type).href) as ds:
            src_width = ds.RasterXSize
            src_height = ds.RasterYSize
            self.assertLessEqual(src_width, max_size, f"{asset_type} width less than {max_size}")
            self.assertLessEqual(src_height, max_size, f"{asset_type} height less than {max_size}")
            self.assertGreater(src_width, 0, f"{asset_type} width greater than 0")
            self.assertGreater(src_height, 0, f"{asset_type} height greater than 0")
            self.assertIsNotNone(src_width, f"{asset_type} width is not None")
            self.assertIsNotNone(src_height, f"{asset_type} height is not None")
        info = gdal.Info(item.assets.get(asset_type).href, options=gdal.InfoOptions(format="json"))
        self.assertEqual(info.get("metadata").get("IMAGE_STRUCTURE", {}).get("LAYOUT", None), "COG", "layout is COG")

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
