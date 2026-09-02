import re
import xml.etree.ElementTree as ET
from dateutil import parser
from typing import Callable

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Band, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (downsample_image,
                                                             find_attrib,
                                                             get_bbox,
                                                             get_centroid,
                                                             get_epsg,
                                                             raster_to_jpg)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):

    configuration: dict = {}

    def __init__(self):
        super().__init__()
        self.hsi_path = None
        self.metadata_path = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)
        Driver.configuration = configuration or {}

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        ImageDriverHelper.add_archive(assets, url)

        # Compute eo__bands
        def create_eo_band(band: ET.Element):
            idx, wavelength = self.__parse_band(band)

            return Band(name=f"B{idx}", index=idx, eo__center_wavelength=wavelength)
        eo__bands = map(lambda x: create_eo_band(x), self.__get_all_bands(url))

        ImageDriverHelper.add_asset(assets, self.hsi_path, Role.data, MimeType.OCTET_STREAM,
                                    AssetFormat.hsi, ResourceType.gridded, eo_bands=list(eo__bands))

        ImageDriverHelper.add_asset(assets, self.metadata_path, Role.metadata, MimeType.XML,
                                    AssetFormat.xml, ResourceType.other)

        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if IngestDriver.must_build_preview(Driver.configuration, self.hsi_path, local_remote_both="both"):
            Driver.LOGGER.debug(f"Building overview for local TIFF {self.hsi_path}")
            quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
            raster_to_jpg(self.hsi_path, Driver.OVERVIEW_FROM_TIFF_PCT, Driver.OVERVIEW_FROM_TIFF_PCT,
                          output_path=quicklook.href, stretch=True, bands_list=self.__find_rgb_bands(url))
            quicklook.size = AccessManager.get_size(quicklook.href)
            assets.append(quicklook)

            Driver.LOGGER.debug(f"Building thumbnail for local TIFF {self.hsi_path}")
            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.JPG, AssetFormat.jpg)
            downsample_image(quicklook.href, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR)
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)
        return assets

    def load_metadata(self, url: str) -> ET.Element:
        with AccessManager.make_local(self.metadata_path) as local_metadata_path:
            tree = ET.parse(local_metadata_path)
            root = tree.getroot()

        return root

    def build_core_item(self, url: str, assets: list[Asset], root: ET.Element) -> Item:
        geometry = ImageDriverHelper.gdal_geometry(self, self.hsi_path, url)
        centroid = get_centroid(geometry)
        bbox = get_bbox(geometry["coordinates"][0])

        metadata = find_attrib(root, "./Metadata", "domain", "ENVI")
        acquisition_time = self.__get_metadata(metadata, "acquisition_time",
                                               lambda x: parser.parse(x))

        item = Item(
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=acquisition_time,
                constellation="OSK",
                sensor_type=SensorType.HYPERSPECTRAL.value,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.osk.value,
                main_asset_format=AssetFormat.hsi.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.hyperspectral.value
            ),
            assets={asset.name: asset for asset in assets}
        )

        return item

    def add_major_metadata(self, url: str, item: Item, root: ET.Element) -> Item:
        metadata = find_attrib(root, "./Metadata", "domain", "ENVI")
        item.properties.satellite = self.__get_metadata(metadata, "asset_name")

        along_scan_gsd = self.__get_metadata(metadata, "along_scan_gsd")
        cross_scan_gsd = self.__get_metadata(metadata, "cross_scan_gsd")
        if along_scan_gsd is not None and cross_scan_gsd is not None:
            item.properties.gsd = (float(along_scan_gsd) + float(cross_scan_gsd)) / 2

        item.properties.proj__epsg = get_epsg(AccessManager.get_gdal_proj(self.hsi_path))

        item.properties.secondary_id = self.__get_metadata(metadata, "file_id")

        return item

    def add_minor_metadata(self, url: str, item: Item, root: ET.Element) -> Item:
        item.properties.instrument = item.properties.satellite
        item.properties.sensor = item.properties.satellite

        metadata = find_attrib(root, "./Metadata", "domain", "ENVI")

        item.properties.eo__cloud_cover = self.__get_metadata(metadata, "cloud_cover", lambda x: float(x))
        item.properties.view__sun_azimuth = self.__get_metadata(metadata, "sun_azimuth", lambda x: float(x))
        item.properties.view__sun_elevation = self.__get_metadata(metadata, "sun_elevation", lambda x: float(x))

        return item

    def __get_metadata(self, metadata: ET.Element, key: str, process: Callable = None):
        value = find_attrib(metadata, "./MDI", "key", key)
        if value is not None:
            if process is not None:
                return process(value.text)
            return value.text
        return None

    def __get_all_bands(self, url: str):
        bands = self.load_metadata(url).find("./Metadata")
        all_bands = filter(lambda x: x.attrib and x.attrib["key"].startswith("Band_"), bands.findall("./MDI"))

        return all_bands

    def __parse_band(self, band: ET.Element):
        number_regex = re.compile(r"(\d+\.?\d?)")

        _, idx, wavelength = band.text.split(" ", 2)
        wavelength = float(number_regex.findall(wavelength)[0])

        return int(idx), wavelength

    def __find_rgb_bands(self, url: str):
        def update_closest_band(band: ET.Element, target_wavelength: float, closest_band):
            idx, wavelength = self.__parse_band(band)

            if closest_band is None:
                closest_band = {"idx": idx, "wavelength": wavelength}
            elif abs(wavelength - target_wavelength) < abs(closest_band["wavelength"] - target_wavelength):
                closest_band = {"idx": idx, "wavelength": wavelength}
            return closest_band

        BLUE_BAND = 470
        closest_blue_band = None
        GREEN_BAND = 550
        closest_green_band = None
        RED_BAND = 660
        closest_red_band = None

        for band in self.__get_all_bands(url):
            closest_blue_band = update_closest_band(band, BLUE_BAND, closest_blue_band)
            closest_green_band = update_closest_band(band, GREEN_BAND, closest_green_band)
            closest_red_band = update_closest_band(band, RED_BAND, closest_red_band)

        return [closest_red_band["idx"], closest_green_band["idx"], closest_blue_band["idx"]]

    def __check_path__(self, path: str):
        self.__init__()

        if not AccessManager.is_dir(path):
            return False

        for file in AccessManager.listdir(path):
            if not file.is_dir and file.name.endswith(".hsi"):
                self.hsi_path = file.path
            elif not file.is_dir and file.name.endswith(".hsi.aux.xml"):
                self.metadata_path = file.path

        return self.hsi_path is not None \
            and self.metadata_path is not None
