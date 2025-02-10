import json
import os
import unittest
from airs.core.models.model import AssetFormat, MimeType
from test.utils import (APROC_ENDPOINT, ARLAS_COLLECTION, ARLAS_URL, ASSET_NAME, MAX_ITERATIONS,
                        BBOX, CLOUD_ID, CLOUD_ITEM, COLLECTION, EPSG_27572, ID, ITEM_PATH, SENTINEL_2_ID,
                        SENTINEL_2_ITEM, SMTP_SERVER, TOKEN, add_item,
                        index_collection_prefix, setUpTest)
from time import sleep

import requests

from aproc.core.models.ogc import Execute
from aproc.core.models.ogc.job import StatusCode, StatusInfo
from aproc.core.models.ogc.process import ProcessList
from extensions.aproc.proc.download.download_process import (
    InputDownloadProcess, OutputDownloadProcess)


class Tests(unittest.TestCase):

    def setUp(self):
        setUpTest()
        requests.delete(SMTP_SERVER + "/*")
        add_item(self, ITEM_PATH, ID)
        sleep(3)
        # Create collection
        r = requests.put("/".join([ARLAS_URL, "arlas", "collections", ARLAS_COLLECTION]), headers={"Content-Type": MimeType.JSON.value}, data=json.dumps({
                         "index_name": index_collection_prefix + "_" + ARLAS_COLLECTION,
                         "id_path": "id",
                         "geometry_path": "geometry",
                         "centroid_path": "centroid",
                         "timestamp_path": "properties.datetime"
                         }))
        self.assertTrue(r.ok, str(r.status_code) + " " + str(r.content))

    def test_download_exists(self):
        # CHECK THE DOWNLOAD PROCESS EXISTS
        r = requests.get("/".join([APROC_ENDPOINT, "processes"]))
        self.assertTrue(r.ok)
        processes: ProcessList = ProcessList(**json.loads(r.content))
        self.assertGreater(len(processes.processes), 0)
        self.assertIn("download", list(map(lambda p: p.id, processes.processes)))

    def test_incorrect_download(self):
        # SEND INCORRECT DOWNLOAD REQUEST (no item yet)
        inputs = InputDownloadProcess(requests=[{"collection": COLLECTION, "item_id": "item_that_deos_not_exist"}], crop_wkt="", target_format="", target_projection="")
        execute = Execute(inputs=inputs.model_dump(exclude_none=True, exclude_unset=True))
        r = requests.post("/".join([APROC_ENDPOINT, "processes/download/execution"]), data=json.dumps(execute.model_dump(exclude_none=True, exclude_unset=True)), headers={"Content-Type": MimeType.JSON.value, "Authorization": TOKEN})
        self.assertFalse(r.ok, str(r.status_code) + ": " + str(r.content))
        # REQUEST MAILS AND ERROR MAILS HAVE BEEN SENT
        r = requests.get(SMTP_SERVER + "?page=1&pageSize=30", headers={'Accept': 'application/json, text/plain, */*'})
        self.assertTrue(r.ok, r.status_code)
        self.assertEqual(len(r.json()["results"]), 3)

    @staticmethod
    def __download_found(url: str):
        if url.startswith("http"):
            print("downloads placed on s3")
            return requests.head(url).status_code == 200
        else:
            print("downloads placed in directory")
            return os.path.exists("./" + url)

    def test_download_project_native_format_native_nocrop(self):
        self.download_and_check_result(ids=[ID, ID], crop_wkt="", target_format="native",
                                       target_projection="native", raw_archive=False,
                                       expected_files=[f"{ASSET_NAME}.tif"])

        # MAILS HAVE BEEN SENT
        r = requests.get(SMTP_SERVER + "?page=1&pageSize=30", headers={'Accept': 'application/json, text/plain, */*'})
        sleep(5)
        self.assertTrue(r.ok, r.status_code)
        self.assertEqual(len(r.json()["results"]), 8)

    def test_download_project_native_format_native_crop(self):
        self.download_and_check_result(ids=[ID], crop_wkt=BBOX, target_format="native",
                                       target_projection="native", raw_archive=False,
                                       expected_files=[f"{ASSET_NAME}.tif", f"{ASSET_NAME}.tfw"])

    def test_download_project_native_format_native_crop_cloud(self):
        add_item(self, CLOUD_ITEM, CLOUD_ID)
        sleep(3)

        self.download_and_check_result(ids=[CLOUD_ID], crop_wkt=BBOX, target_format="native",
                                       target_projection="native", raw_archive=False,
                                       expected_files=[f"{ASSET_NAME}.tif", f"{ASSET_NAME}.tfw"])

    def test_download_archive_geotiff(self):
        self.download_and_check_result(ids=[ID], crop_wkt="", target_format="native",
                                       target_projection="native", raw_archive=True,
                                       expected_files=[f"{ASSET_NAME}.tif"])

    def test_download_archive_geotiff_cloud(self):
        add_item(self, CLOUD_ITEM, CLOUD_ID)
        sleep(3)

        self.download_and_check_result(ids=[CLOUD_ID], crop_wkt="", target_format="native",
                                       target_projection="native", raw_archive=True,
                                       expected_files=[f"{ASSET_NAME}.tif"])

    def test_download_project_3857_format_jp2_crop(self):
        self.download_and_check_result(ids=[ID], crop_wkt="", target_format=AssetFormat.jpg2000.value,
                                       target_projection=EPSG_27572, raw_archive=False,
                                       expected_files=[f"{ASSET_NAME}.J2w", f"{ASSET_NAME}.JP2", f"{ASSET_NAME}.JP2.aux.xml"])

    def test_download_project_3857_format_jp2_crop_cloud(self):
        add_item(self, CLOUD_ITEM, CLOUD_ID)
        sleep(3)

        self.download_and_check_result(ids=[CLOUD_ID], crop_wkt="", target_format=AssetFormat.jpg2000.value,
                                       target_projection=EPSG_27572, raw_archive=False,
                                       expected_files=[f"{ASSET_NAME}.J2w", f"{ASSET_NAME}.JP2", f"{ASSET_NAME}.JP2.aux.xml"])

    def test_download_zarr(self):
        add_item(self, SENTINEL_2_ITEM, SENTINEL_2_ID)
        sleep(3)

        crop_wkt = "POLYGON ((0.087547 42.794645, 0.087547 42.832926, 0.176811 42.832926, 0.176811 42.794645, 0.087547 42.794645))"

        self.download_and_check_result(ids=[SENTINEL_2_ID], crop_wkt=crop_wkt, target_format=AssetFormat.zarr.value,
                                       target_projection="native", raw_archive=False,
                                       expected_files=["S2A_MSIL1C_20240827T105021_N0511_R051_T30TYN_20240827T132431_downsampled.ZARR.tar"])

    def test_download_cancelled(self):
        # test 1 : cancel before it's running
        r = self.send_download_request(InputDownloadProcess(requests=[{"collection": COLLECTION, "item_id": ID}], crop_wkt="", target_format=AssetFormat.jpg2000.value, target_projection=EPSG_27572, raw_archive=False))
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID, "cancel"])).content))
        i: int = 0
        while status.status not in [StatusCode.failed, StatusCode.dismissed, StatusCode.successful] and i < MAX_ITERATIONS:
            sleep(1)
            i = i + 1
            status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        self.assertEqual(status.status, StatusCode.dismissed, status.message)

        # test 2 : cancel while it's running
        r = self.send_download_request(InputDownloadProcess(requests=[{"collection": COLLECTION, "item_id": ID}], crop_wkt="", target_format=AssetFormat.jpg2000.value, target_projection=EPSG_27572, raw_archive=False))
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        i: int = 0
        while status.status not in [StatusCode.running, StatusCode.failed, StatusCode.dismissed, StatusCode.successful] and i < MAX_ITERATIONS:
            sleep(1)
            i = i + 1
            status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID, "cancel"])).content))
        i: int = 0
        while status.status not in [StatusCode.failed, StatusCode.dismissed, StatusCode.successful] and i < MAX_ITERATIONS:
            sleep(1)
            i = i + 1
            status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        self.assertEqual(status.status, StatusCode.dismissed, status.message)

    def send_download_request(self, inputs: InputDownloadProcess):
        execute = Execute(inputs=inputs.model_dump(exclude_none=True, exclude_unset=True))
        r = requests.post("/".join([APROC_ENDPOINT, "processes/download/execution"]), data=json.dumps(execute.model_dump(exclude_none=True, exclude_unset=True)), headers={"Content-Type": MimeType.JSON.value, "Authorization": TOKEN})
        self.assertTrue(r.ok)
        return r

    def get_result(self, status: StatusInfo):
        # GET RESULT (and file location)
        result = requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID, "results"]))
        self.assertTrue(result.ok, result.status_code)
        result: OutputDownloadProcess = OutputDownloadProcess(**json.loads(result.content))
        return result

    def wait_for_success(self, status: StatusInfo):
        i: int = 0
        while status.status not in [StatusCode.failed, StatusCode.dismissed, StatusCode.successful] and i < MAX_ITERATIONS:
            sleep(1)
            i = i + 1
            status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        self.assertEqual(status.status, StatusCode.successful, status.message)
        return status

    def download_and_check_result(self, ids: list[str], crop_wkt: str, target_format: str, target_projection: str, raw_archive: bool, expected_files: list[str]):
        r = self.send_download_request(InputDownloadProcess(
            requests=list(map(lambda id: {"collection": COLLECTION, "item_id": id}, ids)),
            crop_wkt=crop_wkt,
            target_format=target_format,
            target_projection=target_projection,
            raw_archive=raw_archive))

        status: StatusInfo = StatusInfo(**json.loads(r.content))
        status = self.wait_for_success(status)

        result = self.get_result(status)

        # FILE MUST EXIST
        for f in expected_files:
            self.assertTrue(Tests.__download_found(os.path.join(result.download_locations[0], f)))


if __name__ == '__main__':
    unittest.main()
