import json
import unittest
import elasticsearch
import os
import time
import unicodedata

import requests
from aias_common.access.manager import AccessManager
from airs.core.models import mapper
from airs.core.models.model import Item, MimeType
from extensions.aproc.proc.drivers.driver_manager import DriverManager
from extensions.aproc.proc.ingest.settings import Configuration as IngestConfiguration
from extensions.aproc.proc.ingest.ingest_process import summary
from aproc.core.settings import Configuration as AprocConfiguration


index_collection_prefix = os.getenv("AIRS_INDEX_COLLECTION_PREFIX", "airs")
s3_access_key_id = os.getenv("AIRS_S3_ACCESS_KEY_ID", "airs")
s3_access_key = os.getenv("AIRS_S3_SECRET_ACCESS_KEY", "airssecret")
s3_region = os.getenv("AIRS_S3_REGION", "None")
s3_bucket = os.getenv("AIRS_S3_BUCKET", "airstest")
s3_download_bucket = os.getenv("DOWNLOAD_S3_BUCKET", "downloads")

index_endpoint_url = "http://elasticsearch:9200"
s3_endpoint_url = "http://minio:9000"
AIRS_URL = "http://airs-server:8000/arlas/airs"
FAM_URL = "http://fam-service:8005/arlas/fam"
ARLAS_URL = "http://arlas-server:9999"
APROC_ENDPOINT = os.getenv("APROC_ENDPOINT", "http://aproc-service:8001/arlas/aproc")
AGATE_ENDPOINT = os.getenv("AGATE_ENDPOINT", "http://agate:8004/arlas/agate/authorization")
SMTP_SERVER = "http://smtp4dev:80/api/Messages"
COLLECTION = "digitalearth.africa"
CATALOG = "tests"
ARLAS_COLLECTION = "digitalearth.africa"
ID = "077cb463-1f68-5532-aa8b-8df0b510231a"
ID_MANAGED = "077cb463-1f68-5532-aa8b-8df0b510231a_managed"
ASSET = "data"
ASSET_NAME = "ESA_WorldCover_10m_2021_v200_N15E000_Map"
ASSET_PATH = f"test/inputs/{ASSET_NAME}.tif"
ITEM_PATH = f"test/inputs/{ID}.json"
ITEM_PATH_MANAGED = f"test/inputs/{ID_MANAGED}.json"
TOKEN = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIyMWU3ZDI3ZC05MWM4LTRjYTEtOGU4My04MWI1ODBkOTZkMDUiLCJodHRwOi8vYXJsYXMuaW8vbG9jYWxlIjoiZW4iLCJpc3MiOiJhcmxhcy5jcnRzLXN0YWZmLmxvY2FsIiwiZXhwIjoxNjk2ODYxMTU4LCJodHRwOi8vYXJsYXMuaW8vdGltZXpvbmUiOiJFdXJvcGUvUGFyaXMiLCJpYXQiOjE2OTY4NjEwOTgsImVtYWlsIjoidGVjaEBnaXNhaWEuY29tIn0.bonAysbuUeqU3gWVjA7H-WXGI-JXGAgbZNDyWfiq4VY"

BBOX = "Polygon ((0.56676570458404063 17.18722410865874295, 1.71124787775891329 17.2246604414261455, 1.6631154499151104 16.48128183361629695, 0.49189303904923587 16.49197792869269819, 0.49189303904923587 16.49197792869269819, 0.56676570458404063 17.18722410865874295))"

SENTINEL_2_ID = "e3229ea8-a7f8-4c88-a3ca-265cea2f6862"
SENTINEL_2_ITEM = f"test/inputs/{SENTINEL_2_ID}.json"

MINIO_ID = "a250b154-5080-4939-be2f-3baf6a386dab"
MINIO_ITEM = f"test/inputs/{MINIO_ID}.json"

CLOUD_ID = "619d7a94-c85e-4e6d-938c-50a043b51036"
CLOUD_ITEM = f"test/inputs/{CLOUD_ID}.json"

EPSG_27572 = "EPSG:27572"
MAX_ITERATIONS = 600

