from aproc.core.settings import Configuration
from aproc.proc.ingest.drivers.drivers import Drivers
from aproc.core.aproc_celery_app import APROC_CELERY_APP, LOGGER
from aproc.proc.ingest.drivers.exceptions import DriverException, RegisterException, ConnectionException
from airs.core.models.model import Asset
from airs.core.models.mapper import to_json, item_from_json
import os
import requests

def __update_status__(LOGGER, task, state: str, meta: dict = None):
    LOGGER.info(task.name+" "+state+" "+str(meta))
    if task.request.id is not None:
        task.update_state(state=state, meta=meta)


@APROC_CELERY_APP.task(
        name="ingest", 
        bind=True)
def ingest(self, url: str, collection: str, catalog: str) -> dict:
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
    Configuration.init(os.environ.get("APROC_CONFIGURATION_FILE"))
    Drivers.init()

    driver = Drivers.solve(url)
    if driver is not None:
        LOGGER.debug("ingestion: 1 - identify_assets")
        __update_status__(LOGGER, self, state='PROGRESS', meta={'step':'identify_assets'})
        assets: list[Asset] = driver.identify_assets(url)
        __check_assets__(url, assets)

        LOGGER.debug("ingestion: 2 - fetch_assets")
        __update_status__(LOGGER, self, state='PROGRESS', meta={'step':'fetch_assets'})
        try:
            assets = driver.fetch_assets(url, assets)
        except requests.exceptions.ConnectionError as e:
            msg = "Fetching assets failed for connection reasons ({})".format(e.response)
            LOGGER.error(msg)
            raise ConnectionException(msg)
        __check_assets__(url, assets, file_exists=True)

        LOGGER.debug("ingestion: 3 - transform_assets")
        __update_status__(LOGGER, self, state='PROGRESS', meta={'step':'transform_assets'})
        assets = driver.transform_assets(url, assets)
        __check_assets__(url, assets, file_exists=True)

        LOGGER.debug("ingestion: 4 - create_item")
        __update_status__(LOGGER, self, state='PROGRESS', meta={'step':'create_item'})
        item = driver.to_item(url, assets)
        item.collection = collection
        item.catalog = catalog
        LOGGER.debug("ingestion: 5 - upload")
        i: int = 0
        for asset_name, asset in item.assets.items():
            __update_status__(LOGGER, self, state='PROGRESS', meta={'step': 'upload', 'current': i, 'asset': asset_name, 'total': len(item.assets)})
            i += 1
            asset: Asset = asset
            if asset.airs__managed == True:
                with open(asset.href, 'rb') as filedesc:
                    file = {'file': (asset.name, filedesc, asset.type)}
                    try:
                        r=requests.post(url=os.path.join(Configuration.settings.airs_endpoint, "collections",item.collection, "items", item.id, "assets", asset.name), files=file)
                        if r.ok:
                            LOGGER.debug("asset uploaded successfully")                    
                        else:
                            msg="Failed to upload asset: {} - {}".format(r.status_code, r.content)
                            LOGGER.error(msg)
                            raise RegisterException(msg)
                    except requests.exceptions.ConnectionError as e:
                        msg="AIRS Service can not be reached ({})".format(Configuration.settings.airs_endpoint)
                        LOGGER.error(msg)
                        raise ConnectionException(msg)
            else:
                LOGGER.info("{} not managed".format(asset.name))
        LOGGER.debug("ingestion: 6 - register")
        __update_status__(LOGGER, self, state='PROGRESS', meta={'step':'register_item'})
        item_already_exists=False
        try:
            r=requests.get(url=os.path.join(Configuration.settings.airs_endpoint,"collections",item.collection, "items", item.id), headers={"Content-Type": "application/json"})
            if r.ok:
                item_already_exists=True
        except requests.exceptions.ConnectionError as e:
            msg="AIRS Service can not be reached ({})".format(Configuration.settings.airs_endpoint)
            LOGGER.error(msg)
            raise ConnectionException(msg)
        try:
            if item_already_exists:
                r=requests.put(url=os.path.join(Configuration.settings.airs_endpoint,"collections",item.collection, "items", item.id), data=to_json(item), headers={"Content-Type": "application/json"})
            else:
                r=requests.post(url=os.path.join(Configuration.settings.airs_endpoint,"collections",item.collection, "items"), data=to_json(item), headers={"Content-Type": "application/json"})
            if r.ok:
                item_from_json(r.content).model_dump()
                return {
                    "action":"register",
                    "state":"SUCCESS",
                    "item": os.path.join(Configuration.settings.airs_endpoint,"collections",item.collection, "items", item.id)
                    }
            else:
                LOGGER.error("Item has not been registered: {} - {}".format(r.status_code, r.content))
                raise RegisterException("Item has not been registered: {} - {}".format(r.status_code, r.content))
        except requests.exceptions.ConnectionError as e:
            msg="AIRS Service can not be reached ({})".format(Configuration.settings.airs_endpoint)
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
            if asset.airs__managed is True and not os.path.exists(asset.href):
                raise DriverException("Invalid asset {} for {} : file {} not found".format(asset.name, url, asset.href))
