from aeoprocesses.settings import Configuration
from aeoprocesses.ingest.drivers.drivers import Drivers
from aeoprocesses.ingest.drivers.driver import Driver
from aeoprocesses.ingest.drivers.exceptions import DriverException, RegisterException, ConnectionException
from aeoprs.core.models.model import Asset
from aeoprs.core.models.mapper import to_json, item_from_json
from celery import Celery
from celery.utils.log import get_task_logger
import requests
import os

LOGGER = get_task_logger(__name__)
LOGGER.debug(True)
LOGGER.propagate = True
Configuration.init(os.environ.get("AEOPROCESSES_CONFIGURATION_FILE"))
Drivers.init()

app = Celery(name='aeoprocesses', broker=Configuration.settings.celery_broker_url, backend=Configuration.settings.celery_result_backend)

def __update_status__(LOGGER, task, state:str, meta:dict=None):
    LOGGER.info(task.name+" "+state+" "+str(meta))
    if task.request.id is not None:
        task.update_state(state=state, meta=meta)

@app.task(
        name="ingest", 
        bind=True)
def ingest(self, driver_name:str, url:str, collection:str, catalog:str)->dict:
    """ ingest the archive url in 6 step:
    - identify the driver for ingestion
    - identify the assets to fetch
    - fetch the assets (e.g. copy/download)
    - transform the assets if necessary (e.g. create cog)
    - upload the assets
    - register the item

    Args:
        url (str): archive url
        driver_name (str): driver name
        collection (str): target collection
        catalog (str): target catalog

    Returns:
        object: an dict pointing towards the registered item
    """

    driver_class:Driver=Drivers.get_driver_by_name(driver_name)
    if driver_class is not None:
        driver=driver_class()
        LOGGER.debug("ingestion: 1 - identify_assets")
        __update_status__(LOGGER, self, state='PROGRESS', meta={'step':'identify_assets'})
        assets:list[Asset]=driver.identify_assets(url)
        __check_assets__(url, assets)

        LOGGER.debug("ingestion: 2 - fetch_assets")
        __update_status__(LOGGER, self, state='PROGRESS', meta={'step':'fetch_assets'})
        try:
            assets=driver.fetch_assets(url, assets)
        except requests.exceptions.ConnectionError as e:
            msg="Fetching assets failed for connection reasons ({})".format(e.response)
            LOGGER.error(msg)
            raise ConnectionException(msg)
        __check_assets__(url, assets, file_exists=True)

        LOGGER.debug("ingestion: 3 - transform_assets")
        __update_status__(LOGGER, self, state='PROGRESS', meta={'step':'transform_assets'})
        assets=driver.transform_assets(url, assets)
        __check_assets__(url, assets, file_exists=True)

        LOGGER.debug("ingestion: 4 - create_item")
        __update_status__(LOGGER, self, state='PROGRESS', meta={'step':'create_item'})
        item=driver.to_item(url, assets)
        item.collection=collection
        item.catalog=catalog
        LOGGER.debug("ingestion: 5 - upload")
        i:int=0
        for asset_name,asset in item.assets.items():
            __update_status__(LOGGER, self, state='PROGRESS', meta={'step':'upload', 'current': i, 'total': len(item.assets)})
            i+=1
            asset:Asset=asset
            if asset.aeo__managed == True:
                with open(asset.href, 'rb') as filedesc:
                    file = {'file': (asset.name, filedesc, asset.type)}
                    try:
                        r=requests.post(url=os.path.join(Configuration.settings.aeoprs_endpoint,"collections",item.collection, "items", item.id, "assets", asset.name), files=file)
                        if r.ok:
                            LOGGER.debug("asset uploaded successfully")                    
                        else:
                            msg="Failed to upload asset: {} - {}".format(r.status_code, r.content)
                            LOGGER.error(msg)
                            raise RegisterException(msg)
                    except requests.exceptions.ConnectionError as e:
                        msg="AEOPRS Service can not be reached ({})".format(Configuration.settings.aeoprs_endpoint)
                        LOGGER.error(msg)
                        raise ConnectionException(msg)
        LOGGER.debug("ingestion: 6 - register")
        __update_status__(LOGGER, self, state='PROGRESS', meta={'step':'register_item'})
        item_already_exists=False
        try:
            r=requests.get(url=os.path.join(Configuration.settings.aeoprs_endpoint,"collections",item.collection, "items", item.id), headers={"Content-Type": "application/json"})
            if r.ok:
                item_already_exists=True
        except requests.exceptions.ConnectionError as e:
            msg="AEOPRS Service can not be reached ({})".format(Configuration.settings.aeoprs_endpoint)
            LOGGER.error(msg)
            raise ConnectionException(msg)
        try:
            if item_already_exists:
                r=requests.put(url=os.path.join(Configuration.settings.aeoprs_endpoint,"collections",item.collection, "items", item.id), data=to_json(item), headers={"Content-Type": "application/json"})
            else:
                r=requests.post(url=os.path.join(Configuration.settings.aeoprs_endpoint,"collections",item.collection, "items"), data=to_json(item), headers={"Content-Type": "application/json"})
            if r.ok:
                item_from_json(r.content).model_dump()
                return {
                    "action":"register",
                    "state":"SUCCESS",
                    "item": os.path.join(Configuration.settings.aeoprs_endpoint,"collections",item.collection, "items", item.id)
                    }
            else:
                LOGGER.error("Item has not been registered: {} - {}".format(r.status_code, r.content))
                raise RegisterException("Item has not been registered: {} - {}".format(r.status_code, r.content))
        except requests.exceptions.ConnectionError as e:
            msg="AEOPRS Service can not be reached ({})".format(Configuration.settings.aeoprs_endpoint)
            LOGGER.error(msg)
            raise ConnectionException(msg)
    else:
        LOGGER.error("No driver found for {}".format(url))
        raise DriverException("No driver found for  {}".format(url))


def __check_assets__(url:str, assets:list[Asset], file_exists: bool=False):
    for asset in assets:
        if asset.name is None:
            raise DriverException("Invalid asset for {} : no name provided".format(url))
        if asset.href is None:
            raise DriverException("Invalid asset {} for {} : no href provided".format(asset.name, url))
        if asset.roles is None:
            raise DriverException("Invalid asset {} for {} : no roles provided".format(asset.name, url))
        if file_exists:
            if not os.path.exists(asset.href):
                raise DriverException("Invalid asset {} for {} : file {} not found".format(asset.name, url, asset.href))
