import json
import os
import unittest
from test.utils import APROC_ENDPOINT, COLLECTION, CATALOG, MAX_ITERATIONS, setUpTest
from time import sleep

import requests

from airs.core.models import mapper
from airs.core.models.model import Item, Role
from aproc.core.models.ogc import Execute
from aproc.core.models.ogc.job import StatusCode, StatusInfo
from aproc.core.models.ogc.process import ProcessDescription, ProcessList
from extensions.aproc.proc.ingest.directory_ingest_process import \
    InputDirectoryIngestProcess
from extensions.aproc.proc.ingest.ingest_process import InputIngestProcess


LOCAL_ROOT = "/inputs"
MINIO_ROOT = "http://minio:9000/archives/inputs"  # NOSONAR
GS_ROOT = "gs://gisaia-public"


DIMAP = "DIMAP/PROD_SPOT6_001/VOL_SPOT6_001_A/IMG_SPOT6_MS_001_A/"
IKONOS = "IK2_OPER_OSA_GEO_1P_20080715T105300_N43-318_E003-351_0001.SIP/20081014210521_po_2624415_0000000/po_2624415_blu_0000000.tif"
WORLDVIEW = "WorldView_3_sample_infrared_data_View_ready_2A_infrared/"
AST = "ast/"
TERRASARX = "TDX1_SAR__MGD_SE___HS_S_SRA_20210824T165400_20210824T165401/"
RAPID_EYE = "3159120_2020-03-11_RE1_3A/"
TIF = "cog.tiff"
JP2000 = "jpeg2000.jpg2"


