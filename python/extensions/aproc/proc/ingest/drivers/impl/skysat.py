import json
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (downsample_image,
                                                             geotiff_to_jpg, get_bbox, get_centroid,
                                                             get_epsg)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):
    def __init__(self):
        super().__init__()
        self.md_path = None
        self.sr_path = None
        self.visual_tif_path = None
        self.thumbnail_path = None
        # Mask with clear/snow/shadow/haze/cloud/confidence/...
        self.udm_path = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        ImageDriverHelper.add_archive(assets, url)

        ImageDriverHelper.add_asset(assets, self.sr_path, Role.data,
                                    MimeType.TIFF, AssetFormat.geotiff, ResourceType.gridded)
        ImageDriverHelper.add_asset(assets, self.md_path, Role.metadata,
                                    MimeType.JSON, AssetFormat.json, ResourceType.other)
        assets.append(Asset(href=self.udm_path, size=AccessManager.get_size(self.udm_path),
                            roles=[Role.snow_ice.value, Role.cloud.value, Role.cloud_shadow.value],
                            name="UDM2", type=MimeType.GEOTIFF.value, description="UDM2", airs__managed=False,
                            asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value))

        if self.visual_tif_path:
            ImageDriverHelper.add_asset(assets, self.visual_tif_path, Role.visual,
                                        MimeType.TIFF, AssetFormat.geotiff, ResourceType.gridded)

        if self.thumbnail_path:
            ImageDriverHelper.add_asset(assets, self.thumbnail_path, Role.thumbnail,
                                        MimeType.PNG, AssetFormat.png, ResourceType.other, airs__managed=True)

        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if self.visual_tif_path:
            bands = [1, 2, 3]
            tif_path = self.visual_tif_path
            stretch = False
        else:
            bands = [3, 2, 1]
            tif_path = self.sr_path
            stretch = True

        quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
        geotiff_to_jpg(tif_path, 10, 10, output_path=quicklook.href,
                       bands_list=bands, stretch=stretch)
        quicklook.size = AccessManager.get_size(quicklook.href)
        assets.append(quicklook)

        if self.thumbnail_path is None:
            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.JPG, AssetFormat.jpg)
            downsample_image(quicklook.href, thumbnail.href, 4)
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        with AccessManager.stream(self.md_path) as fb:
            md = json.load(fb)

        geometry = md["geometry"]
        centroid = get_centroid(geometry)
        bbox = get_bbox(geometry["coordinates"][0])

        properties = md["properties"]
        date_time = datetime.strptime(properties["acquired"], "%Y-%m-%dT%H:%M:%S.%fZ")
        eo__cloud_cover = properties["cloud_cover"]
        eo__snow_cover = properties["snow_ice_percent"]
        gsd = properties["gsd"]

        sattelite = properties["satellite_id"]
        view__azimuth = properties["satellite_azimuth"]
        view__sun_azimuth = properties["sun_azimuth"]
        view__sun_elevation = properties["sun_elevation"]

        item = Item(
            id=self.get_item_id(url),
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                eo__cloud_cover=eo__cloud_cover,
                eo__snow_cover=eo__snow_cover,
                gsd=gsd,
                proj__epsg=get_epsg(AccessManager.get_gdal_proj(self.sr_path)),
                instrument=sattelite,
                constellation="SkySat",
                satellite=sattelite,
                sensor=sattelite,
                sensor_type=SensorType.OPTIC.value,
                view__azimuth=view__azimuth,
                view__sun_azimuth=view__sun_azimuth,
                view__sun_elevation=view__sun_elevation,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.skysat.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.optic.value
            ),
            assets=dict([(asset.name, asset) for asset in assets])
        )

        return item

    def __check_path__(self, path: str):
        self.__init__()

        if not AccessManager.is_dir(path):
            return False

        for file in AccessManager.listdir(path):
            if file.is_dir:
                continue

            if file.name.find("_analytic_SR_") != -1 and file.name.endswith(".tif"):
                self.sr_path = file.path
            elif file.name.endswith("_metadata.json"):
                self.md_path = file.path
            elif file.name.find("_udm2") != -1 and file.name.endswith(".tif"):
                self.udm_path = file.path
            elif file.name.find("_visual_") != -1 and file.name.endswith(".thumbnail.png"):
                self.thumbnail_path = file.path
            elif file.name.find("_visual_") != -1 and file.name.endswith(".tif"):
                self.visual_tif_path = file.path

        return self.sr_path is not None \
            and self.md_path is not None \
            and self.udm_path is not None
