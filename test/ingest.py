from aproc.core.models.ogc import Execute
from extensions.aproc.proc.ingest.drivers.drivers import Drivers
from extensions.aproc.proc.ingest.ingest_process import InputIngestProcess
from utils import dir_to_list, filter_data
import requests
import os
import json
import csv

APROC_ENDPOINT = os.getenv("APROC_ENDPOINT")
DRY_RUN = os.getenv("DRY_RUN", True)
Drivers.init(os.getenv("DRIVERS_CONFIGURATION_FILE"))

def ingest(url, collection, catalog):
    inputs = InputIngestProcess(url=url, collection=collection, catalog=catalog, annotations="")
    execute = Execute(inputs=inputs.model_dump())
    r = requests.post("/".join([APROC_ENDPOINT, "processes/ingest/execution"]), data=json.dumps(execute.model_dump()),
                      headers={"Content-Type": "application/json"})

def ingest_folders(data, collection, catalog, writer):
    for d in data:
        if 'archive' in d:
            if str(DRY_RUN).lower() == "false":
                ingest(d['path'], collection, catalog)
            else:
                # Write a csv file with two columns path and id
                print("Try to ingest : " + d['path'] + " with id " + d['id'])
                row=[d['path'], d['id']]
                writer.writerow(row)
        else:
            if 'children' in d:
                ingest_folders(d['children'], collection, catalog, writer)


dir_to_list_data = dir_to_list(os.getenv("INGESTED_FOLDER"))
f = open(os.getenv("OUTPUT_FILE",'/tmp/result.csv'), 'w')
writer = csv.writer(f)
ingest_folders(filter_data(dir_to_list_data), os.getenv("COLLECTION"), os.getenv("CATALOG"), writer)
f.close()

