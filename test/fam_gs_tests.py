import unittest
from test.fam_tests import Tests as FAMTests


class Tests(FAMTests):

    def setUp(self):
        FAMTests.URL = "http://fam-gs-service:8005/arlas/fam"  # NOSONAR


if __name__ == '__main__':
    unittest.main()