class Tests(unittest.TestCase):
    def setUp(self):
        setUpTest()

    def ingest(self, url, collection, catalog, expected=StatusCode.successful, include_drivers: list[str] = [], exclude_drivers: list[str] = []):
        inputs = InputIngestProcess(url=url, collection=collection, catalog=catalog, annotations="", include_drivers=include_drivers, exclude_drivers=exclude_drivers)
        execute = Execute(inputs=inputs.model_dump(exclude_none=True, exclude_unset=True))
        r = requests.post("/".join([APROC_ENDPOINT, "processes/ingest/execution"]), data=json.dumps(execute.model_dump(exclude_none=True, exclude_unset=True)), headers={"Content-Type": "application/json"})
        self.assertTrue(r.ok, str(r.status_code) + ": " + str(r.content))
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        i: int = 0
        while status.status not in [StatusCode.failed, StatusCode.dismissed, StatusCode.successful] and i < MAX_ITERATIONS:
            sleep(1)
            i = i + 1
            status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        self.assertEqual(status.status, expected)
        return status

    def ingest_directory(self, url, collection, catalog):
        inputs = InputDirectoryIngestProcess(directory=url, collection=collection, catalog=catalog, annotations="")
        execute = Execute(inputs=inputs.model_dump(exclude_none=True, exclude_unset=True))
        r = requests.post("/".join([APROC_ENDPOINT, "processes/directory_ingest/execution"]), data=json.dumps(execute.model_dump(exclude_none=True, exclude_unset=True)), headers={"Content-Type": "application/json"})
        self.assertTrue(r.ok, str(r.status_code) + ": " + str(r.content))
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        i: int = 0
        while status.status not in [StatusCode.failed, StatusCode.dismissed, StatusCode.successful] and i < MAX_ITERATIONS:
            sleep(1)
            i = i + 1
            status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        self.assertEqual(status.status, StatusCode.successful)

    def async_ingest(self, url, id, assets: list[str], archive=True, include_drivers: list[str] = [], exclude_drivers: list[str] = []):
        status = self.ingest(url, COLLECTION, CATALOG, include_drivers=include_drivers, exclude_drivers=exclude_drivers)
        result = json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID, "results"])).content)
        self.assertEqual(result["item_location"], "http://airs-server:8000/arlas/airs/collections/" + COLLECTION + "/items/" + id, result["item_location"])
        item = mapper.item_from_json(requests.get(result["item_location"]).content)
        self.check_result(item, id, assets, archive)
        return status

    def test_async_ingest_dimap(self):  # Driver DIMAP
        url = os.path.join(LOCAL_ROOT, DIMAP)
        item_id = "148ddaaa431bdd2ff06b823df1e3725d462f668bd95188603bfff443ff055c71"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])

    def test_async_ingest_dimap_minio(self):  # Driver DIMAP
        url = os.path.join(MINIO_ROOT, DIMAP)
        item_id = "a75c9fc5a9fee985be7bd967ef713a20df65e7163f660bf6607436845fb48f4b"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])

    def test_async_ingest_dimap_cloud(self):  # Driver DIMAP
        url = os.path.join(GS_ROOT, DIMAP)
        item_id = "7fb3088260c163c8bdf37f9b56b35b0232ab8adbb556f9fbfd8d547d26bc20d1"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])

    def test_async_ingest_dimap_driver_include(self):  # Driver DIMAP
        url = os.path.join(LOCAL_ROOT, DIMAP)
        self.ingest(url, COLLECTION, CATALOG, include_drivers=["dimap"])

    def test_async_ingest_dimap_driver_include_fail(self):  # Driver DIMAP
        url = os.path.join(LOCAL_ROOT, DIMAP)
        self.ingest(url, COLLECTION, CATALOG, include_drivers=["spot5"], expected=StatusCode.failed)

    def test_async_ingest_dimap_driver_exclude(self):  # Driver DIMAP
        url = os.path.join(LOCAL_ROOT, DIMAP)
        self.ingest(url, COLLECTION, CATALOG, exclude_drivers=["spot5"])

    def test_async_ingest_dimap_driver_exclude_fail(self):  # Driver DIMAP
        url = os.path.join(LOCAL_ROOT, DIMAP)
        self.ingest(url, COLLECTION, CATALOG, exclude_drivers=["dimap"], expected=StatusCode.failed)

    def test_async_ingest_ikonos(self):  # Driver GEOEYE
        url = os.path.join(LOCAL_ROOT, IKONOS)
        item_id = "0e73667ac0bd10b5f18bcb5ee40518db973b2946fe8b40d2b4cb988724ac9507"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])

    def test_async_ingest_ikonos_minio(self):  # Driver GEOEYE
        url = os.path.join(MINIO_ROOT, IKONOS)
        item_id = "7a315977cc4dfa9809514e994e5f921f13ad0e56df6e6eec172ecf6771174970"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])

    def test_async_ingest_ikonos_cloud(self):  # Driver GEOEYE
        url = os.path.join(GS_ROOT, "test-aias", IKONOS)
        item_id = "26fc0091ed9d5b0f53769ecaf2a0cef26b0007e477be9b4c94f198a26b2e00d1"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])

    def test_async_ingest_wv(self):  # Driver DIGITALGLOBE
        url = os.path.join(LOCAL_ROOT, WORLDVIEW)
        item_id = "22785c0db31d772b6ba2f685ab7b9fbfec8931b37394b53a0a7d7e519ec9aa3a"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_wv_minio(self):  # Driver DIGITALGLOBE
        url = os.path.join(MINIO_ROOT, WORLDVIEW)
        item_id = "8ae23c4168a65926d6b898e548910635d5f299ddf1e711fa873d1c552a269bb6"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_wv_cloud(self):  # Driver DIGITALGLOBE
        url = os.path.join(GS_ROOT, "test-aias", WORLDVIEW)
        item_id = "03f59a67eb3309e0a05135a8c047c364b469cae7691fa98f22026d18f5bf24d7"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_ast(self):  # Driver AST
        url = os.path.join(LOCAL_ROOT, AST)
        item_id = "af129ada4336f27a532950d43eaf4fa3802f82ea87b4cb339199e2562ef10f2c"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_ast_minio(self):  # Driver AST
        url = os.path.join(MINIO_ROOT, AST)
        item_id = "9de1896cad5ffaa490f2c38dbca2e19fb6db486350a6408364bccbc4d020f5b5"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_ast_cloud(self):  # Driver AST
        url = os.path.join(GS_ROOT, "test-aias", AST)
        item_id = "17e377bf0c44c3a7cc8ec70e1ff9c73852454bb1a86e64f3a61545138b89b08b"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_terrasarx(self):  # Driver TERRASRX
        url = os.path.join(LOCAL_ROOT, TERRASARX)
        item_id = "53b302d1f1877f7509fbdd619b2071b024aa54604fdd1d85718059dfb88aac2c"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_terrasarx_minio(self):  # Driver TERRASRX
        url = os.path.join(MINIO_ROOT, TERRASARX)
        item_id = "71bc30f00c55474b9266c422a1ffdd00b0f2fa7b086d7674c5e3b0c2f62f55b8"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_terrasarx_cloud(self):  # Driver TERRASRX
        url = os.path.join(GS_ROOT, "test-aias", TERRASARX)
        item_id = "650cbc54a5554720fa3290473f0db93888ecae701c602539018927292277ab46"
        self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_rapideye(self):  # Driver RAPIDEYE - No thumbnail nor overview.
        url = os.path.join(LOCAL_ROOT, RAPID_EYE)
        item_id = "bb2ddbcc86e90a95afa61b7cd7dccc7eb6335f6a40052e49213cb404d0baf17a"
        self.async_ingest(url, item_id, ["data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_rapideye_minio(self):  # Driver RAPIDEYE - No thumbnail nor overview.
        url = os.path.join(MINIO_ROOT, RAPID_EYE)
        item_id = "c70e4c74cc2f403f13bc1bebd953433203e346fc76d2ed248a2fc1e3bfa80154"
        self.async_ingest(url, item_id, ["data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_rapideye_cloud(self):  # Driver RAPIDEYE - No thumbnail nor overview.
        url = os.path.join(GS_ROOT, "test-aias", RAPID_EYE)
        item_id = "a4afb6d08ca248639d359ad529b84bea9afa58db4f68aab47995c46f81c3318c"
        self.async_ingest(url, item_id, ["data", "metadata", "extent", "airs_item"], archive=False)

    def test_async_ingest_tif(self):  # Driver TIF
        url = os.path.join(LOCAL_ROOT, TIF)
        item_id = "36f978ad9fe1e9b4ea8064c893140012a967e1a7a5d1ac65a589a16566f03ccd"
        self.async_ingest(url, item_id, ["data", "airs_item"], archive=False)

    def test_async_ingest_tif_minio(self):  # Driver TIF
        url = os.path.join(MINIO_ROOT, TIF)
        item_id = "dbe4de0187fb0aeaf4fddd76ff7237a160109e0bcc280952d7fc4334b30992d9"
        self.async_ingest(url, item_id, ["data", "airs_item"], archive=False)

    def test_async_ingest_tif_cloud(self):  # Driver TIF
        url = os.path.join(GS_ROOT, "test-aias", TIF)
        item_id = "03bc217a7894c34abc42d292a270a3f194096507d2a86a3365092631769ff525"
        self.async_ingest(url, item_id, ["data", "airs_item"], archive=False)

    def test_async_ingest_jpg2000(self):  # Driver JPEG2000
        url = os.path.join(LOCAL_ROOT, JP2000)
        item_id = "e2614a12233e3f859a4083b54d2b7e4e4615055013af13c73b6c7e427548785c"
        self.async_ingest(url, item_id, ["data", "airs_item"], archive=False)

    def test_async_ingest_jpg2000_minio(self):  # Driver JPEG2000
        url = os.path.join(MINIO_ROOT, JP2000)
        item_id = "7d0a49ed64306fa310b723788df1b5d43ef00c5367003007020aff1be436546f"
        self.async_ingest(url, item_id, ["data", "airs_item"], archive=False)

    def test_async_ingest_jpg2000_cloud(self):  # Driver JPEG2000
        url = os.path.join(GS_ROOT, "test-aias", JP2000)
        item_id = "95d6803989b40dd72fc642e51477cd9ed0cb4432218711246aaa447c1a3bc046"
        self.async_ingest(url, item_id, ["data", "airs_item"], archive=False)

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

    # TODO: test folder cloud
    # TODO: test folder minio

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
        self.assertEqual(item.collection, COLLECTION)
        self.assertEqual(item.catalog, CATALOG)
        self.assertEqual(item.id, id)
        self.assertIsNotNone(item.geometry)
        self.assertIsNotNone(item.geometry.get("coordinates"))
        self.assertEqual(len(item.bbox), 4)
        self.assertEqual(len(item.centroid), 2)
        self.assertIn(Role.data.value, item.assets.keys())
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
        self.assertIsNotNone(item.properties.proj__epsg)

    def test_job_by_id(self):
        url = os.path.join(LOCAL_ROOT, DIMAP)
        item_id = "148ddaaa431bdd2ff06b823df1e3725d462f668bd95188603bfff443ff055c71"
        status: StatusInfo = self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])
        status2: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        self.assertEqual(status.jobID, status2.jobID)
        self.assertEqual(status2.processID, "ingest")

    def test_get_jobs_by_resource_id(self):
        url = os.path.join(LOCAL_ROOT, DIMAP)
        item_id = "148ddaaa431bdd2ff06b823df1e3725d462f668bd95188603bfff443ff055c71"
        status: StatusInfo = self.async_ingest(url, item_id, ["thumbnail", "overview", "data", "metadata", "extent", "airs_item"])
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
