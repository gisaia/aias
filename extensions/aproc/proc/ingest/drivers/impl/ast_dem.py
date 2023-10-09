import os
from datetime import datetime

from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    ObservationType, Properties, ResourceType,
                                    Role)
from aproc.core.settings import Configuration
from extensions.aproc.proc.ingest.drivers.driver import Driver as ProcDriver
from extensions.aproc.proc.ingest.drivers.impl.utils import \
    get_geom_bbox_centroid, get_id


class Driver(ProcDriver):

    met_path = None
    tif_path = None

    # Implements drivers method

    def init(configuration: Configuration):
        return

    # Implements drivers method
    def supports(url: str) -> bool:
        try:
            result = Driver.__check_path__(url)
            return result
        except Exception as e:
            Driver.LOGGER.debug(e)
            return False

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        return [
            Asset(href=self.tif_path,
                  roles=[Role.data.value], name=Role.data.value, type="image/tif",
                  description=Role.data.value, airs__managed=False, asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value)
        ]

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def get_item_id(self, url: str) -> str:
        return get_id(url)+'-'+get_id(os.path.splitext(os.path.basename(self.tif_path))[0])

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        import pvl
        data = pvl.load(self.met_path)
        ul_lat = float(self.__get_corner_coord__(data, 'UPPERLEFTCORNERLATITUDE'))
        ul_lon = float(self.__get_corner_coord__(data, 'UPPERLEFTCORNERLONGITUDE'))
        ur_lat = float(self.__get_corner_coord__(data, 'UPPERRIGHTCORNERLATITUDE'))
        ur_lon = float(self.__get_corner_coord__(data, 'UPPERRIGHTCORNERLONGITUDE'))
        lr_lat = float(self.__get_corner_coord__(data, 'LOWERRIGHTCORNERLATITUDE'))
        lr_lon = float(self.__get_corner_coord__(data, 'LOWERRIGHTCORNERLONGITUDE'))
        ll_lat = float(self.__get_corner_coord__(data, 'LOWERLEFTCORNERLATITUDE'))
        ll_lon = float(self.__get_corner_coord__(data, 'LOWERLEFTCORNERLONGITUDE'))
        geometry, bbox, centroid = get_geom_bbox_centroid(ul_lon,ul_lat,ur_lon,ur_lat,lr_lon,lr_lat,ll_lon,ll_lat)
        time = data['INVENTORYMETADATA']['SINGLEDATETIME']['TIMEOFDAY']['VALUE']
        date = data['INVENTORYMETADATA']['SINGLEDATETIME']['CALENDARDATE']['VALUE']
        date_time = int(datetime.strptime((date + ' ' + time).rstrip('0'), "%Y-%m-%d %H:%M:%S.%f").timestamp())
        processing__level = data['INVENTORYMETADATA']['COLLECTIONDESCRIPTIONCLASS']['SHORTNAME']['VALUE']
        eo__cloud_cover = float(data['INVENTORYMETADATA']['CLOUDCOVERAGE']['SCENECLOUDCOVERAGE']['VALUE'])
        gsdRow = float(data['INVENTORYMETADATA']['SWATHSTRUCTUREINFO']['CROSSTRACKPIXELRESOLUTION']['VALUE'])
        gsdCol = float(data['INVENTORYMETADATA']['SWATHSTRUCTUREINFO']['ALONGTRACKPIXELRESOLUTION']['VALUE'])
        gsd = (gsdCol + gsdRow)/2
        constellation = data['INVENTORYMETADATA']['PLATFORMINSTRUMENTSENSOR']['PLATFORMSHORTNAME']['VALUE']
        instrument = data['INVENTORYMETADATA']['PLATFORMINSTRUMENTSENSOR']['INSTRUMENTSHORTNAME']['VALUE']
        sensor = data['INVENTORYMETADATA']['PLATFORMINSTRUMENTSENSOR']['PLATFORMSHORTNAME']['VALUE']
        view__sun_azimuth = float(data['INVENTORYMETADATA']['PRODUCTSPECIFICMETADATA']['SOLAR_AZIMUTH_ANGLE']['VALUE'])
        view__sun_elevation = float(data['INVENTORYMETADATA']['PRODUCTSPECIFICMETADATA']['SOLAR_ELEVATION_ANGLE']['VALUE'])

        item = Item(
            id=self.get_item_id(url),
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                eo__cloud_cover=eo__cloud_cover,
                processing__level=processing__level,
                gsd=gsd,
                instrument=instrument,
                constellation=constellation,
                sensor=sensor,
                view__sun_azimuth=view__sun_azimuth,
                view__sun_elevation=view__sun_elevation,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.ast_dem.value,
                main_asset_format=AssetFormat.geotiff.value,
                observation_type=ObservationType.dem.value
            ),
            assets=dict(map(lambda asset: (asset.name, asset), assets))
        )
        return item

    def __check_path__(path: str):
        Driver.tif_path = None
        Driver.met_path = None
        valid_and_exist = os.path.isdir(path) and os.path.exists(path)
        if valid_and_exist is True:
            for file in os.listdir(path):
                if os.path.isfile(os.path.join(path, file)):
                    if file.endswith(".tif"):
                        Driver.tif_path = os.path.join(path, file)
                    if file.endswith(".tif.met"):
                        Driver.met_path = os.path.join(path, file)
            return Driver.tif_path is not None and Driver.met_path is not None

        else:
            Driver.LOGGER.debug("The reference {} is not a folder or does not exist.".format(path))
            return False
    @staticmethod
    def __get_corner_coord__( data,corner):
        return data['INVENTORYMETADATA']['SPATIALDOMAINCONTAINER']['HORIZONTALSPATIALDOMAINCONTAINER']['BOUNDINGBOX'][corner]['VALUE']
