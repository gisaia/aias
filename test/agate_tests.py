import json
import os
import unittest

import requests
from utils import (AGATE_ENDPOINT, AIRS_URL, ARLAS_COLLECTION, ARLAS_URL,
                   ASSET, ASSET_PATH, COLLECTION, ID, ITEM_PATH, setUpTest)

from airs.core.models import mapper
from airs.core.models.model import Item


class Tests(unittest.TestCase):

    def setUp(self):
        setUpTest()
        try:
            requests.delete("/".join([ARLAS_URL, "arlas", "collections", ARLAS_COLLECTION]))
        except Exception:
            ...
        self.__add_item__()
        r = requests.put("/".join([ARLAS_URL, "arlas", "collections", ARLAS_COLLECTION]),  headers={"Content-Type": "application/json"}, data=json.dumps({
              "index_name": ARLAS_COLLECTION,
              "id_path": "id",
              "geometry_path": "geometry",
              "centroid_path": "centroid",
              "timestamp_path": "properties.datetime"
        }))
        self.assertTrue(r.ok, str(r.status_code)+" "+str(r.content))

    def test_download(self):
        # SEND DOWNLOAD REQUEST
        r = requests.get("/".join([AGATE_ENDPOINT, "collections", ARLAS_COLLECTION, "items", ID, "assets", ASSET]))
        self.assertTrue(r.ok, str(r.status_code)+" "+str(r.content))
        r = requests.get("/".join([AGATE_ENDPOINT, "collections", ARLAS_COLLECTION, "items", ID+"SHOULDNOTBEFOUND", "assets", ASSET]))
        self.assertFalse(r.ok, str(r.status_code)+" "+str(r.content))

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
