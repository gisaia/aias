from aeoprs.core.settings import Configuration as AEOPRSConfiguration
from aeoprocesses.ingest.drivers.drivers import Drivers
from aeoprocesses.ingest.ingest_services import ProcServices, TaskState
import aeoprs.core.product_registration as rs
import aeoprs.core.s3 as s3
from service_tests import COLLECTION
from celery import states
from time import sleep
import unittest
import boto3 as boto3
import elasticsearch


ID="SENTINEL2A_20230604-105902-526_L2A_T31TCJ_D"

class Tests(unittest.TestCase):

    def setUp(self):
        ProcServices.init("test/conf/aeoprocesses.yaml")
        AEOPRSConfiguration.init(configuration_file="test/conf/aeoprs.yaml")
        es = elasticsearch.Elasticsearch(AEOPRSConfiguration.settings.index.endpoint_url)
        try:
            # Clean the index
            es.indices.delete(index=AEOPRSConfiguration.settings.index.collection_prefix+"_"+COLLECTION)
        except Exception:
            ...
        try:
            # Clean the bucket
            objects=s3.get_client().list_objects(Bucket=AEOPRSConfiguration.settings.s3.bucket, Prefix=rs.get_assets_relative_path(COLLECTION, ID))
            for object in objects["Contents"]:
                s3.get_client().delete_object(Bucket=AEOPRSConfiguration.settings.s3.bucket, Key=object["Key"])
            s3.get_client().delete_object(Bucket=AEOPRSConfiguration.settings.s3.bucket, Key=rs.get_item_relative_path(COLLECTION, ID))
        except Exception as e:
            print(e)
            ...

    def test_async_ingest_theia(self):
        task_id=ProcServices.async_register("https://catalogue.theia-land.fr/arlas/explore/theia/_search?f=metadata.core.identity.identifier%3Aeq%3ASENTINEL2A_20230604-105902-526_L2A_T31TCJ_D&righthand=false&pretty=false&flat=false&&&size=1&max-age-cache=120")
        ts:TaskState=ProcServices.get_state(task_id=task_id)        
        while ts.state not in [states.SUCCESS, states.FAILURE, states.REJECTED, states.REVOKED, states.IGNORED, states.EXCEPTION_STATES]:
            print(ts.model_dump_json())
            sleep(1)
            ts:TaskState=ProcServices.get_state(task_id=task_id)
        self.assertTrue(ts.state==states.SUCCESS)
        self.assertTrue(ts.info["item"], "http://127.0.0.1:8000/collections/main_catalog/items/SENTINEL2A_20230604-105902-526_L2A_T31TCJ_D")        

    def test_sync_ingest_theia(self):
        r=ProcServices.sync_register("https://catalogue.theia-land.fr/arlas/explore/theia/_search?f=metadata.core.identity.identifier%3Aeq%3ASENTINEL2A_20230604-105902-526_L2A_T31TCJ_D&righthand=false&pretty=false&flat=false&&&size=1&max-age-cache=120")
        self.assertTrue(r["state"]==states.SUCCESS)
        self.assertTrue(r["item"], "http://127.0.0.1:8000/collections/main_catalog/items/SENTINEL2A_20230604-105902-526_L2A_T31TCJ_D")

    def test_sync_ingest_dimap(self):
        r=ProcServices.sync_register("/DIMAP/PROD_SPOT6_001/VOL_SPOT6_001_A/IMG_SPOT6_MS_001_A/")
        self.assertTrue(r["state"]==states.SUCCESS)

if __name__ == '__main__':
    unittest.main()
