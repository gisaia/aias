import json
import os
import unittest
from test.utils import FAM_URL
from test.fam_tests import Tests as FAMTests
import requests
from fastapi import status

from fam.core.model import Archive, File, PathRequest


class Tests(FAMTests):

    def setUp(self):
        FAMTests.URL = "http://fam-bucket-service:8005/arlas/fam"

if __name__ == '__main__':
    unittest.main()
