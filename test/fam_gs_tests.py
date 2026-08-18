import unittest
from aias_common.access.file import File
from fam.core.model import PathRequest
from test.fam_tests import Tests as FAMTests
import requests

class Tests(FAMTests):

    def setUp(self):
        FAMTests.URL = "http://fam-gs-service:8005/arlas/fam"  # NOSONAR

if __name__ == '__main__':
    unittest.main()
