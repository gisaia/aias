from datetime import datetime
import json
import unittest
from extensions.aproc.proc.drivers.exceptions import DriverException
from test.utils import ID, ID_MANAGED, s3_access_key, s3_access_key_id, s3_bucket, s3_endpoint_url, s3_region, index_collection_prefix, index_endpoint_url, COLLECTION
import elasticsearch


class TimedTests(unittest.TestCase):
    def setUp(self):
        self.tick = datetime.now()

    def tearDown(self):
        self.tock = datetime.now()
        diff = self.tock - self.tick
        print(f"Test {self._testMethodName} took {diff.total_seconds()}s")


class AprocTests(TimedTests):

    def get_client(self):
        from boto3 import Session
        session = Session(
                aws_access_key_id=s3_access_key_id,
                aws_secret_access_key=s3_access_key,
                region_name=s3_region)
        return session.client("s3", endpoint_url=s3_endpoint_url)

    def setUpESandMinio(self):
        import airs.core.product_registration as rs
        es = elasticsearch.Elasticsearch(index_endpoint_url)
        for collection in [COLLECTION, "collection1", "collection2", "collection3"]:
            try:
                # Clean the index
                es.indices.delete(index=index_collection_prefix + "_" + collection)
            except Exception as e:
                ...
            try:
                objects = self.get_client().list_objects(Bucket=s3_bucket, Prefix=collection)
                for object in objects["Contents"]:
                    self.get_client().delete_object(Bucket=s3_bucket, Key=object["Key"])
                self.get_client().delete_object(Bucket=s3_bucket, Key=rs.get_item_relative_path(collection, ID))
            except Exception as e:
                ...

    def setUp(self):
        super().setUp()
        self.setUpESandMinio()

    def tearDown(self):
        super().tearDown()
