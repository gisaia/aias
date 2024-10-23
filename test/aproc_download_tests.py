import json
import os
import unittest
from test.utils import (AIRS_URL, APROC_ENDPOINT, ARLAS_COLLECTION, ARLAS_URL,
                        BBOX, COLLECTION, ID, ITEM_PATH, SENTINEL_2_ID,
                        SENTINEL_2_ITEM, SMTP_SERVER, TOKEN,
                        index_collection_prefix, setUpTest)
from time import sleep

import requests

from airs.core.models import mapper
from airs.core.models.model import AssetFormat, Item
from aproc.core.models.ogc import Execute
from aproc.core.models.ogc.job import StatusCode, StatusInfo
from aproc.core.models.ogc.process import ProcessList
from extensions.aproc.proc.download.download_process import (
    InputDownloadProcess, OutputDownloadProcess)


class Tests(unittest.TestCase):

    def setUp(self):
        setUpTest()
        requests.delete(SMTP_SERVER + "/*")
        self.__add_item__(ITEM_PATH, ID)
        sleep(3)
        # Create collection
        print("create collection {}".format(ARLAS_COLLECTION))
        r = requests.put("/".join([ARLAS_URL, "arlas", "collections", ARLAS_COLLECTION]), headers={"Content-Type": "application/json"}, data=json.dumps({
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
        execute = Execute(inputs=inputs.model_dump())
        r = requests.post("/".join([APROC_ENDPOINT, "processes/download/execution"]), data=json.dumps(execute.model_dump()), headers={"Content-Type": "application/json", "Authorization": TOKEN})
        self.assertFalse(r.ok, str(r.status_code) + ": " + str(r.content))
        # REQUEST MAILS AND ERROR MAILS HAVE BEEN SENT
        r = requests.get(SMTP_SERVER + "?page=1&pageSize=30", headers={'Accept': 'application/json, text/plain, */*'})
        self.assertTrue(r.ok, r.status_code)
        self.assertEqual(len(r.json()["results"]), 3)

    def __download_found(url: str):
        if url.startswith("http"):
            print("downloads placed on s3")
            return requests.head(url).status_code == 200
        else:
            print("downloads placed in directory")
            return os.path.exists("./" + url)

    def test_download_project_native_format_native_nocrop(self):
        r = self.send_download_request(InputDownloadProcess(requests=[{"collection": COLLECTION, "item_id": ID}, {"collection": COLLECTION, "item_id": ID}], crop_wkt="", target_format="native", target_projection="native", raw_archive=False))
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        status = self.wait_for_success(status)
        result = self.get_result(status)
        # FILE MUST EXISTS
        self.assertTrue(Tests.__download_found(result.download_locations[0] + "/ESA_WorldCover_10m_2021_v200_N15E000_Map.tif"))

        # MAILS HAVE BEEN SENT
        r = requests.get(SMTP_SERVER + "?page=1&pageSize=30", headers={'Accept': 'application/json, text/plain, */*'})
        sleep(5)
        self.assertTrue(r.ok, r.status_code)
        self.assertEqual(len(r.json()["results"]), 8)

    def test_download_project_native_format_native_crop(self):
        r = self.send_download_request(InputDownloadProcess(requests=[{"collection": COLLECTION, "item_id": ID}], crop_wkt=BBOX, target_format="native", target_projection="native", raw_archive=False))
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        status = self.wait_for_success(status)
        result = self.get_result(status)
        # FILE MUST EXISTS
        self.assertTrue(Tests.__download_found(result.download_locations[0] + "/ESA_WorldCover_10m_2021_v200_N15E000_Map.tif"))
        self.assertTrue(Tests.__download_found(result.download_locations[0] + "/ESA_WorldCover_10m_2021_v200_N15E000_Map.tfw"))

    def test_download_archive_geotiff(self):
        r = self.send_download_request(InputDownloadProcess(requests=[{"collection": COLLECTION, "item_id": ID}], crop_wkt="", target_format="native", target_projection="native", raw_archive=True))
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        status = self.wait_for_success(status)
        result = self.get_result(status)
        # FILE MUST EXISTS
        self.assertTrue(Tests.__download_found(result.download_locations[0] + "/ESA_WorldCover_10m_2021_v200_N15E000_Map.tif"))

    def test_download_project_3857_format_jp2_crop(self):
        r = self.send_download_request(InputDownloadProcess(requests=[{"collection": COLLECTION, "item_id": ID}], crop_wkt="", target_format=AssetFormat.jpg2000.value, target_projection="EPSG:27572", raw_archive=False))
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        status = self.wait_for_success(status)
        result = self.get_result(status)
        # FILE MUST EXISTS
        self.assertTrue(Tests.__download_found(result.download_locations[0] + "/ESA_WorldCover_10m_2021_v200_N15E000_Map.J2w"))
        self.assertTrue(Tests.__download_found(result.download_locations[0] + "/ESA_WorldCover_10m_2021_v200_N15E000_Map.JP2"))
        self.assertTrue(Tests.__download_found(result.download_locations[0] + "/ESA_WorldCover_10m_2021_v200_N15E000_Map.JP2.aux.xml"))

    def test_download_zarr(self):
        self.__add_item__(SENTINEL_2_ITEM, SENTINEL_2_ID)
        sleep(3)

        crop_wkt = "POLYGON ((0.087547 42.794645, 0.087547 42.832926, 0.176811 42.832926, 0.176811 42.794645, 0.087547 42.794645))"

        r = self.send_download_request(InputDownloadProcess(requests=[{"collection": COLLECTION, "item_id": SENTINEL_2_ID}], crop_wkt=crop_wkt,
                                                            target_format=AssetFormat.zarr.value, target_projection="native", raw_archive=False))
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        status = self.wait_for_success(status)
        result = self.get_result(status)
        # FILE MUST EXISTS
        self.assertTrue(Tests.__download_found(result.download_locations[0] + "/S2A_MSIL1C_20240827T105021_N0511_R051_T30TYN_20240827T132431.ZARR"))

    def test_download_cancelled(self):
        # test 1 : cancell before it's running
        r = self.send_download_request(InputDownloadProcess(requests=[{"collection": COLLECTION, "item_id": ID}], crop_wkt="", target_format=AssetFormat.jpg2000.value, target_projection="EPSG:27572", raw_archive=False))
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID, "cancel"])).content))
        tries = 0
        while tries < 100 and (status.status not in [StatusCode.failed, StatusCode.dismissed, StatusCode.successful]):
            sleep(1)
            tries = tries + 1
            status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        self.assertEqual(status.status, StatusCode.dismissed, status.message)

        # test 2 : cancell while it's running
        r = self.send_download_request(InputDownloadProcess(requests=[{"collection": COLLECTION, "item_id": ID}], crop_wkt="", target_format=AssetFormat.jpg2000.value, target_projection="EPSG:27572", raw_archive=False))
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        tries = 0
        while tries < 100 and (status.status not in [StatusCode.running, StatusCode.failed, StatusCode.dismissed, StatusCode.successful]):
            sleep(1)
            tries = tries + 1
            status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID, "cancel"])).content))
        tries = 0
        while tries < 100 and (status.status not in [StatusCode.failed, StatusCode.dismissed, StatusCode.successful]):
            sleep(1)
            tries = tries + 1
            status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        self.assertEqual(status.status, StatusCode.dismissed, status.message)

    def send_download_request(self, inputs: InputDownloadProcess):
        execute = Execute(inputs=inputs.model_dump())
        r = requests.post("/".join([APROC_ENDPOINT, "processes/download/execution"]), data=json.dumps(execute.model_dump()), headers={"Content-Type": "application/json", "Authorization": TOKEN})
        self.assertTrue(r.ok)
        return r

    def get_result(self, status: StatusInfo):
        # GET RESULT (and file location)
        result = requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID, "results"]))
        print("result: {}".format(result.content))
        self.assertTrue(result.ok, result.status_code)
        result: OutputDownloadProcess = OutputDownloadProcess(**json.loads(result.content))
        return result

    def wait_for_success(self, status: StatusInfo):
        while status.status not in [StatusCode.failed, StatusCode.dismissed, StatusCode.successful]:
            sleep(1)
            status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        self.assertEqual(status.status, StatusCode.successful, status.message)
        return status

    def __add_item__(self, item_path: str, id: str) -> Item:
        print(f"create item {id}")
        with open(item_path, 'r') as file:
            data = file.read()
            r = requests.post(url=os.path.join(AIRS_URL, "collections", COLLECTION, "items"), data=data, headers={"Content-Type": "application/json"})
            self.assertTrue(r.ok, msg=r.content)
        print("item created")
        r = requests.get(url=os.path.join(AIRS_URL, "collections", COLLECTION, "items", id))
        self.assertTrue(r.ok, msg=r.content)
        return mapper.item_from_json(r.content)


if __name__ == '__main__':
    unittest.main()
