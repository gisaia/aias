import unittest
from aias_common.access.file import File
from fam.core.model import PathRequest
from test.fam_tests import Tests as FAMTests
import requests

class Tests(FAMTests):

    def setUp(self):
        FAMTests.URL = "http://fam-gs-service:8005/arlas/fam"  # NOSONAR

    def test_identifier_are_the_same(self):
        r = requests.get(url="/".join([Tests.URL, "root"]))
        root: File = File(**r.json())
        r = requests.post(url="/".join([Tests.URL, "archives"]), data=PathRequest(path="/".join([root.path, "spacewill/superview"])).model_dump_json(), headers={"Content-Type": "application/json"})
        self.assertTrue(r.ok, str(r.status_code) + ": " + str(r.content))
        print(r.json())
        name_to_id = {}
        for item in r.json():
            name_to_id[item["name"]] = item["id"]
        r = requests.post(url="/".join([Tests.URL, "archives"]), data=PathRequest(path="/".join([root.path, "spacewill/superview/SPACEWILL_SUPERVIEW_TIFF_MANUAL_TASKING_SYNTHETIC"])).model_dump_json(), headers={"Content-Type": "application/json"})
        for item in r.json():
            self.assertEqual(item["id"], name_to_id[item["name"]])


if __name__ == '__main__':
    unittest.main()
