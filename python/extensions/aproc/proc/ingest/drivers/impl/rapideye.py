import os
import xml.etree.ElementTree as ET
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    downsample_image, find_or_none, geotiff_to_jpg, get_epsg,
    get_geom_bbox_centroid_from_corners)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):
    ns = {"gml": "http://www.opengis.net/gml",
          "re": "http://schemas.rapideye.de/products/productMetadataGeocorrected",
          "eop": "http://earth.esa.int/eop",
          "opt": "http://earth.esa.int/opt"}

    def __init__(self):
        super().__init__()
        self.browse_path = None
        self.xml_path = None
        self.tif_path = None
        self.tfw_path = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        ImageDriverHelper.add_archive(assets, url)

        assets.append(Asset(href=self.xml_path, size=AccessManager.get_size(self.xml_path),
                            roles=[Role.metadata.value], name=Role.metadata.value, type=MimeType.XML.value,
                            description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.xml.value))
        assets.append(Asset(href=self.tif_path, size=AccessManager.get_size(self.tif_path),
                            roles=[Role.data.value], name=Role.data.value, type=MimeType.TIFF.value,
                            description=Role.data.value, airs__managed=False, asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value))
        if self.tfw_path:
            assets.append(Asset(href=self.tfw_path, size=AccessManager.get_size(self.tfw_path),
                                roles=[Role.extent.value], name=Role.extent.value, type=MimeType.TEXT.value,
                                description=Role.extent.value, airs__managed=False, asset_format=AssetFormat.tfw.value, asset_type=ResourceType.other.value))

        if self.browse_path:
            ImageDriverHelper.add_asset(assets, self.browse_path, Role.visual, MimeType.TIFF, AssetFormat.geotiff, ResourceType.gridded)
        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if self.browse_path:
            quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
            geotiff_to_jpg(self.browse_path, Driver.OVERVIEW_FROM_BROWSE_PCT, Driver.OVERVIEW_FROM_BROWSE_PCT, output_path=quicklook.href)
            quicklook.size = AccessManager.get_size(quicklook.href)
            assets.append(quicklook)

            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.JPG, AssetFormat.jpg)
            downsample_image(quicklook.href, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR)
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)
        return assets

    def load_metadata(self, url: str) -> object:
        with AccessManager.make_local(self.xml_path) as local_xml_path:
            tree = ET.parse(local_xml_path)
            root = tree.getroot()

        return root

    def build_core_item(self, url: str, assets: list[Asset], root: ET.Element) -> Item:
        ul_lat = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:topLeft/re:latitude", Driver.ns).text)
        ul_lon = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:topLeft/re:longitude", Driver.ns).text)
        ur_lat = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:topRight/re:latitude", Driver.ns).text)
        ur_lon = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:topRight/re:longitude", Driver.ns).text)
        lr_lat = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:bottomRight/re:latitude", Driver.ns).text)
        lr_lon = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:bottomRight/re:longitude", Driver.ns).text)
        ll_lat = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:bottomLeft/re:latitude", Driver.ns).text)
        ll_lon = float(root.find("gml:target/re:Footprint/re:geographicLocation/re:bottomLeft/re:longitude", Driver.ns).text)
        geometry, bbox, centroid = get_geom_bbox_centroid_from_corners(ul_lon, ul_lat, ur_lon, ur_lat, lr_lon, lr_lat, ll_lon, ll_lat)

        date = root.find("gml:using/eop:EarthObservationEquipment/eop:acquisitionParameters/re:Acquisition/re:acquisitionDateTime", Driver.ns).text
        date_time = int(datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())

        constellation = root.find("gml:using/eop:EarthObservationEquipment/eop:platform/eop:Platform/eop:shortName", Driver.ns).text

        item = Item(
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                constellation=constellation,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.rapideye.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.optic.value
            ),
            assets={asset.name: asset for asset in assets}
        )

        return item

    def add_major_metadata(self, url: str, item: Item, root: ET.Element) -> Item:
        item.properties.proj__epsg = get_epsg(AccessManager.get_gdal_proj(self.tif_path))
        item.properties.processing__level = find_or_none(root, "gml:metaDataProperty/re:EarthObservationMetaData/eop:productType", ns=Driver.ns)
        item.properties.secondary_id = find_or_none(root, "gml:metaDataProperty/re:EarthObservationMetaData/eop:identifier", ns=Driver.ns)

        gsd_col = find_or_none(root, "gml:resultOf/re:EarthObservationResult/eop:product/re:ProductInformation/re:columnGsd", lambda x: float(x), ns=Driver.ns)
        gsd_row = find_or_none(root, "gml:resultOf/re:EarthObservationResult/eop:product/re:ProductInformation/re:rowGsd", lambda x: float(x), ns=Driver.ns)
        if gsd_col is not None and gsd_row is not None:
            item.properties.gsd = (gsd_col + gsd_row) / 2

        return item

    def add_minor_metadata(self, url: str, item: Item, root: ET.Element) -> Item:
        item.properties.view__incidence_angle = find_or_none(root, "gml:using/eop:EarthObservationEquipment/eop:acquisitionParameters/re:Acquisition/eop:incidenceAngle", lambda x: float(x), ns=Driver.ns)
        item.properties.view__sun_azimuth = find_or_none(root, "gml:using/eop:EarthObservationEquipment/eop:acquisitionParameters/re:Acquisition/opt:illuminationAzimuthAngle", lambda x: float(x), ns=Driver.ns)
        item.properties.view__sun_elevation = find_or_none(root, "gml:using/eop:EarthObservationEquipment/eop:acquisitionParameters/re:Acquisition/opt:illuminationElevationAngle", lambda x: float(x), ns=Driver.ns)
        item.properties.view__azimuth = find_or_none(root, "gml:using/eop:EarthObservationEquipment/eop:acquisitionParameters/re:Acquisition/re:azimuthAngle", lambda x: float(x), ns=Driver.ns)
        item.properties.sensor_type = SensorType.OPTIC.value
        item.properties.sensor = find_or_none(root, "gml:using/eop:EarthObservationEquipment/eop:platform/eop:Platform/eop:shortName", ns=Driver.ns)
        item.properties.instrument = find_or_none(root, "gml:using/eop:EarthObservationEquipment/eop:instrument/eop:Instrument/eop:shortName", ns=Driver.ns)
        item.properties.eo__cloud_cover = find_or_none(root, "gml:resultOf/re:EarthObservationResult/opt:cloudCoverPercentage", lambda x: float(x), ns=Driver.ns)

        return item

    def __check_path__(self, path: str):
        self.__init__()
        if AccessManager.is_dir(path):
            for file in AccessManager.listdir(path):
                if not file.is_dir:
                    if file.name.endswith("_browse.tif"):
                        self.browse_path = file.path
                    if file.name.endswith(".tif") and file.name.find("browse") < 0 and file.name.find("_udm") < 0:
                        self.tif_path = file.path
                        tfw_path = os.path.splitext(self.tif_path)[0] + ".tfw"
                        if AccessManager.exists(tfw_path):
                            self.tfw_path = tfw_path
                    if file.name.endswith("_metadata.xml"):
                        self.xml_path = file.path
            return self.tif_path is not None and self.xml_path is not None
        return False
