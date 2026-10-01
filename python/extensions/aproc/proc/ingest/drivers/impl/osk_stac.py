import json
from typing import Any

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Band, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from dateutil import parser
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (downsample_image,
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
        self.browse_path = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)
        Driver.configuration = configuration or {}

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        ImageDriverHelper.add_archive(assets, url)

        ImageDriverHelper.add_asset(assets, self.hsi_path, Role.data, MimeType.OCTET_STREAM,
                                    AssetFormat.hsi, ResourceType.gridded, eo_bands=self.__get_asset_bands(url, Role.data.value))

        ImageDriverHelper.add_asset(assets, self.metadata_path, Role.metadata, MimeType.XML,
                                    AssetFormat.xml, ResourceType.other)

        if self.browse_path:
            ImageDriverHelper.add_asset(assets, self.browse_path, Role.visual, MimeType.TIFF,
                                        AssetFormat.geotiff, ResourceType.gridded, eo_bands=self.__get_asset_bands(url, Role.visual.value))
        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        data_path = None
        bands_list = None
        if self.browse_path:
            data_path = self.browse_path
        elif IngestDriver.must_build_preview(Driver.configuration, self.hsi_path, local_remote_both="both"):
            data_path = self.hsi_path
            bands_list = self.__find_rgb_bands(url)

        if data_path is not None:
            Driver.LOGGER.debug(f"Building overview from {data_path} for {url}")
            quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
            raster_to_jpg(data_path, Driver.OVERVIEW_SIZE, Driver.OVERVIEW_SIZE,
                          output_path=quicklook.href, stretch=Driver.configuration.get('overview_stretch', True), bands_list=bands_list)
            quicklook.size = AccessManager.get_size(quicklook.href)
            assets.append(quicklook)

            Driver.LOGGER.debug(f"Building thumbnail for {url}")
            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.JPG, AssetFormat.jpg)
            downsample_image(quicklook.href, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR)
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)
        return assets

    def load_metadata(self, url: str) -> dict[str, Any]:
        with AccessManager.stream(self.metadata_path) as fb:
            md = json.load(fb)
        return md

    def build_core_item(self, url: str, assets: list[Asset], metadata: dict[str, Any]) -> Item:
        datetime = metadata["properties"]["datetime"]
        start_datetime = metadata["properties"]["start_datetime"]
        end_datetime = metadata["properties"]["end_datetime"]
        geometry = metadata["geometry"]

        item = Item(
            geometry=geometry,
            bbox=metadata["bbox"],
            centroid=get_centroid(geometry),
            properties=Properties(
                datetime=parser.parse(datetime),
                start_datetime=parser.parse(start_datetime),
                end_datetime=parser.parse(end_datetime),
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
        item.properties.satellite = item.properties.constellation
        item.properties.gsd = metadata.get("properties", {}).get("gsd", None)

        item.properties.proj__epsg = get_epsg(AccessManager.get_gdal_proj(self.hsi_path))

        item.properties.secondary_id = metadata.get("id", None)
        item.properties.processing__level = metadata.get("properties", {}).get("processing:level", None)

        return item

    def add_minor_metadata(self, url: str, item: Item, metadata: dict[str, Any]) -> Item:
        item.properties.instrument = item.properties.satellite
        item.properties.sensor = item.properties.satellite

        item.properties.eo__cloud_cover = metadata.get("properties", {}).get("eo:cloud_cover", None)
        item.properties.view__sun_azimuth = metadata.get("properties", {}).get("view:sun_azimuth", None)
        item.properties.view__sun_elevation = metadata.get("properties", {}).get("view:sun_elevation", None)
        item.properties.view__incidence_angle = metadata.get("properties", {}).get("view:incidence_angle", None)
        item.properties.view__off_nadir = metadata.get("properties", {}).get("view:off_nadir", None)

        return item

    def __get_asset_bands(self, url: str, asset_name: str) -> list[Band]:
        bands = self.load_metadata(url).get("assets", {}).get(asset_name, {}).get("bands", [])

        return [Band(
            name=b.get("name", None),
            eo__center_wavelength=b.get("eo:center_wavelength", None),
            eo__full_width_half_max=b.get("eo:full_width_half_max", None),
            eo__common_name=b.get("eo:common_name", None)
        ) for b in bands]

    def __find_rgb_bands(self, url: str):
        def update_closest_band(band: Band, target_wavelength: float, closest_band):
            if closest_band is None:
                closest_band = {"idx": band.name[1:], "wavelength": band.eo__center_wavelength}
            elif abs(band.eo__center_wavelength - target_wavelength) < abs(closest_band["wavelength"] - target_wavelength):
                closest_band = {"idx": band.name[1:], "wavelength": band.eo__center_wavelength}
            return closest_band

        BLUE_BAND = 470
        closest_blue_band = None
        GREEN_BAND = 550
        closest_green_band = None
        RED_BAND = 660
        closest_red_band = None

        for band in self.__get_asset_bands(url, Role.data.value):
            closest_blue_band = update_closest_band(band, BLUE_BAND, closest_blue_band)
            closest_green_band = update_closest_band(band, GREEN_BAND, closest_green_band)
            closest_red_band = update_closest_band(band, RED_BAND, closest_red_band)

        return [closest_red_band["idx"], closest_green_band["idx"], closest_blue_band["idx"]]

    def __check_path__(self, path: str):
        self.__init__()

        if not AccessManager.is_dir(path):
            return False

        for file in AccessManager.listdir(path):
            if not file.is_dir:
                if file.name.endswith(".hsi") and not file.name.endswith("-igm.hsi"):
                    self.hsi_path = file.path
                elif file.name.endswith(".json"):
                    self.metadata_path = file.path
                elif file.name.endswith("-RGB.tif"):
                    self.browse_path = file.path

        return self.hsi_path is not None \
            and self.metadata_path is not None
