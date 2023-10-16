import requests
import unittest
import os
from fam.core.model import PathRequest
from utils import setUpTest, index_endpoint_url, ITEM_PATH, FAM_URL, COLLECTION, ID, ASSET, ASSET_PATH, \
    index_collection_prefix
from fastapi import APIRouter, HTTPException, status


class Tests(unittest.TestCase):

    def setUp(self):
        ...

    def test_not_found(self):
        r=requests.post(url=os.path.join(FAM_URL, "files"), data=PathRequest(path="a_file_that_does_not_exist").model_dump_json(), headers={"Content-Type": "application/json"})
        self.assertEquals(r.status_code, status.HTTP_404_NOT_FOUND, r.content)

    def test_dot_dot_not_authorized(self):
        r=requests.post(url=os.path.join(FAM_URL, "files"), data=PathRequest(path="toto/../titi").model_dump_json(), headers={"Content-Type": "application/json"})
        self.assertEquals(r.status_code, status.HTTP_400_BAD_REQUEST, r.content)

    def test_directory(self):
        r=requests.post(url=os.path.join(FAM_URL, "files"), data=PathRequest(path="DIMAP").model_dump_json(), headers={"Content-Type": "application/json"})
        self.assertTrue(r.ok)

    def test_file(self):
        r=requests.post(url=os.path.join(FAM_URL, "files"), data=PathRequest(path="DIMAP/PROD_SPOT6_001").model_dump_json(), headers={"Content-Type": "application/json"})
        self.assertTrue(r.ok)


if __name__ == '__main__':
    unittest.main()
