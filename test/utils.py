import elasticsearch
from boto3 import Session
import aeoprs.core.product_registration as rs
import os


index_collection_prefix = os.getenv("ARLASEO_INDEX_COLLECTION_PREFIX","arlaseotest")
s3_access_key_id = os.getenv("ARLASEO_S3_ACCESS_KEY_ID","arlaseo")
s3_access_key = os.getenv("ARLASEO_S3_SECRET_ACCESS_KEY","arlaseosecret")
s3_region = os.getenv("ARLASEO_S3_REGION","None")
s3_bucket = os.getenv("ARLASEO_S3_BUCKET","arlaseotest")

index_endpoint_url = "http://localhost:9200"
s3_endpoint_url = "http://localhost:9000"
AEOPRS_URL="http://127.0.0.1:8000"
COLLECTION="digitalearth.africa"
ID="077cb463-1f68-5532-aa8b-8df0b510231a"
ASSET="classification"
ASSET_PATH="test/inputs/ESA_WorldCover_10m_2021_v200_N15E000_Map.tif"
ITEM_PATH="test/inputs/077cb463-1f68-5532-aa8b-8df0b510231a.json"


def get_client():
    session = Session(
            aws_access_key_id=s3_access_key_id,
            aws_secret_access_key=s3_access_key,
            region_name=s3_region)
    return session.client("s3", endpoint_url=s3_endpoint_url)


def setUpTest():
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
        ...