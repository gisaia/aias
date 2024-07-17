import json
import os
import unittest
from test.utils import FAM_URL

import requests
from fastapi import status

from fam.core.model import Archive, File, PathRequest


class Tests(unittest.TestCase):

    def setUp(self):
        ...

    def test_not_found(self):
        r = requests.get(url=os.path.join(FAM_URL, "root"))
        print(r.content)
        root: File = File(**r.json())
        r = requests.post(url=os.path.join(FAM_URL, "files"), data=PathRequest(path=root.path + "/a_file_that_does_not_exist").model_dump_json(), headers={"Content-Type": "application/json"})
        self.assertEquals(r.status_code, status.HTTP_404_NOT_FOUND, r.content)

    def test_dot_dot_not_authorized(self):
        r = requests.post(url=os.path.join(FAM_URL, "files"), data=PathRequest(path="toto/../titi").model_dump_json(), headers={"Content-Type": "application/json"})
        self.assertEquals(r.status_code, status.HTTP_400_BAD_REQUEST, r.content)

    def test_directory(self):
        r = requests.get(url=os.path.join(FAM_URL, "root"))
        root: File = File(**r.json())
        r = requests.post(url=os.path.join(FAM_URL, "files"), data=PathRequest(path=root.path + "/DIMAP").model_dump_json(), headers={"Content-Type": "application/json"})
        self.assertTrue(r.ok, str(r.status_code) + ": " + str(r.content))

    def test_archive(self):
        r = requests.get(url=os.path.join(FAM_URL, "root"))
        root: File = File(**r.json())
        r = requests.post(url=os.path.join(FAM_URL, "archives"), data=PathRequest(path=root.path + "/DIMAP").model_dump_json(), headers={"Content-Type": "application/json"})
        self.assertTrue(r.ok, str(r.status_code) + ": " + str(r.content))
        archive = Archive(**(json.loads(r.content)[0]))
        print(archive.model_dump_json())
        self.assertEquals(archive.name, "IMG_SPOT6_MS_001_A")
        self.assertEquals(archive.path, root.path + "/DIMAP/PROD_SPOT6_001/VOL_SPOT6_001_A/IMG_SPOT6_MS_001_A")
        self.assertEquals(archive.is_dir, True)
        self.assertEquals(archive.id, "3c3207184afc7982192f8185bbbd78b98705c4b46307d786107ea3715d47c900")
        self.assertEquals(archive.driver_name, "dimap")


if __name__ == '__main__':
    unittest.main()