AprocConfiguration.init(configuration_file='conf/aproc.yaml')
AccessManager.init(AprocConfiguration.settings.access_manager)
IngestConfiguration.init(configuration_file='./conf/drivers.yaml')
DriverManager.init(summary.id, IngestConfiguration.settings.drivers)


def get_client():
    from boto3 import Session
    session = Session(
            aws_access_key_id=s3_access_key_id,
            aws_secret_access_key=s3_access_key,
            region_name=s3_region)
    return session.client("s3", endpoint_url=s3_endpoint_url)


def setUpTest():
    import airs.core.product_registration as rs
    es = elasticsearch.Elasticsearch(index_endpoint_url)
    try:
        # Clean the index
        es.indices.delete(index=index_collection_prefix+"_"+COLLECTION)
    except Exception:
        ...
    try:
        # Clean the bucket
        objects = get_client().list_objects(Bucket=s3_bucket, Prefix=rs.get_assets_relative_path(COLLECTION, ID))
        for object in objects["Contents"]:
            get_client().delete_object(Bucket=s3_bucket, Key=object["Key"])
        get_client().delete_object(Bucket=s3_bucket, Key=rs.get_item_relative_path(COLLECTION, ID))
    except Exception as e:
        print(e)


def dir_to_list(dirname, parent={}):
    data = []
    for name in [unicodedata.normalize('NFC', f) for f in os.listdir(dirname)]:
        dct = {}
        if not name.startswith('.'):
            dct['name'] = name
            dct['path'] = os.path.join(dirname, name)
            dct['modification_time'] = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(os.stat(dct['path']).st_mtime))
            if os.path.isfile(dct['path']):
                driver = DriverManager.solve(summary.id, dct['path'])
                if driver is not None:
                    dct['type'] = 'file'
                    dct["archive"] = True
                    dct["id"] = driver.get_item_id(dct['path'])
                    dct["archive_type"] = driver.name
            if os.path.isdir(dct['path']):
                driver = DriverManager.solve(summary.id, dct['path'])
                if driver is not None:
                    dct['type'] = 'folder'
                    dct["archive"] = True
                    dct["id"] = driver.get_item_id(dct['path'])
                    dct["archive_type"] = driver.name
                else:
                    dct['type'] = 'folder'
                    dct['children'] = dir_to_list(dct['path'], parent=dct)
            data.append(dct)
    return data


def filter_data(arr):
    def filter_condition(a):
        if 'type' in a:
            if a['type'] == 'folder':
                if 'children' in a and len(a['children']) > 0:
                    return True
                if 'children' in a and len(a['children']) == 0:
                    return False
                if a['archive']:
                    return True
            if a['type'] == 'file' and a['archive'] is True:
                return True
        else:
            return False

    def func(item):
        item = dict(item)
        if 'children' in item:
            item['children'] = filter_data(item['children'])
        return item
    return list(map(func, list(filter(filter_condition, arr))))


def add_item(calling_test: unittest.TestCase, item_path: str, id: str) -> Item:
    print(f"create item {id}")
    with open(item_path, 'r') as file:
        data = file.read()
        r = requests.post(url="/".join([AIRS_URL, "collections", COLLECTION, "items"]), data=data, headers={"Content-Type": "application/json"})
        calling_test.assertTrue(r.ok, msg=r.content)
    print("item created")
    r = requests.get(url="/".join([AIRS_URL, "collections", COLLECTION, "items", id]))
    calling_test.assertTrue(r.ok, msg=r.content)
    return mapper.item_from_json(r.content)


def create_arlas_collection(calling_test: unittest.TestCase):
    print(f"Creating collection {ARLAS_COLLECTION}")
    r = requests.put("/".join([ARLAS_URL, "arlas", "collections", ARLAS_COLLECTION]), headers={"Content-Type": MimeType.JSON.value},
                     data=json.dumps({
                        "index_name": index_collection_prefix + "_" + ARLAS_COLLECTION,
                        "id_path": "id",
                        "geometry_path": "geometry",
                        "centroid_path": "centroid",
                        "timestamp_path": "properties.datetime"
                     }))
    calling_test.assertTrue(r.ok, str(r.status_code) + " " + str(r.content))
    print("Collection created")
