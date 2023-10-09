import json
import os
import time
from datetime import datetime

import requests
from dateutil.parser import parse as parse_date

from airs.core.models.model import Asset, Band, Item, ObservationType, Properties, Role, ItemFormat, AssetFormat, ResourceType
from aproc.core.settings import Configuration
from extensions.aproc.proc.ingest.drivers.driver import Driver as ProcDriver
from extensions.aproc.proc.ingest.drivers.exceptions import ConnectionException


class Driver(ProcDriver):
    token=None
    manage_data=False

    # Implements drivers method
    def init(configuration:Configuration):
        token=Driver.__getTheiaToken__(configuration["login"], configuration["pwd"], configuration["token_url"])
        manage_data=configuration.get("manage_data", False)

    # Implements drivers method
    def supports(url:str)->bool:
        try:
            result=Driver.__fetch_url__(url)
            return result is not None and result.get("collection") is not None and result.get("collection")=="theia"
        except Exception as e:
            Driver.LOGGER.debug(e)
            return False

    # Implements drivers method
    def get_item_id(self, url: str) -> str:
        ...

    # Implements drivers method
    def identify_assets(self, url:str)->list[Asset]:
        hits=Driver.__fetch_url__(url).get("hits")
        if hits:
            if len(hits)>0:
                if len(hits)<2:
                    hit=hits[0]
                    return [
                        Asset(href=hit["data"]["metadata"]["core"]["graphics"]["thumbnail"], roles=[Role.thumbnail.value], name=Role.thumbnail.value, type="image/png", description=Role.thumbnail.value, asset_format=AssetFormat.png.value, asset_type=ResourceType.gridded.value),
                        Asset(href=hit["data"]["metadata"]["core"]["graphics"]["quicklook"], roles=[Role.overview.value], name=Role.overview.value, type="image/png", description=Role.overview.value, asset_format=AssetFormat.png.value, asset_type=ResourceType.gridded.value),
                        Asset(href=hit["data"]["_services"]["download"][0]["url"]+"?issuerId=theia", roles=[Role.data.value], name=Role.data.value, type="application/zip", description=Role.data.value, airs__managed=Driver.manage_data, asset_format=AssetFormat.zip.value, asset_type=ResourceType.other.value)
                    ]
                else: 
                    Driver.LOGGER.error("more than one hit found ({} found)".format(len(hits.get("hits"))))
                    return []
            else: 
                Driver.LOGGER.error("no hits found")
                return []
        else:
            Driver.LOGGER.error("no hits found")
            return []

    # Implements drivers method
    def fetch_assets(self, url:str, assets:list[Asset])->list[Asset]:
        for asset in assets:
            if asset.airs__managed:
                filepath=self.get_asset_filepath(url, asset)
                token=Driver.token
                Driver.LOGGER.debug("Using token {} ".format(token))
                time_start = time.time()
                tmp_file=filepath+".download"
                get_product = 'curl -o {} -k -H "Authorization: Bearer {}" {}'.format(tmp_file, token, asset.href)
                Driver.LOGGER.debug("Downloading product with {} ".format(get_product))
                os.system(get_product)
                if not os.path.exists(tmp_file):
                    msg="Fetching assets failed for connection reasons ({})".format(asset.href)
                    Driver.LOGGER.error(msg)
                    raise ConnectionException(msg)
                os.rename(tmp_file, filepath)
                Driver.LOGGER.debug("Product downloaded in {}s ({} Mb)".format(round(time.time() - time_start), round(os.path.getsize(filepath)/1000000)))
                asset.href=filepath
        return assets

    # Implements drivers method
    def transform_assets(self, url:str, assets:list[Asset])->list[Asset]:
        return assets

    # Implements drivers method
    def to_item(self, url:str, assets:list[Asset])->Item:
        hits=Driver.__fetch_url__(url).get("hits")
        hit=hits[0]
        bands=[]
        if hit["data"]["metadata"]["core"]["identity"]["collection"].lower()=="sentinel2" and hit["data"]["metadata"]["core"]["description"]["processingLevel_en"].lower()=="level 2a":
            bands = [Band(name="B2", common_name="Blue - Wavelength 456-532"),
                     Band(name="B3", common_name="Green - Wavelength 536-582"),
                     Band(name="B4", common_name="Red - Wavelength 646-685"),
                     Band(name="B5", common_name="Vegetation Red Edge - Wavelength 694-714"),
                     Band(name="B6", common_name="Vegetation Red Edge - Wavelength 730-748"),
                     Band(name="B7", common_name="Vegetation Red Edge - Wavelength 766-794"),
                     Band(name="B8", common_name="NIR - Wavelength 774-907"),
                     Band(name="B8A", common_name="Vegetation Red Edge - Wavelength 848-880"),
                     Band(name="B11", common_name="SWIR - Wavelength 1538-1679"),
                     Band(name="B12", common_name="SWIR - Wavelength 2065-2303")]
        else:
            if hit["data"]["metadata"]["core"]["identity"]["collection"].lower()=="snow":
                bands = [Band(name="SCD", common_name="Snow_Cover_Duration"),
                        Band(name="SMD", common_name="Snow_Melt_Out_Date"),
                        Band(name="SOD", common_name="Snow_Onset_Date"),
                        Band(name="NOB", common_name="Number_Observations")]
            else:
                Driver.LOGGER.error("No bands identified for {}".format(hit["data"]["metadata"]["core"]["identity"]["collection"]))
        id=hit["md"]["id"]
        acquisition_date=hit["md"]["timestamp"]/1000
        item=Item(
            id=id,
            geometry=hit["md"]["geometry"],
            centroid=hit["md"]["centroid"]["coordinates"],
            bbox= [min(map(lambda xy: xy[0],hit["md"]["geometry"]["coordinates"][0])),min(map(lambda xy: xy[1],hit["md"]["geometry"]["coordinates"][0])),max(map(lambda xy: xy[0],hit["md"]["geometry"]["coordinates"][0])),max(map(lambda xy: xy[1],hit["md"]["geometry"]["coordinates"][0]))],
            properties=Properties(
                item_format=ItemFormat.theia.value,
                datetime=acquisition_date,
                begin_datetime=int(datetime.timestamp(parse_date(hit["data"]["metadata"]["core"]["temporalCoverage"]["begin"]))),
                end_datetime= int(datetime.timestamp(parse_date(hit["data"]["metadata"]["core"]["temporalCoverage"]["end"]))),
                constellation=hit["data"]["metadata"]["core"]["identity"]["collection"],
                processing__level=hit["data"]["metadata"]["core"]["description"]["processingLevel_en"],
                sensor_type= hit["data"]["_sensorType_en"],
                eo__cloud_cover= hit["data"]["metadata"]["ObservationContext"]["eo"]["opt"]["cloudCoverPercentage"],
                eo__snow_cover= hit["data"]["metadata"]["ObservationContext"]["eo"]["opt"]["snowCoverPercentage"],
                water_coverage= hit["data"]["metadata"]["ObservationContext"]["eo"]["opt"]["waterCoverPercentage"],
                gsd=hit["data"]["metadata"]["ObservationContext"]["processusUsed"]["sensor"]["resolution"]["value"],
                create_datetime=int(datetime.timestamp(parse_date(hit["data"]["metadata"]["core"]["identity"]["lifecycle"]["created"]))),
                update_datetime=int(datetime.timestamp(parse_date(hit["data"]["metadata"]["core"]["identity"]["lifecycle"]["updated"]))),
                item_type=ResourceType.gridded.value,
                main_asset_format=AssetFormat.zip.value,
                observation_type=ObservationType.image.value
            ),
            assets=dict(map(lambda asset: (asset.name, asset), assets))
        )
        return item

    def __fetch_url__(url:str):
        r = requests.get(url, verify=False)
        if r.ok:
            return json.loads(r.content)
        else: return None

    def __getTheiaToken__(login:str, pwd:str, url):
        Driver.LOGGER.debug("Retrieving access token from theia for {}".format(login))
        get_token_cmd = 'curl -k -s -X POST --data-urlencode "ident={}" --data-urlencode "pass={}" {}>token.json'.format(login, pwd, url)
        os.system(get_token_cmd)
        __token = ""
        with open('token.json') as data_file:
            try:
                __token=data_file.readline()
            except:
                Driver.LOGGER.error("Failed to fetch the token ... with the command line {}".format(get_token_cmd))
        os.remove('token.json')
        return __token
