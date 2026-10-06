import os
import xml.etree.ElementTree as ET
from dateutil import parser
from typing import Any, Callable

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Band, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (downsample_image,
                                                             find_attrib,
                                                             get_bbox,
                                                             get_centroid,
                                                             get_epsg,
                                                             raster_to_jpg)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver
from extensions.aproc.proc.utils.find_rgb import find_rgb_bands


METADATA_KEY = "./Metadata"


class Driver(IngestDriver):

    configuration: dict = {}

    def __init__(self):
        super().__init__()
        self.data_path = None
        self.data_format = None
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

        ImageDriverHelper.add_asset(assets, self.data_path, Role.data, MimeType.OCTET_STREAM,
                                    self.data_format, ResourceType.gridded, eo_bands=self.__get_all_bands(url))

        if self.metadata_path:
            ImageDriverHelper.add_asset(assets, self.metadata_path, Role.metadata, MimeType.XML,
                                        AssetFormat.xml, ResourceType.other)

        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if IngestDriver.must_build_preview(Driver.configuration, self.data_path, local_remote_both="both"):
            Driver.LOGGER.debug(f"Building overview for TIFF {self.data_path}")
            quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
            raster_to_jpg(self.data_path, Driver.OVERVIEW_SIZE, Driver.OVERVIEW_SIZE,
                          output_path=quicklook.href, stretch=Driver.configuration.get('overview_stretch', True),
                          bands_list=find_rgb_bands(self.__get_all_bands(url)))
            quicklook.size = AccessManager.get_size(quicklook.href)
            assets.append(quicklook)

            Driver.LOGGER.debug(f"Building thumbnail for TIFF {self.data_path}")
            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.JPG, AssetFormat.jpg)
            downsample_image(quicklook.href, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR)
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)
        return assets

    def load_metadata(self, url: str) -> dict[str, Any]:
        from osgeo import gdal

        options = gdal.InfoOptions(format="json")
        return AccessManager.get_gdal_info(self.data_path, options)

    def load_xml_metadata(self) -> ET.Element | None:
        if self.metadata_path:
            with AccessManager.make_local(self.metadata_path) as local_metadata_path:
                tree = ET.parse(local_metadata_path)
                root = tree.getroot()

            return root
        return None

    def build_core_item(self, url: str, assets: list[Asset], metadata: dict[str, Any]) -> Item:
        geometry = ImageDriverHelper.gdal_geometry(self, self.data_path, url)
        centroid = get_centroid(geometry)
        bbox = get_bbox(geometry["coordinates"][0])

        xml_root = self.load_xml_metadata()
        if xml_root:
            xml_metadata = find_attrib(xml_root, METADATA_KEY, "domain", "ENVI")
            acquisition_time = self.__get_metadata(xml_metadata, "acquisition_time",
                                                   lambda x: parser.parse(x))
        else:
            try:
                acquisition_time = parser.parse(os.path.basename(self.data_path).split("-")[0])
            except Exception:
                raise DriverException(f"No metadata file found for {url}. No time found in the data file's name.")

        item = Item(
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=acquisition_time,
                constellation="ghost",
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

    def add_major_metadata(self, url: str, item: Item, metadata: dict[str, Any]) -> Item:
        xml_root = self.load_xml_metadata()

        if xml_root:
            xml_metadata = find_attrib(xml_root, METADATA_KEY, "domain", "ENVI")
            item.properties.satellite = self.__get_metadata(xml_metadata, "asset_name")

            along_scan_gsd = self.__get_metadata(xml_metadata, "along_scan_gsd")
            cross_scan_gsd = self.__get_metadata(xml_metadata, "cross_scan_gsd")
            if along_scan_gsd is not None and cross_scan_gsd is not None:
                item.properties.gsd = (float(along_scan_gsd) + float(cross_scan_gsd)) / 2

            item.properties.secondary_id = self.__get_metadata(xml_metadata, "file_id")
        else:
            item.properties.satellite = item.properties.constellation

            item.properties.secondary_id = os.path.basename(self.data_path).removesuffix(".hsi").removesuffix(".dat")

        item.properties.proj__epsg = get_epsg(AccessManager.get_gdal_proj(self.data_path))

        return item

    def add_minor_metadata(self, url: str, item: Item, metadata: dict[str, Any]) -> Item:
        item.properties.instrument = item.properties.satellite
        item.properties.sensor = item.properties.satellite

        xml_root = self.load_xml_metadata()
        if xml_root:
            xml_metadata = find_attrib(xml_root, METADATA_KEY, "domain", "ENVI")

            item.properties.eo__cloud_cover = self.__get_metadata(xml_metadata, "cloud_cover", lambda x: float(x))
            item.properties.view__sun_azimuth = self.__get_metadata(xml_metadata, "sun_azimuth", lambda x: float(x))
            item.properties.view__sun_elevation = self.__get_metadata(xml_metadata, "sun_elevation", lambda x: float(x))

        return item

    def __get_metadata(self, metadata: ET.Element, key: str, process: Callable = None):
        value = find_attrib(metadata, "./MDI", "key", key)
        if value is not None:
            if process is not None:
                return process(value.text)
            return value.text
        return None

    def __get_all_bands(self, url: str) -> list[Band]:
        bands = self.load_metadata(url).get("bands", [])

        eo_bands = []
        for b in bands:
            name = f"B{b['band']}"
            wavelength = b.get("metadata", {}).get("", {}).get("wavelength", None)
            if wavelength:
                # Needs to be in µm
                wavelength = float(wavelength) / 1000
            eo_bands.append(Band(name=name, eo__center_wavelength=wavelength, index=b["band"]))

        return eo_bands

    def __check_path__(self, path: str):
        self.__init__()

        if not AccessManager.is_dir(path):
            return False

        for file in AccessManager.listdir(path):
            if not file.is_dir:
                if file.name.endswith(".hsi"):
                    self.data_path = file.path
                    self.data_format = AssetFormat.hsi
                elif file.name.endswith(".dat"):
                    self.data_path = file.path
                    self.data_format = AssetFormat.dat
                elif file.name.endswith(".hsi.aux.xml"):
                    self.metadata_path = file.path

        return self.data_path is not None
