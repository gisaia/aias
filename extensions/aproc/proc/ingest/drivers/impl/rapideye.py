import os
import xml.etree.ElementTree as ET
from airs.core.models.model import Asset, Item, Properties, Role
from aproc.core.settings import Configuration
from extensions.aproc.proc.ingest.drivers.driver import Driver as ProcDriver
from extensions.aproc.proc.ingest.drivers.impl.utils import setup_gdal, get_geom_bbox_centroid
from datetime import datetime

class Driver(ProcDriver):
    quicklook_path = None
    thumbnail_path = None
    xml_path = None
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
        assets = []
        if self.thumbnail_path is not None:
            assets.append(Asset(href=self.thumbnail_path,
                                roles=[Role.thumbnail.value], name=Role.thumbnail.value, type="image/jpg",
                                description=Role.thumbnail.value))
        if self.quicklook_path is not None:
            assets.append(Asset(href=self.quicklook_path,
                                roles=[Role.overview.value], name=Role.overview.value, type="image/jpg",
                                description=Role.overview.value))
        assets.append(Asset(href=self.tif_path,
                            roles=[Role.data.value], name=Role.data.value, type="image/tif",
                            description=Role.data.value, airs__managed=False))

        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        from osgeo import gdal, ogr
        setup_gdal()
        ns = {"gml": "http://www.opengis.net/gml",
              "re":"http://schemas.rapideye.de/products/productMetadataGeocorrected",
              "eop":"http://earth.esa.int/eop",
              "opt":"http://earth.esa.int/opt"}
        tree = ET.parse(self.xml_path)
        root = tree.getroot()
        ul_lat = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:topLeft/re:latitude",ns).text)
        ul_lon = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:topLeft/re:longitude",ns).text)
        ur_lat = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:topRight/re:latitude",ns).text)
        ur_lon = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:topRight/re:longitude",ns).text)
        lr_lat = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:bottomRight/re:latitude",ns).text)
        lr_lon = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:bottomRight/re:longitude",ns).text)
        ll_lat = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:bottomLeft/re:latitude",ns).text)
        ll_lon = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:bottomLeft/re:longitude",ns).text)
        geometry, bbox, centroid = get_geom_bbox_centroid(ul_lon,ul_lat,ur_lon,ur_lat,lr_lon,lr_lat,ll_lon,ll_lat)

        date = root.find("gml:using/eop:EarthObservationEquipment/eop:acquisitionParameters/re:Acquisition/re:acquisitionDateTime",ns).text
        date_time = int(datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())
        view__incidence_angle = float(root.find("gml:using/eop:EarthObservationEquipment/eop:acquisitionParameters/re:Acquisition/eop:incidenceAngle",ns).text)
        view__sun_azimuth = float(root.find("gml:using/eop:EarthObservationEquipment/eop:acquisitionParameters/re:Acquisition/opt:illuminationAzimuthAngle",ns).text)
        view__sun_elevation = float(root.find("gml:using/eop:EarthObservationEquipment/eop:acquisitionParameters/re:Acquisition/opt:illuminationElevationAngle",ns).text)
        view__azimuth = float(root.find("gml:using/eop:EarthObservationEquipment/eop:acquisitionParameters/re:Acquisition/re:azimuthAngle",ns).text)
        sensor_type = root.find("gml:using/eop:EarthObservationEquipment/eop:sensor/re:Sensor/eop:sensorType",ns).text
        sensor = root.find("gml:using/eop:EarthObservationEquipment/eop:platform/eop:Platform/eop:shortName",ns).text
        constellation = root.find("gml:using/eop:EarthObservationEquipment/eop:platform/eop:Platform/eop:shortName",ns).text
        instrument = root.find("gml:using/eop:EarthObservationEquipment/eop:instrument/eop:Instrument/eop:shortName",ns).text
        processing__level = root.find("gml:metaDataProperty/re:EarthObservationMetaData/eop:productType",ns).text
        eo__cloud_cover =  float(root.find("gml:resultOf/re:EarthObservationResult/opt:cloudCoverPercentage",ns).text)
        gsdCol = float(root.find("gml:resultOf/re:EarthObservationResult/eop:product/re:ProductInformation/re:columnGsd",ns).text)
        gsdRow = float(root.find("gml:resultOf/re:EarthObservationResult/eop:product/re:ProductInformation/re:rowGsd",ns).text)
        gsd = (gsdCol + gsdRow)/2

        item = Item(
            id=str(url.replace("/", "-")),
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                eo__cloud_cover=eo__cloud_cover,
                processing__level=processing__level,
                gsd=gsd,
                instrument= instrument,
                constellation = constellation,
                sensor = sensor,
                sensor_type = sensor_type,
                view__azimuth= view__azimuth,
                view__incidence_angle=view__incidence_angle,
                view__sun_azimuth= view__sun_azimuth,
                view__sun_elevation= view__sun_elevation
            ),
            assets=dict(map(lambda asset: (asset.name, asset), assets))
        )
        return item

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
                    if file.endswith(".tif") and file.find("browse")<0:
                        Driver.tif_path = os.path.join(path, file)
                    if file.endswith("_metadata.xml"):
                        Driver.xml_path = os.path.join(path, file)
            return Driver.tif_path is not None and \
                   Driver.xml_path is not None

        else:
            #TODO try to hide this log for file exploration services
            Driver.LOGGER.error("The folder {} does not exist.".format(path))
            return False