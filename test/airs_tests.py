import os
import unittest
from test.utils import (AIRS_URL, ASSET, ASSET_PATH, COLLECTION, ID_MANAGED, ITEM_PATH_MANAGED,
                        index_collection_prefix, index_endpoint_url, setUpTest)

import elasticsearch
import requests

from airs.core.models import mapper as mapper


class Tests(unittest.TestCase):

    def setUp(self):
        setUpTest()

    def test_not_found(self):
        # ADD ITEM FAIL BECAUSE ASSET MISSING
        with open(ITEM_PATH_MANAGED, 'r') as file:
            data = file.read()
            r = requests.post(url=os.path.join(AIRS_URL, "collections", COLLECTION, "items"), data=data, headers={"Content-Type": "application/json"})
            self.assertFalse(r.ok, str(r.status_code) + str(r.content))

        # ASSET NOT FOUND
        r = requests.head(url=os.path.join(AIRS_URL, "collections", COLLECTION, "items", ID_MANAGED, "assets", ASSET))
        self.assertEqual(r.status_code, 404, str(r.status_code) + str(r.content))

        # ITEM NOT FOUND
        r = requests.get(url=os.path.join(AIRS_URL, "collections", COLLECTION, "items", ID_MANAGED))
        self.assertEqual(r.status_code, 404, str(r.status_code) + str(r.content))

    def test_init_collection(self):
        # UPLOAD ASSET
        r = requests.post(url=os.path.join(AIRS_URL, "collections", COLLECTION, "_init"))
        self.assertTrue(r.ok, str(r.status_code) + str(r.content))

    def test_upload(self):
        # UPLOAD ASSET
        f = open(ASSET_PATH, 'rb')
        file = {'file': (ASSET, f, "image/tiff")}
        r = requests.post(url=os.path.join(AIRS_URL, "collections", COLLECTION, "items", ID_MANAGED, "assets", ASSET), files=file)
        self.assertTrue(r.ok, str(r.status_code) + str(r.content))
        f.close()
        # ASSET FOUND
        r = requests.head(url=os.path.join(AIRS_URL, "collections", COLLECTION, "items", ID_MANAGED, "assets", ASSET))
        self.assertTrue(r.ok, str(r.status_code) + str(r.content))

    def test_add_item(self):
        # ADD ITEM
        self.test_upload()
        with open(ITEM_PATH_MANAGED, 'r') as file:
            data = file.read()
            r = requests.post(url=os.path.join(AIRS_URL, "collections", COLLECTION, "items"), data=data, headers={"Content-Type": "application/json"})
            self.assertTrue(r.ok, str(r.status_code)+str(r.content))

        # ITEM FOUND
        r = requests.get(url=os.path.join(AIRS_URL, "collections", COLLECTION, "items", ID_MANAGED))
        self.assertTrue(r.ok, str(r.status_code) + str(r.content))

    def test_update_item(self):
        # ADD ITEM
        self.test_add_item()

        # UPDATE
        with open(ITEM_PATH_MANAGED, 'r') as file:
            data = file.read()
            r = requests.put(url=os.path.join(AIRS_URL, "collections", COLLECTION, "items", ID_MANAGED), data=data, headers={"Content-Type": "application/json"})
            self.assertTrue(r.ok, str(r.status_code)+str(r.content))

        # ITEM FOUND
        r = requests.get(url=os.path.join(AIRS_URL, "collections", COLLECTION, "items", ID_MANAGED))
        self.assertTrue(r.ok, str(r.status_code) + str(r.content))

    def test_access_asset(self):
        # ADD ITEM
        self.test_upload()
        with open(ITEM_PATH_MANAGED, 'r') as file:
            data = file.read()
            r = requests.post(url=os.path.join(AIRS_URL, "collections", COLLECTION, "items"), data=data, headers={"Content-Type": "application/json"})
            self.assertTrue(r.ok, str(r.status_code) + str(r.content))
        # FILE FOUND FOR THE MANAGED ASSET
        r = requests.get(url=os.path.join(AIRS_URL, "collections", COLLECTION, "items", ID_MANAGED))
        item = mapper.item_from_json(r.content)
        location = item.assets["data"].href
        r = requests.head(url=location)
        self.assertTrue(r.ok, str(r.status_code) + str(r.content))

    def test_delete(self):
        self.test_add_item()

        # DELETE ITEM
        r = requests.delete(url=os.path.join(AIRS_URL, "collections", COLLECTION, "items", ID_MANAGED))
        self.assertTrue(r.ok, str(r.status_code) + str(r.content))

        # ITEM NOT FOUND
        r = requests.get(url=os.path.join(AIRS_URL, "collections", COLLECTION, "items", ID_MANAGED))
        self.assertEqual(r.status_code, 404, str(r.status_code) + str(r.content))

        # ASSET NOT FOUND
        r = requests.head(url=os.path.join(AIRS_URL, "collections", COLLECTION, "items", ID_MANAGED, "assets", ASSET))
        self.assertEqual(r.status_code, 404, str(r.status_code) + str(r.content))

    def test_reindex(self):
        self.test_add_item()
        # REMOVE ITEM
        es = elasticsearch.Elasticsearch(index_endpoint_url)
        try:
            # Clean the index
            es.indices.delete(index=index_collection_prefix + "_" + COLLECTION)
        except Exception:
            ...
        # ITEM NOT FOUND
        r = requests.get(url=os.path.join(AIRS_URL, "collections", COLLECTION, "items", ID_MANAGED))
        self.assertEqual(r.status_code, 404, str(r.status_code) + str(r.content))

        # REINDEX
        r = requests.post(url=os.path.join(AIRS_URL, "collections", COLLECTION, "_reindex"), headers={"Content-Type": "application/json"})
        # ITEM FOUND
        r = requests.get(url=os.path.join(AIRS_URL, "collections", COLLECTION, "items", ID_MANAGED))
        self.assertTrue(r.ok, str(r.status_code) + str(r.content))


if __name__ == '__main__':
    unittest.main()
