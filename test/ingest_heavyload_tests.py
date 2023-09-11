import requests
import os
import json
from aeoprs.core.settings import Configuration as AEOPRSConfiguration
from aeoprocesses.ingest.drivers.drivers import Drivers
from aeoprocesses.ingest.ingest_services import ProcServices, TaskState
import aeoprs.core.product_registration as rs
import aeoprs.core.s3 as s3
from service_tests import COLLECTION
from celery import states
import time
import unittest
import boto3 as boto3
import elasticsearch

BATCH_SIZE = 1000
class Tests(unittest.TestCase):

    def setUp(self):
        ProcServices.init(os.environ.get("AEOPROCESSES_CONFIGURATION_FILE"))
        AEOPRSConfiguration.init(configuration_file="test/conf/aeoprs.yaml")
        es = elasticsearch.Elasticsearch(AEOPRSConfiguration.settings.index.endpoint_url)
        try:
            # Clean the index
            es.indices.delete(index=AEOPRSConfiguration.settings.index.collection_prefix+"_"+COLLECTION)
        except Exception:
            ...
        try:
            # Clean the bucket
            objects=s3.get_client().list_objects(Bucket=AEOPRSConfiguration.settings.s3.bucket, Prefix=COLLECTION)
            for object in objects["Contents"]:
                s3.get_client().delete_object(Bucket=AEOPRSConfiguration.settings.s3.bucket, Key=object["Key"])
        except Exception as e:
            print(e)
            ...

    def test_async_ingest_theia(self):

        start = time.time()
        r = requests.get("https://catalogue.theia-land.fr/arlas/explore/theia/_search?f=metadata.ObservationContext.processusUsed.platform_fr%3Aeq%3ASENTINEL%202&f=metadata.core.description.processingLevel_fr%3Aeq%3ANIVEAU%202A&include=data.metadata.core.identity.identifier&righthand=false&pretty=false&flat=false&&&size={}&max-age-cache=120".format(BATCH_SIZE), verify=False)
        self.assertTrue(r.ok)
        hits=json.loads(r.content)["hits"]
        task_id=None
        print("submitting {} archives".format(BATCH_SIZE))
        for hit in hits:
            url="https://catalogue.theia-land.fr/arlas/explore/theia/_search?f=metadata.core.identity.identifier%3Aeq%3A{}&righthand=false&pretty=false&flat=false&&&size=1&max-age-cache=120".format(hit["md"]["id"])
            task_id=ProcServices.async_register(url)
        end = time.time()
        print("{} archives submitted in {} s".format(BATCH_SIZE, end - start))

        start = time.time()
        ts:TaskState=ProcServices.get_state(task_id=task_id)
        while ts.state not in [states.SUCCESS, states.FAILURE, states.REJECTED, states.REVOKED, states.IGNORED, states.EXCEPTION_STATES]:
            time.sleep(1)
            ts:TaskState=ProcServices.get_state(task_id=task_id)
        end = time.time()
        print("{} archives registered in {} s".format(BATCH_SIZE, end - start))
        print("Checking that the {} archives are registered ...".format(BATCH_SIZE))
        for hit in hits:
            url="http://localhost:8000/collections/main_catalog/items/{}".format(hit["md"]["id"])
            r = requests.get(url)
            self.assertTrue(r.ok, url+" not found")


if __name__ == '__main__':
    unittest.main()
