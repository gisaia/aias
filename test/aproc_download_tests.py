import json
import os
import unittest
from test.utils import (AIRS_URL, APROC_ENDPOINT, ARLAS_COLLECTION, ARLAS_URL,
                        COLLECTION, ID, ITEM_PATH, BBOX,
                        SMTP_SERVER, TOKEN, index_collection_prefix, setUpTest)
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
        self.__add_item__()
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

    def test_download_project_native_format_native_nocrop(self):
        r = self.send_download_request(InputDownloadProcess(requests=[{"collection": COLLECTION, "item_id": ID}], crop_wkt="", target_format="native", target_projection="native", raw_archive=False))
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        status = self.wait_for_success(status)
        result = self.get_result(status)
        # FILE MUST EXISTS
        os.path.exists("./" + result.download_locations[0] + "/ESA_WorldCover_10m_2021_v200_N15E000_Map.tif")
        os.path.exists("./" + result.download_locations[0] + "/ESA_WorldCover_10m_2021_v200_N15E000_Map.tfw")

        # MAILS HAVE BEEN SENT
        r = requests.get(SMTP_SERVER + "?page=1&pageSize=30", headers={'Accept': 'application/json, text/plain, */*'})
        self.assertTrue(r.ok, r.status_code)
        self.assertEqual(len(r.json()["results"]), 8)

    def test_download_project_3857_format_jpeg2000_crop(self):
        r = self.send_download_request(InputDownloadProcess(requests=[{"collection": COLLECTION, "item_id": ID}], crop_wkt=BBOX, target_format=AssetFormat.jpg2000.value, target_projection="EPSG:27572", raw_archive=False))
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        status = self.wait_for_success(status)
        result = self.get_result(status)
        # FILE MUST EXISTS
        os.path.exists("./" + result.download_locations[0])

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

    def __add_item__(self) -> Item:
        print("create item")
        with open(ITEM_PATH, 'r') as file:
            data = file.read()
            r = requests.post(url=os.path.join(AIRS_URL, "collections", COLLECTION, "items"), data=data, headers={"Content-Type": "application/json"})
            self.assertTrue(r.ok, msg=r.content)
        print("item created")
        r = requests.get(url=os.path.join(AIRS_URL, "collections", COLLECTION, "items", ID))
        self.assertTrue(r.ok, msg=r.content)
        return mapper.item_from_json(r.content)


if __name__ == '__main__':
    unittest.main()
