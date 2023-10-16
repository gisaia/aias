import datetime
import time
import os
import unicodedata
from extensions.aproc.proc.ingest.drivers.drivers import Drivers


class Fam():

    def list_archives(path: str):
        driver = Drivers.solve(path)
        if driver is not None:
            print(driver.name)
            print(driver.get_item_id(path))
        else:
            if os.path.isdir(path):
                for file in os.listdir(path):
                    Fam.list_archives(os.path.join(path, file))


Drivers.init('./conf/drivers.yaml')
Fam.list_archives(".")