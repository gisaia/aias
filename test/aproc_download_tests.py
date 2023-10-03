import unittest
import os
from time import sleep
import requests
import json
from airs.core.models import mapper
from airs.core.models.model import Item, Asset, Role
from aproc.core.models.ogc.process import ProcessList, ProcessDescription
from extensions.aproc.proc.download.download_process import InputDownloadProcess, OutputDownloadProcess

from utils import AIRS_URL, APROC_ENDPOINT, setUpTest

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
        processes: ProcessList = ProcessList(**json.loads(r.content))
        self.assertGreater(len(processes.processes), 0)
        self.assertIn("download", list(map(lambda p: p.id, processes.processes)))

        # SEND INCORRECT DOWNLOAD REQUEST (no item yet)
        inputs = InputDownloadProcess(collection=COLLECTION, item_id=ID, asset_name=ASSET, crop_wkt="", target_format="", target_projection="")
        execute = Execute(inputs=inputs.model_dump())
        r = requests.post("/".join([APROC_ENDPOINT, "processes/download/execution"]), data=execute.model_dump_json(), headers={"Content-Type": "application/json", "arlas-user-email": "sylvain.gaudan@gisaia.com"})
        self.assertTrue(r.ok)
        # WAIT FOR FAILURE
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        while status.status not in [StatusCode.failed, StatusCode.dismissed, StatusCode.successful]:
            sleep(1)
            status: StatusInfo = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        self.assertEqual(status.status, StatusCode.failed)
        # ERROR MAILS HAVE BEEN SENT
        r = requests.get(SMTP_SERVER, headers={'Accept': 'application/json, text/plain, */*'})
        self.assertTrue(r.ok, r.status_code)
        self.assertEqual(len(r.json()["results"]), 2)

        self.__add_item__()
        # SEND DOWNLOAD REQUEST
        inputs = InputDownloadProcess(collection=COLLECTION, item_id=ID, asset_name=ASSET, crop_wkt="", target_format="", target_projection="")
        execute = Execute(inputs=inputs.model_dump())
        r = requests.post("/".join([APROC_ENDPOINT, "processes/download/execution"]), data=execute.model_dump_json(), headers={"Content-Type": "application/json", "arlas-user-email": "sylvain.gaudan@gisaia.com"})
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
        os.path.exists("./"+result.download_location)

        # MAILS HAVE BEEN SENT
        r = requests.get(SMTP_SERVER, headers={'Accept': 'application/json, text/plain, */*'})
        self.assertTrue(r.ok, r.status_code)
        self.assertEqual(len(r.json()["results"]), 4)

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
        return mapper.item_from_json(r.content)


if __name__ == '__main__':
    unittest.main()
