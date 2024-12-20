import os
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from .image_driver_helper import ImageDriverHelper

from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat, MimeType,
                                    ObservationType, Properties, ResourceType,
                                    Role)
from aproc.core.settings import Configuration
from extensions.aproc.proc.ingest.drivers.driver import Driver as ProcDriver
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    get_epsg, get_file_size, get_geom_bbox_centroid, get_hash_url, setup_gdal)


class Driver(ProcDriver):
    quicklook_path = None
    thumbnail_path = None
    xml_path = None
    tif_path = None
    tfw_path = None

    # Implements drivers method

    @staticmethod
    def init(configuration: Configuration):
        return

    # Implements drivers method
    @staticmethod
    def supports(url: str) -> bool:
        try:
            result = Driver.__check_path__(url)
            return result
        except Exception as e:
            Driver.LOGGER.warn(e)
            return False

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        if Driver.quicklook_path is None:
            ImageDriverHelper.add_overview_if_you_can(self, self.tif_path, Role.thumbnail, Driver.thumbnail_size, assets)
            ImageDriverHelper.add_overview_if_you_can(self, self.tif_path, Role.overview, Driver.overview_size, assets)
        assets.append(Asset(href=self.xml_path, size=get_file_size(self.xml_path),
                            roles=[Role.metadata.value], name=Role.metadata.value, type=MimeType.XML,
                            description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.xml.value))
        assets.append(Asset(href=self.tif_path, size=get_file_size(self.tif_path),
                            roles=[Role.data.value], name=Role.data.value, type=MimeType.TIFF,
                            description=Role.data.value, airs__managed=False, asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value))
        if Driver.tfw_path:
            assets.append(Asset(href=self.tfw_path, size=get_file_size(self.tfw_path),
                                roles=[Role.extent.value], name=Role.extent.value, type=MimeType.TEXT,
                                description=Role.extent.value, airs__managed=False, asset_format=AssetFormat.tfw.value, asset_type=ResourceType.other.value))
        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def get_item_id(self, url: str) -> str:
        return get_hash_url(url)

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        from osgeo import gdal
        from osgeo.gdalconst import GA_ReadOnly
        setup_gdal()
        ns = {"gml": "http://www.opengis.net/gml",
              "re": "http://schemas.rapideye.de/products/productMetadataGeocorrected",
              "eop": "http://earth.esa.int/eop",
              "opt": "http://earth.esa.int/opt"}
        tree = ET.parse(self.xml_path)
        root = tree.getroot()
        ul_lat = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:topLeft/re:latitude", ns).text)
        ul_lon = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:topLeft/re:longitude", ns).text)
        ur_lat = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:topRight/re:latitude", ns).text)
        ur_lon = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:topRight/re:longitude", ns).text)
        lr_lat = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:bottomRight/re:latitude", ns).text)
        lr_lon = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:bottomRight/re:longitude", ns).text)
        ll_lat = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:bottomLeft/re:latitude", ns).text)
        ll_lon = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:bottomLeft/re:longitude", ns).text)
        geometry, bbox, centroid = get_geom_bbox_centroid(ul_lon, ul_lat, ur_lon, ur_lat, lr_lon, lr_lat, ll_lon, ll_lat)

        date = root.find("gml:using/eop:EarthObservationEquipment/eop:acquisitionParameters/re:Acquisition/re:acquisitionDateTime", ns).text
        date_time = int(datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())
        view__incidence_angle = float(root.find("gml:using/eop:EarthObservationEquipment/eop:acquisitionParameters/re:Acquisition/eop:incidenceAngle", ns).text)
        view__sun_azimuth = float(root.find("gml:using/eop:EarthObservationEquipment/eop:acquisitionParameters/re:Acquisition/opt:illuminationAzimuthAngle", ns).text)
        view__sun_elevation = float(root.find("gml:using/eop:EarthObservationEquipment/eop:acquisitionParameters/re:Acquisition/opt:illuminationElevationAngle", ns).text)
        view__azimuth = float(root.find("gml:using/eop:EarthObservationEquipment/eop:acquisitionParameters/re:Acquisition/re:azimuthAngle", ns).text)
        sensor_type = root.find("gml:using/eop:EarthObservationEquipment/eop:sensor/re:Sensor/eop:sensorType", ns).text
        sensor = root.find("gml:using/eop:EarthObservationEquipment/eop:platform/eop:Platform/eop:shortName", ns).text
        constellation = root.find("gml:using/eop:EarthObservationEquipment/eop:platform/eop:Platform/eop:shortName", ns).text
        instrument = root.find("gml:using/eop:EarthObservationEquipment/eop:instrument/eop:Instrument/eop:shortName", ns).text
        processing__level = root.find("gml:metaDataProperty/re:EarthObservationMetaData/eop:productType", ns).text
        eo__cloud_cover = float(root.find("gml:resultOf/re:EarthObservationResult/opt:cloudCoverPercentage", ns).text)
        gsdCol = float(root.find("gml:resultOf/re:EarthObservationResult/eop:product/re:ProductInformation/re:columnGsd", ns).text)
        gsdRow = float(root.find("gml:resultOf/re:EarthObservationResult/eop:product/re:ProductInformation/re:rowGsd", ns).text)
        gsd = (gsdCol + gsdRow) / 2
        src_ds = gdal.Open(self.tif_path, GA_ReadOnly)
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
                proj__epsg=get_epsg(src_ds),
                instrument=instrument,
                constellation=constellation,
                sensor=sensor,
                sensor_type=sensor_type,
                view__azimuth=view__azimuth,
                view__incidence_angle=view__incidence_angle,
                view__sun_azimuth=view__sun_azimuth,
                view__sun_elevation=view__sun_elevation,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.rapideye.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.image.value
            ),
            assets=dict(map(lambda asset: (asset.name, asset), assets))
        )
        return item

    @staticmethod
    def __check_path__(path: str):
        Driver.thumbnail_path = None
        Driver.quicklook_path = None
        Driver.tif_path = None
        Driver.xml_path = None
        valid_and_exist = os.path.isdir(path) and os.path.exists(path)
        if valid_and_exist is True:
            for file in os.listdir(path):
                if os.path.isfile(os.path.join(path, file)):
                    if file.endswith("_browse.tif"):
                        Driver.quicklook_path = os.path.join(path, file)
                        Driver.thumbnail_path = os.path.join(path, file)
                    if file.endswith(".tif") and file.find("browse") < 0 and file.find("_udm") < 0:
                        Driver.tif_path = os.path.join(path, file)
                        tfw_path = Path(Driver.tif_path).with_suffix(".tfw")
                        if tfw_path.exists():
                            Driver.tfw_path = str(tfw_path)
                    if file.endswith("_metadata.xml"):
                        Driver.xml_path = os.path.join(path, file)
            return Driver.tif_path is not None and Driver.xml_path is not None
        return False