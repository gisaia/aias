import elasticsearch
import os
import time
import unicodedata
from extensions.aproc.proc.ingest.drivers.drivers import Drivers

index_collection_prefix = os.getenv("AIRS_INDEX_COLLECTION_PREFIX","airs")
s3_access_key_id = os.getenv("AIRS_S3_ACCESS_KEY_ID","airs")
s3_access_key = os.getenv("AIRS_S3_SECRET_ACCESS_KEY","airssecret")
s3_region = os.getenv("AIRS_S3_REGION","None")
s3_bucket = os.getenv("AIRS_S3_BUCKET","airstest")

index_endpoint_url = "http://elasticsearch:9200"
s3_endpoint_url = "http://minio:9000"
AIRS_URL = "http://airs-server:8000/arlas/airs"
FAM_URL = "http://fam-service:8005/arlas/fam"
ARLAS_URL = "http://arlas-server:9999"
APROC_ENDPOINT = os.getenv("APROC_ENDPOINT", "http://aproc-service:8001/arlas/aproc")
AGATE_ENDPOINT = os.getenv("AGATE_ENDPOINT", "http://agate:8004/arlas/agate/authorization")
SMTP_SERVER="http://smtp4dev:80/api/Messages"
COLLECTION="digitalearth.africa"
CATALOG = "tests"
ARLAS_COLLECTION="digitalearth.africa"
ID="077cb463-1f68-5532-aa8b-8df0b510231a"
ID_MANAGED="077cb463-1f68-5532-aa8b-8df0b510231a_managed"
ASSET="data"
ASSET_PATH="test/inputs/ESA_WorldCover_10m_2021_v200_N15E000_Map.tif"
ITEM_PATH="test/inputs/077cb463-1f68-5532-aa8b-8df0b510231a.json"
ITEM_PATH_MANAGED="test/inputs/077cb463-1f68-5532-aa8b-8df0b510231a_managed.json"
TOKEN="Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIyMWU3ZDI3ZC05MWM4LTRjYTEtOGU4My04MWI1ODBkOTZkMDUiLCJodHRwOi8vYXJsYXMuaW8vbG9jYWxlIjoiZW4iLCJpc3MiOiJhcmxhcy5jcnRzLXN0YWZmLmxvY2FsIiwiZXhwIjoxNjk2ODYxMTU4LCJodHRwOi8vYXJsYXMuaW8vdGltZXpvbmUiOiJFdXJvcGUvUGFyaXMiLCJpYXQiOjE2OTY4NjEwOTgsImVtYWlsIjoidGVjaEBnaXNhaWEuY29tIn0.bonAysbuUeqU3gWVjA7H-WXGI-JXGAgbZNDyWfiq4VY"

BBOX = "Polygon ((0.56676570458404063 17.18722410865874295, 1.71124787775891329 17.2246604414261455, 1.6631154499151104 16.48128183361629695, 0.49189303904923587 16.49197792869269819, 0.49189303904923587 16.49197792869269819, 0.56676570458404063 17.18722410865874295))"

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
        objects=get_client().list_objects(Bucket=s3_bucket, Prefix=rs.get_assets_relative_path(COLLECTION, ID))
        for object in objects["Contents"]:
            get_client().delete_object(Bucket=s3_bucket, Key=object["Key"])
        get_client().delete_object(Bucket=s3_bucket, Key=rs.get_item_relative_path(COLLECTION, ID))
    except Exception as e:
        print(e)

Drivers.init('./conf/drivers.yaml')
def dir_to_list(dirname, parent={}):
    data = []
    for name in [unicodedata.normalize('NFC', f) for f in os.listdir(dirname)]:
        dct = {}
        if not name.startswith('.'):
            dct['name'] = name
            dct['path'] = os.path.join(dirname, name)
            dct['modification_time'] = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(os.stat(dct['path'] ).st_mtime))
            if os.path.isfile(dct['path']):
                driver = Drivers.solve(dct['path'])
                if driver is not None:
                    dct['type'] = 'file'
                    dct["archive"] = True
                    dct["id"]= driver.get_item_id(dct['path'])
                    dct["archive_type"] = driver.name
            if os.path.isdir(dct['path']):
                driver = Drivers.solve(dct['path'])
                if driver is not None:
                    dct['type'] = 'folder'
                    dct["archive"] = True
                    dct["id"]= driver.get_item_id(dct['path'])
                    dct["archive_type"] = driver.name
                else:
                    dct['type'] = 'folder'
                    dct['children'] = dir_to_list(dct['path'] ,parent=dct)
            data.append(dct)
    return data

def filter_data(arr):
    def filter_condition(a):
        if 'type' in a:
            if a['type'] == 'folder':
                if 'children' in a and len(a['children'])>0:
                    return True
                if 'children' in a and len(a['children'])==0:
                    return False
                if a['archive']:
                    return True
            if a['type'] == 'file' and a['archive'] == True:
                return True
        else:
            return False

    def func(item):
        item = dict(item)
        if 'children' in item:
            item['children'] = filter_data(item['children'])
        return item
    return list(map(func,list(filter(filter_condition, arr))))