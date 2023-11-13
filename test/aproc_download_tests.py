import unittest
import os
from time import sleep
import requests
import json
from airs.core.models import mapper
from airs.core.models.model import Item, Asset, Role
from aproc.core.models.ogc.process import ProcessList, ProcessDescription
from extensions.aproc.proc.download.download_process import InputDownloadProcess, OutputDownloadProcess

from utils import AIRS_URL, APROC_ENDPOINT, ARLAS_COLLECTION, ARLAS_URL, TOKEN, setUpTest

from aproc.core.models.ogc.job import StatusCode, StatusInfo
from aproc.core.models.ogc import (Execute)
from utils import setUpTest, index_endpoint_url, ITEM_PATH, AIRS_URL, COLLECTION, ID, ASSET, ASSET_PATH, SMTP_SERVER, \
    index_collection_prefix


class Tests(unittest.TestCase):

    def setUp(self):
        setUpTest()
        requests.delete(SMTP_SERVER+"/*")

    def test_download(self):
        # CHECK THE DOWNLOAD PROCESS EXISTS
        r = requests.get("/".join([APROC_ENDPOINT, "processes"]))
        self.assertTrue(r.ok)
        print(r.content)
        processes: ProcessList = ProcessList(**json.loads(r.content))
        self.assertGreater(len(processes.processes), 0)
        self.assertIn("download", list(map(lambda p: p.id, processes.processes)))

        # SEND INCORRECT DOWNLOAD REQUEST (no item yet)
        inputs = InputDownloadProcess(requests=[{"collection": COLLECTION, "item_id":ID}], crop_wkt="", target_format="", target_projection="")
        execute = Execute(inputs=inputs.model_dump())
        r = requests.post("/".join([APROC_ENDPOINT, "processes/download/execution"]), data=json.dumps(execute.model_dump()), headers={"Content-Type": "application/json", "Authorization": TOKEN})
        print(execute.model_dump_json())
        self.assertFalse(r.ok, str(r.status_code) + ": " + str(r.content))
        # REQUEST MAILS AND ERROR MAILS HAVE BEEN SENT
        r = requests.get(SMTP_SERVER+"?page=1&pageSize=30", headers={'Accept': 'application/json, text/plain, */*'})
        self.assertTrue(r.ok, r.status_code)
        self.assertEqual(len(r.json()["results"]), 3)

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
        self.assertTrue(r.ok, str(r.status_code)+" "+str(r.content))

        # SEND DOWNLOAD REQUEST
        inputs = InputDownloadProcess(requests=[{"collection": COLLECTION, "item_id":ID}, {"collection": COLLECTION, "item_id":ID}], crop_wkt="", target_format="", target_projection="")
        execute = Execute(inputs=inputs.model_dump())
        r = requests.post("/".join([APROC_ENDPOINT, "processes/download/execution"]), data=json.dumps(execute.model_dump()), headers={"Content-Type": "application/json", "Authorization": TOKEN})
        self.assertTrue(r.ok)

        # WAIT FOR SUCCESS
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        while status.status not in [StatusCode.failed, StatusCode.dismissed, StatusCode.successful]:
            sleep(1)
            status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        self.assertEqual(status.status, StatusCode.successful)

        # GET RESULT (and file location)
        result = requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID, "results"]))
        print("result: {}".format(result.content))
        self.assertTrue(result.ok, result.status_code)
        result: OutputDownloadProcess = OutputDownloadProcess(**json.loads(result.content))
        # FILE MUST EXISTS
        os.path.exists("./"+result.download_locations[0])

        # MAILS HAVE BEEN SENT
        r = requests.get(SMTP_SERVER+"?page=1&pageSize=30", headers={'Accept': 'application/json, text/plain, */*'})
        self.assertTrue(r.ok, r.status_code)
        self.assertEqual(len(r.json()["results"]), 11)

    def __add_item__(self) -> Item:
        print("create item")
        # UPLOAD ASSET
        with open(ASSET_PATH, 'rb') as file:
            file = {'file': (ASSET, file, "image/tiff")}
            requests.post(url=os.path.join(AIRS_URL, "collections", COLLECTION, "items", ID, "assets", ASSET), files=file)
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
