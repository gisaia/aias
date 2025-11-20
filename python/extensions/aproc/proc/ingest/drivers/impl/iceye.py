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
    downsample_image, get_epsg_from_gdal_info, get_geom_bbox_centroid)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):
    output_folder: str | None = None  # todo: this should use self.get_asset_filepath instead

    def __init__(self):
        super().__init__()
        self.md_path = None
        self.tif_path = None
        self.quicklook_path = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)
        Driver.output_folder = configuration['tmp_directory']

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []

        ImageDriverHelper.add_asset(assets, self.tif_path, Role.data,
                                    MimeType.GEOTIFF, AssetFormat.geotiff, ResourceType.gridded)
        ImageDriverHelper.add_asset(assets, self.md_path, Role.metadata,
                                    MimeType.XML, AssetFormat.xml, ResourceType.other)
        ImageDriverHelper.add_asset(assets, self.quicklook_path, Role.overview,
                                    MimeType.PNG, AssetFormat.png, ResourceType.other, airs__managed=True)
        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        thumbnail_folder = os.path.join(Driver.output_folder, self.get_item_id(url), 'thumbnail')
        AccessManager.makedir(thumbnail_folder)
        thumbnail_path = os.path.join(thumbnail_folder, "thumbnail.png")

        downsample_image(self.quicklook_path, thumbnail_path, 8)
        ImageDriverHelper.add_asset(assets, thumbnail_path, Role.thumbnail,
                                    MimeType.PNG, AssetFormat.png, ResourceType.other, airs__managed=True)

        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        with AccessManager.make_local(self.md_path) as local_md_path:
            tree = ET.parse(local_md_path)
            root = tree.getroot()

        [_, _, ul_lat, ul_lon] = root.find("coord_first_near").text.split(" ")
        [_, _, ur_lat, ur_lon] = root.find("coord_first_far").text.split(" ")
        [_, _, lr_lat, lr_lon] = root.find("coord_last_far").text.split(" ")
        [_, _, ll_lat, ll_lon] = root.find("coord_last_near").text.split(" ")

        geometry, bbox, centroid = get_geom_bbox_centroid(float(ul_lon), float(ul_lat), float(ur_lon), float(ur_lat), float(lr_lon), float(lr_lat), float(ll_lon), float(ll_lat))

        start_time = root.find("acquisition_start_utc").text
        start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%f")
        stop_time = root.find("acquisition_end_utc").text
        stop_time = datetime.strptime(stop_time, "%Y-%m-%dT%H:%M:%S.%f")

        satellite = root.find("satellite_name").text
        level = root.find("product_level").text
        range_spacing = float(root.find("range_spacing").text)
        azimuth_spacing = float(root.find("azimuth_spacing").text)
        gsd = (range_spacing + azimuth_spacing) / 2
        orbit_direction = root.find("orbit_direction").text
        orbit_number = root.find("orbit_absolute_number").text
        polarizations = [root.find("polarization").text]

        item = Item(
            id=self.get_item_id(url),
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=start_time,
                start_datetime=start_time,
                end_datetime=stop_time,
                constellation="Sentinel 1",
                satellite=satellite,
                instrument=satellite,
                sensor=satellite,
                sensor_type=SensorType.SAR,
                item_format=ItemFormat.safe,
                main_asset_format=AssetFormat.geotiff,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.radar,
                processing__level=level,
                gsd=gsd,
                acq__acquisition_orbit_direction=orbit_direction,
                acq__acquisition_orbit=orbit_number,
                sar__polarizations=polarizations,
                proj__epsg=get_epsg_from_gdal_info(self.tif_path)
            ),
            assets=dict([(asset.name, asset) for asset in assets])
        )

        return item

    def __check_path__(self, path: str):
        self.__init__()

        if os.path.basename(path).startswith("ICEYE") and AccessManager.is_dir(path):
            for file in AccessManager.listdir(path):
                if file.name.startswith("ICEYE") and file.name.endswith(".tif"):
                    self.tif_path = file.path
                elif file.name.startswith("ICEYE") and file.name.endswith(".xml"):
                    self.md_path = file.path
                elif file.name.startswith("ICEYE_QUICKLOOK") and file.name.endswith(".png"):
                    self.quicklook_path = file.path

            return self.tif_path is not None \
                and self.md_path is not None \
                and self.quicklook_path is not None

        return False
