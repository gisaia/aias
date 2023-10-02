from aproc.core.models.ogc import Execute
from extensions.aproc.proc.ingest.drivers.drivers import Drivers
from extensions.aproc.proc.ingest.ingest_process import InputIngestProcess
from utils import dir_to_list, filter_data
import requests
import os
APROC_ENDPOINT = os.getenv("APROC_ENDPOINT")
Drivers.init(os.getenv("DRIVERS_CONFIGURATION_FILE"))

def ingest(url, collection, catalog):
    inputs = InputIngestProcess(url=url, collection=collection, catalog=catalog)
    execute = Execute(inputs=inputs.model_dump())
    r = requests.post("/".join([APROC_ENDPOINT, "processes/ingest/execution"]), data=execute.model_dump_json(), headers={"Content-Type": "application/json"})

def ingest_folders(data,collection,catalog):
    for d in data:
        if 'archive' in d:
            print("Try to ingest : " + d['path'])
            ingest(d['path'], collection,catalog)
        else:
            if 'children' in d:
                ingest_folders(d['children'],collection,catalog)

url = os.getenv("INGESTED_FOLDER")
collection = os.getenv("COLLECTION")
catalog = os.getenv("CATALOG")
data = dir_to_list(url)
ingest_folders(filter_data(data),collection,catalog)