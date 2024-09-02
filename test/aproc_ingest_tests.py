import json
import unittest
from test.utils import APROC_ENDPOINT, COLLECTION, CATALOG, setUpTest
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


class Tests(unittest.TestCase):
    def setUp(self):
        setUpTest()

    def ingest(self, url, collection, catalog, expected=StatusCode.successful):
        inputs = InputIngestProcess(url=url, collection=collection, catalog=catalog, annotations="")
        execute = Execute(inputs=inputs.model_dump())
        r = requests.post("/".join([APROC_ENDPOINT, "processes/ingest/execution"]), data=json.dumps(execute.model_dump()), headers={"Content-Type": "application/json"})
        self.assertTrue(r.ok, str(r.status_code) + ": " + str(r.content))
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        while status.status not in [StatusCode.failed, StatusCode.dismissed, StatusCode.successful]:
            sleep(1)
            status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        self.assertEqual(status.status, expected)
        return status

    def ingest_directory(self, url, collection, catalog):
        inputs = InputDirectoryIngestProcess(directory=url, collection=collection, catalog=catalog, annotations="")
        execute = Execute(inputs=inputs.model_dump())
        r = requests.post("/".join([APROC_ENDPOINT, "processes/directory_ingest/execution"]), data=json.dumps(execute.model_dump()), headers={"Content-Type": "application/json"})
        self.assertTrue(r.ok, str(r.status_code) + ": " + str(r.content))
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        while status.status not in [StatusCode.failed, StatusCode.dismissed, StatusCode.successful]:
            sleep(1)
            status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        self.assertEqual(status.status, StatusCode.successful)

    def async_ingest(self, url, id, assets: list[str], archive=True):
        status = self.ingest(url, COLLECTION, CATALOG)
        result = json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID, "results"])).content)
        self.assertEqual(result["item_location"], "http://airs-server:8000/arlas/airs/collections/" + COLLECTION + "/items/" + id, result["item_location"])
        item = mapper.item_from_json(requests.get(result["item_location"]).content)
        self.check_result(item, id, assets, archive)
        return status

    def test_async_ingest_dimap(self):  # Driver DIMAP
        url = "/inputs/DIMAP/PROD_SPOT6_001/VOL_SPOT6_001_A/IMG_SPOT6_MS_001_A/"
        id = "148ddaaa431bdd2ff06b823df1e3725d462f668bd95188603bfff443ff055c71"
        self.async_ingest(url, id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])

    def test_async_ingest_ikonos(self):  # Driver GEOEYE
        url = "/inputs/IK2_OPER_OSA_GEO_1P_20080715T105300_N43-318_E003-351_0001.SIP/20081014210521_po_2624415_0000000/po_2624415_blu_0000000.tif"
        id = "0e73667ac0bd10b5f18bcb5ee40518db973b2946fe8b40d2b4cb988724ac9507"
        self.async_ingest(url, id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])

    def test_async_ingest_wv(self):  # Driver DIGITALGLOBE
        url = "/inputs/WorldView_3_sample_infrared_data_View_ready_2A_infrared"
        id = "4bd829d461af55d10d3cf98ae2f5014e1945b8d42c60fa36b76245e167fc35ba"
        self.async_ingest(url, id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_ast(self):  # Driver AST
        url = "/inputs/ast/AST_L1B_00307242024224227_20240729075840_2355295.VNIR_Swath.ImageData3N.tif"
        id = "ae0f91d2865b53188eb11158723f192b72dae3ad13ecaf5f5af9d28785c88aeb"
        self.async_ingest(url, id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_terrasarx(self):  # Driver TERRASRX
        url = "/inputs/TDX1_SAR__MGD_SE___HS_S_SRA_20210824T165400_20210824T165401/TDX1_SAR__MGD_SE___HS_S_SRA_20210824T165400_20210824T165401.xml"
        id = "76871773d00a00aead7e7ab7e6b59182b3da8b0ab8679a2c5d15457fccdd24ce"
        self.async_ingest(url, id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_rapideye(self):  # Driver RAPIDEYE - No thumbnail nor overview.
        url = "/inputs/3159120_2020-03-11_RE1_3A"
        id = "f07bc337f2c904f7d23007b0d9c868872036162dc48f954ccd46f55198de530e"
        self.async_ingest(url, id, ["data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_tif(self):  # Driver TIF
        url = "/inputs/cog.tiff"
        id = "36f978ad9fe1e9b4ea8064c893140012a967e1a7a5d1ac65a589a16566f03ccd"
        self.async_ingest(url, id, ["data", "airs_item"], archive=False)

    def test_async_ingest_jpg2000(self):  # Driver JPEG2000
        url = "/inputs/jpeg2000.jpg2"
        id = "e2614a12233e3f859a4083b54d2b7e4e4615055013af13c73b6c7e427548785c"
        self.async_ingest(url, id, ["data", "airs_item"], archive=False)

    def test_async_ingest_invalid_tif(self):  # Test Driver error handling
        url = "/inputs/empty.tiff"
        status = self.ingest(url, COLLECTION, CATALOG, StatusCode.failed)
        self.assertGreaterEqual(status.message.index("Exception while ingesting"), 0)

    def test_async_ingest_nogeo_tif(self):  # Test Driver error handling
        url = "/inputs/nogeo.tiff"
        status = self.ingest(url, COLLECTION, CATALOG, StatusCode.failed)
        self.assertGreaterEqual(status.message.index("Exception while ingesting"), 0)

    def test_ingest_folder(self):  # Test Folder ingestion
        self.ingest_directory("", collection=COLLECTION, catalog=CATALOG)

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

    def check_result(self, item: Item, id, assets: list, archive=True):
        self.assertEquals(item.collection, COLLECTION)
        self.assertEquals(item.catalog, CATALOG)
        self.assertEquals(item.id, id)
        self.assertIsNotNone(item.geometry)
        self.assertIsNotNone(item.geometry.get("coordinates"))
        self.assertEquals(len(item.bbox), 4)
        self.assertEquals(len(item.centroid), 2)
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
        self.assertIsNotNone(item.properties.proj__epsg)

    def test_job_by_id(self):
        url = "/inputs/DIMAP/PROD_SPOT6_001/VOL_SPOT6_001_A/IMG_SPOT6_MS_001_A/"
        id = "148ddaaa431bdd2ff06b823df1e3725d462f668bd95188603bfff443ff055c71"
        status: StatusInfo = self.async_ingest(url, id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])
        status2: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        self.assertEqual(status.jobID, status2.jobID)
        self.assertEqual(status2.processID, "ingest")

    def test_get_jobs_by_resource_id(self):
        url = "/inputs/DIMAP/PROD_SPOT6_001/VOL_SPOT6_001_A/IMG_SPOT6_MS_001_A/"
        id = "148ddaaa431bdd2ff06b823df1e3725d462f668bd95188603bfff443ff055c71"
        status: StatusInfo = self.async_ingest(url, id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])
        resource_status: list = json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs/resources", status.resourceID])).content)
        self.assertGreaterEqual(len(resource_status), 1)
        self.assertEqual(resource_status[0]["resourceID"], status.resourceID)

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
