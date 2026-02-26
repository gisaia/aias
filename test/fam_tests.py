import json
import os
import unittest
from test.utils import FAM_URL

import requests
from fastapi import status

from fam.core.model import Archive, File, PathRequest


class Tests(unittest.TestCase):
    URL = FAM_URL

    def setUp(self):
        ...

    def test_not_found(self):
        r = requests.get(url="/".join([Tests.URL, "root"]))
        root: File = File(**r.json())
        r = requests.post(url="/".join([Tests.URL, "files"]), data=PathRequest(path="/".join([root.path, "a_file_that_does_not_exist"])).model_dump_json(), headers={"Content-Type": "application/json"})
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND, r.content)

    def test_dot_dot_not_authorized(self):
        r = requests.post(url="/".join([Tests.URL, "files"]), data=PathRequest(path="toto/../titi").model_dump_json(exclude_none=True, exclude_unset=True), headers={"Content-Type": "application/json"})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST, r.content)

    def test_directory(self):
        r = requests.get(url="/".join([Tests.URL, "root"]))
        root: File = File(**r.json())
        r = requests.post(url="/".join([Tests.URL, "files"]), data=PathRequest(path="/".join([root.path, "images"])).model_dump_json(), headers={"Content-Type": "application/json"})
        self.assertTrue(r.ok, str(r.status_code) + ": " + str(r.content))

    def test_archive(self):
        r = requests.get(url="/".join([Tests.URL, "root"]))
        root: File = File(**r.json())
        r = requests.post(url="/".join([Tests.URL, "archives"]), data=PathRequest(path="/".join([root.path, "images"])).model_dump_json(), headers={"Content-Type": "application/json"})
        self.assertTrue(r.ok, str(r.status_code) + ": " + str(r.content))
        archive = Archive(**(json.loads(r.content)[0]))
        self.assertTrue(archive.path.startswith("/inputs/images/") or archive.path.startswith("http://minio:9000/archives/inputs/images/") or archive.path.startswith("gs://gisaia-public/test-aias/images/"))
        self.assertFalse(archive.is_dir)
        self.assertEqual(archive.driver_name, "tiff")
        self.assertGreater(archive.last_modification_date.timestamp(), 0)
        self.assertGreater(archive.creation_date.timestamp(), 0)

if __name__ == '__main__':
    unittest.main()
