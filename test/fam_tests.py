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
        r = requests.get(url=os.path.join(Tests.URL, "root"))
        root: File = File(**r.json())
        r = requests.post(url=os.path.join(Tests.URL, "files"), data=PathRequest(path=os.path.join(root.path, "a_file_that_does_not_exist")).model_dump_json(), headers={"Content-Type": "application/json"})
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND, r.content)

    def test_dot_dot_not_authorized(self):
        r = requests.post(url=os.path.join(Tests.URL, "files"), data=PathRequest(path="toto/../titi").model_dump_json(exclude_none=True, exclude_unset=True), headers={"Content-Type": "application/json"})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST, r.content)

    def test_directory(self):
        r = requests.get(url=os.path.join(Tests.URL, "root"))
        root: File = File(**r.json())
        r = requests.post(url=os.path.join(Tests.URL, "files"), data=PathRequest(path=os.path.join(root.path, "DIMAP")).model_dump_json(), headers={"Content-Type": "application/json"})
        self.assertTrue(r.ok, str(r.status_code) + ": " + str(r.content))

    def test_archive(self):
        r = requests.get(url=os.path.join(Tests.URL, "root"))
        root: File = File(**r.json())
        r = requests.post(url=os.path.join(Tests.URL, "archives"), data=PathRequest(path=os.path.join(root.path, "DIMAP")).model_dump_json(), headers={"Content-Type": "application/json"})
        self.assertTrue(r.ok, str(r.status_code) + ": " + str(r.content))
        archive = Archive(**(json.loads(r.content)[0]))
        self.assertEqual(archive.name, "IMG_SPOT6_MS_001_A")
        self.assertEqual(archive.path, os.path.join(root.path, "DIMAP/PROD_SPOT6_001/VOL_SPOT6_001_A/IMG_SPOT6_MS_001_A/"))
        self.assertTrue(archive.is_dir)
        self.assertIn(archive.id, ["148ddaaa431bdd2ff06b823df1e3725d462f668bd95188603bfff443ff055c71", "a75c9fc5a9fee985be7bd967ef713a20df65e7163f660bf6607436845fb48f4b", "9c74339d7d73e441e61d1b61b660d92713a163f3c212bf7dca261e4bc1e03601"])
        self.assertEqual(archive.driver_name, "dimap")

if __name__ == '__main__':
    unittest.main()
