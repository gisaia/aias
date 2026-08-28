import json
import re
from datetime import datetime
from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType, Band)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):

    def __init__(self):
        super().__init__()
        self.md_path = None
        self.bands_path = []
        self.quicklook_path = None
        self.thumbnail_path = None
        self.tif_pattern = re.compile(r'_B([1-9]|1[01])\.TIF$', re.IGNORECASE)
        self.main_asset_name = None
        self.gsd = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        ImageDriverHelper.init(Driver, configuration)

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets: list[Asset] = []
        # Add the archive asset
        ImageDriverHelper.add_archive(assets, url)
        # Load metadata JSON
        with AccessManager.stream(self.md_path) as fb:
            md = json.load(fb)
        asset_dict = md.get("assets", {})
        for band in self.bands_path:
            file_name = band.get("name")
            file_path = band.get("path")
            for key, obj in asset_dict.items():
                href = obj.get("href", "")
                if file_name not in href:
                    continue
                # Build eo bands
                bands = []
                for b in obj.get("eo:bands", []):
                    name = b.get("name")
                    common_name = b.get("common_name")
                    if not (name or common_name):
                        continue
                    gsd = b.get("gsd")
                    if gsd is not None:
                        if self.gsd is None or gsd < self.gsd:
                            self.gsd = gsd
                            self.main_asset_name = common_name
                    bands.append(
                        Band(
                            name=name,
                            eo__common_name=common_name,
                            eo__center_wavelength=b.get("center_wavelength"),
                        )
                    )
                assets.append(
                    Asset(
                        href=file_path,
                        size=AccessManager.get_size(file_path),
                        roles=[Role.data],
                        name=key,
                        type=MimeType.GEOTIFF,
                        description=obj.get("description"),
                        airs__managed=False,
                        asset_format=AssetFormat.geotiff,
                        asset_type=ResourceType.gridded,
                        eo__bands=bands,
                        eo__gsd=gsd
                    )
                )

        # Add metadata assets
        ImageDriverHelper.add_asset(
            assets, self.md_path, Role.metadata, MimeType.JSON, AssetFormat.json, ResourceType.other
        )
        ImageDriverHelper.add_asset(
            assets, self.quicklook_path, Role.overview, MimeType.JPEG, AssetFormat.jpg, ResourceType.gridded, True
        )
        ImageDriverHelper.add_asset(
            assets, self.thumbnail_path, Role.thumbnail, MimeType.JPEG, AssetFormat.jpg, ResourceType.gridded, True
        )

        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    def load_metadata(self, url: str) -> object:
        with AccessManager.stream(self.md_path) as fb:
            md = json.load(fb)
        return md

    def build_core_item(self, url: str, assets: list[Asset], metadata: dict) -> Item:
        bbox = metadata.get("bbox", None)
        if bbox and len(bbox) >= 4:
            centroid_lon = (bbox[0] + bbox[2]) / 2
            centroid_lat = (bbox[1] + bbox[3]) / 2
            centroid = [centroid_lon, centroid_lat]
        else:
            centroid = None
        properties = metadata.get("properties", {})
        date_time_str = properties.get("datetime", None)
        date_time = (
            datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            if date_time_str
            else None
        )
        item = Item(
            id=self.get_item_id(url),
            geometry=metadata.get("geometry", None),
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                constellation='LANDSAT',
                sensor_type=SensorType.OPTIC.value,
                secondary_id=metadata.get("id", None),
                item_format=ItemFormat.landsat,
                item_type=ResourceType.gridded.value,
                main_asset_format=AssetFormat.geotiff,
                main_asset_name=self.main_asset_name,
                observation_type=ObservationType.optic
            ),
            assets={asset.name: asset for asset in assets}
        )

        return item

    def add_major_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        properties = metadata.get("properties", {})
        if self.gsd is not None:
            item.properties.gsd = self.gsd
        item.properties.processing__level = properties.get("landsat:correction", None)
        item.properties.proj__epsg = properties.get("proj:epsg", None)
        item.properties.satellite = properties.get("platform", None)
        return item

    def add_minor_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        properties = metadata.get("properties", {})
        instruments = properties.get("instruments", [])
        platform = properties.get("platform", None)
        if len(instruments) > 0:
            item.properties.instrument = instruments[0]
        item.properties.platform = platform
        item.properties.view__off_nadir = properties.get("view:off_nadir", None)
        item.properties.view__sun_azimuth = properties.get("view:sun_azimuth", None)
        item.properties.view__sun_elevation = properties.get("view:sun_elevation", None)
        item.properties.proj__shape = properties.get("proj:shape", None)
        item.properties.eo__cloud_cover = properties.get("eo:cloud_cover", None)
        item.properties.sensor = platform
        return item

    def __check_path__(self, path: str):
        self.__init__()
        if AccessManager.is_dir(path):
            for file in AccessManager.listdir(path):
                if file.name.startswith("LC09") or file.name.startswith("LC08"):
                    if file.name.endswith("_thumb_large.jpeg"):
                        self.quicklook_path = file.path
                    elif file.name.endswith("_thumb_small.jpeg"):
                        self.thumbnail_path = file.path
                    elif self.tif_pattern.search(file.name):
                        self.bands_path.append({"path": file.path, "name": file.name})
                    elif file.name.endswith("_stac.json"):
                        self.md_path = file.path
            return self.md_path is not None \
                and self.quicklook_path is not None \
                and self.thumbnail_path is not None \
                and len(self.bands_path) > 0
        return False
