import unittest
from os import path

import requests

AIRS_URL = "http://127.0.0.1:8000"


class Tests(unittest.TestCase):

    def test_conformance(self):
        r = requests.get(url=path.join(AIRS_URL, "conformance"))
        self.assertTrue(r.ok)

    def test_jobs(self):
        ...

    def test_landing_page(self):
        r = requests.get(url=AIRS_URL)
        self.assertTrue(r.ok)

    def test_processes(self):
        # GET /processes
        r = requests.get(url=path.join(AIRS_URL, "processes"))
        self.assertTrue(r.ok)
        print(r.json())


if __name__ == '__main__':
    unittest.main()
