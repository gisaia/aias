import json
import requests
import unittest
import os
import boto3 as boto3
import elasticsearch
from aeoprs.core.settings import Configuration
import aeoprs.core.s3 as s3
import aeoprs.core.product_registration as rs
import boto3 as boto3
from aeoprs.core.models import mapper as mapper

AEOPRS_URL="http://127.0.0.1:8000"
COLLECTION="digitalearth.africa"
ID="077cb463-1f68-5532-aa8b-8df0b510231a"
ASSET="classification"
ASSET_PATH="test/inputs/ESA_WorldCover_10m_2021_v200_N15E000_Map.tif"
ITEM_PATH="test/inputs/077cb463-1f68-5532-aa8b-8df0b510231a.json"

class Tests(unittest.TestCase):

    def setUp(self):
        Configuration.init(configuration_file="test/conf/aeoprs.yaml")
        es = elasticsearch.Elasticsearch(Configuration.settings.index.endpoint_url)
        try:
            # Clean the index
            es.indices.delete(index=Configuration.settings.index.collection_prefix+"_"+COLLECTION)
        except Exception:
            ...
        try:
            # Clean the bucket
            objects=s3.get_client().list_objects(Bucket=Configuration.settings.s3.bucket, Prefix=rs.get_assets_relative_path(COLLECTION, ID))
            for object in objects["Contents"]:
                objects=s3.get_client().delete_object(Bucket=Configuration.settings.s3.bucket, Key=object["Key"])
            s3.get_client().delete_object(Bucket=Configuration.settings.s3.bucket, Key=rs.get_item_relative_path(COLLECTION, ID))
        except Exception as e:
            print(e)
            ...

    def test_not_found(self):
        # ADD ITEM FAIL BECAUSE ASSET MISSING
        with open(ITEM_PATH,'r') as file:
            data = file.read()
            r=requests.post(url=os.path.join(AEOPRS_URL,"collections",COLLECTION, "items"), data=data, headers={"Content-Type": "application/json"})
            self.assertFalse(r.ok,msg="Item registration did not fail")

        # ASSET NOT FOUND
        r=requests.head(url=os.path.join(AEOPRS_URL,"collections",COLLECTION, "items", ID, "assets", ASSET))
        self.assertFalse(r.ok,msg="Asset must not be found")

        # ITEM NOT FOUND
        r=requests.get(url=os.path.join(AEOPRS_URL,"collections",COLLECTION, "items", ID))
        self.assertFalse(r.ok,msg="Item must not be found")

    def test_upload(self):
        # UPLOAD ASSET
        file = {'file': (ASSET, open(ASSET_PATH, 'rb'), "image/tiff")}
        r=requests.post(url=os.path.join(AEOPRS_URL,"collections",COLLECTION, "items", ID, "assets", ASSET), files=file)
        self.assertTrue(r.ok,msg="Asset upload")

        # ASSET FOUND
        r=requests.head(url=os.path.join(AEOPRS_URL,"collections",COLLECTION, "items", ID, "assets", ASSET))
        self.assertTrue(r.ok,msg="Asset not found")


    def test_add_item(self):
        # ADD ITEM
        self.test_upload()
        with open(ITEM_PATH,'r') as file:
            data = file.read()
            r=requests.post(url=os.path.join(AEOPRS_URL,"collections",COLLECTION, "items"), data=data, headers={"Content-Type": "application/json"})
            self.assertTrue(r.ok,msg="Item registration")

        # ITEM FOUND
        r=requests.get(url=os.path.join(AEOPRS_URL,"collections",COLLECTION, "items", ID))
        self.assertTrue(r.ok,msg="Item must not found")

    def test_access_asset(self):
        # ADD ITEM
        self.test_upload()
        with open(ITEM_PATH,'r') as file:
            data = file.read()
            r=requests.post(url=os.path.join(AEOPRS_URL,"collections",COLLECTION, "items"), data=data, headers={"Content-Type": "application/json"})
            self.assertTrue(r.ok,msg="Item registration")

        # FILE FOUND FOR THE MANAGED ASSET
        r=requests.get(url=os.path.join(AEOPRS_URL,"collections",COLLECTION, "items", ID))
        item=mapper.item_from_json(r.content)
        r=requests.head(url=item.assets["classification"].href)
        self.assertTrue(r.ok,msg="Asset found")


    def test_delete(self):
        self.test_add_item()

        # DELETE ITEM
        r=requests.delete(url=os.path.join(AEOPRS_URL,"collections",COLLECTION, "items", ID))
        self.assertTrue(r.ok,msg="Item must not found")

        # ITEM NOT FOUND
        r=requests.get(url=os.path.join(AEOPRS_URL,"collections",COLLECTION, "items", ID))
        self.assertFalse(r.ok,msg="Item must not be found")

        # ASSET NOT FOUND
        r=requests.head(url=os.path.join(AEOPRS_URL,"collections",COLLECTION, "items", ID, "assets", ASSET))
        self.assertFalse(r.ok,msg="Asset must not be found")

if __name__ == '__main__':
    unittest.main()
