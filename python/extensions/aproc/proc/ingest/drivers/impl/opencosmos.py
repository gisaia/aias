import json
from datetime import datetime
import os

import dateutil

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (downsample_image,
                                                             geotiff_to_jpg,
                                                             get_epsg)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):
    configuration: dict = {}

    def __init__(self):
        super().__init__()
        self.data_path = None
        self.main_asset_role = None
        self.tif_paths = []
        self.tci_path = None
        self.pan_path = None
        self.md_path = None
        self.extra_md_path = None
        self.rpc_path = None
        self.thumbnail_path = None
        self.quicklook_path = None
        self.product_types = tuple(Driver.configuration.get('product_types', []))   # e.g. "platero-l1c" or "hammer_l1c"

    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)
        Driver.configuration = configuration

    def identify_assets(self, url: str):
        assets: list[Asset] = []
        ImageDriverHelper.add_archive(assets, url)
        ImageDriverHelper.add_asset(assets, self.md_path, Role.metadata, MimeType.JSON, AssetFormat.json, ResourceType.other)
        if self.extra_md_path:
            asset = Asset(href=self.extra_md_path, size=AccessManager.get_size(self.extra_md_path),
                          roles=[Role.metadata.value], name="metadata.json", type=MimeType.JSON,
                          description="metadata.json", airs__managed=False, asset_format=AssetFormat.json.value, asset_type=ResourceType.other.value)
            assets.append(asset)

        # Main image
        assets.append(Asset(href=self.data_path, size=AccessManager.get_size(self.data_path),
                            roles=list(set([Role.data.value, Role.visual.value, self.main_asset_role])), name=Role.data.value, type=MimeType.GEOTIFF.value,
                            description=Role.data.value, airs__managed=False, asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value))

        if self.thumbnail_path:
            ImageDriverHelper.add_asset(assets, self.thumbnail_path, Role.thumbnail, MimeType.WEBP, AssetFormat.webp, ResourceType.other, airs__managed=True)
        if self.tci_path:
            ImageDriverHelper.add_asset(assets, self.tci_path, Role.data, MimeType.TIFF, AssetFormat.geotiff, ResourceType.gridded)
        if self.pan_path:
            ImageDriverHelper.add_asset(assets, self.pan_path, Role.pan, MimeType.TIFF, AssetFormat.geotiff, ResourceType.gridded)

        for tif_path in self.tif_paths:
            asset = Asset(href=tif_path, size=AccessManager.get_size(tif_path),
                          roles=[Role.data.value, Role.visual.value], name=os.path.basename(tif_path), type=MimeType.TIFF.value,
                          description=os.path.basename(tif_path), airs__managed=False, asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value)
            assets.append(asset)

        if self.rpc_path:
            assets.append(Asset(href=self.rpc_path, size=AccessManager.get_size(self.rpc_path),
                                roles=[Role.rpc.value], name=Role.rpc.value, type=MimeType.TEXT.value,
                                description=Role.rpc.value, airs__managed=False, asset_format=AssetFormat.rpb.value, asset_type=ResourceType.other.value))

        return assets

    def fetch_assets(self, url: str, assets: list[Asset]):
        if self.thumbnail_path:
            thumbnail = ImageDriverHelper.make_local_preview_asset(self, url, self.thumbnail_path, MimeType.PNG, AssetFormat.png, role=Role.thumbnail)
            self.thumbnail_path = thumbnail.href
            assets.append(thumbnail)
        return assets

    def transform_assets(self, url: str, assets: list[Asset]):
        if self.tci_path is not None:
            if AccessManager.is_local(self.tci_path) and Driver.configuration.get('build_overview_when_local', True):
                Driver.LOGGER.debug(f"Building overview for local TIFF {self.tci_path}")
                quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
                geotiff_to_jpg(self.tci_path, Driver.OVERVIEW_FROM_TIFF_PCT, Driver.OVERVIEW_FROM_TIFF_PCT, output_path=quicklook.href, stretch=Driver.configuration.get('overview_stretch', False))
                quicklook.size = AccessManager.get_size(quicklook.href)
                self.quicklook_path = quicklook.href
                assets.append(quicklook)
            elif not AccessManager.is_local(self.tci_path) and Driver.configuration and Driver.configuration.get('build_overview_when_remote', False):
                Driver.LOGGER.debug(f"Building overview for remote TIFF {self.tci_path}")
                overview_folder = self.assets_dir + '/opencosmos/' + self.get_item_id(url) + '/overview'
                AccessManager.makedir(overview_folder)
                overview_path = overview_folder + '/overview.jpg'
                with AccessManager.make_local(self.tci_path) as local_tci_path:
                    quicklook = ImageDriverHelper.prepare_preview_asset(self, overview_path, Role.overview, MimeType.JPG, AssetFormat.jpg)
                    geotiff_to_jpg(local_tci_path, Driver.OVERVIEW_FROM_TIFF_PCT, Driver.OVERVIEW_FROM_TIFF_PCT, output_path=quicklook.href, stretch=Driver.configuration.get('overview_stretch', False))
                    quicklook.size = AccessManager.get_size(quicklook.href)
                    self.quicklook_path = quicklook.href
                    assets.append(quicklook)

        if self.quicklook_path is not None and self.thumbnail_path is None:
            thumbnail_type = MimeType.JPG
            thumbnail_format = AssetFormat.jpg
            if self.quicklook_path.endswith(".png"):
                thumbnail_type = MimeType.PNG
                thumbnail_format = AssetFormat.png
            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, thumbnail_type, thumbnail_format)
            downsample_image(self.quicklook_path, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR)
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)
        return assets

    def load_metadata(self, url: str) -> dict:
        with AccessManager.stream(self.md_path) as fb:
            metadata = json.load(fb)

        return metadata

    def build_core_item(self, url: str, assets: list[Asset], metadata: dict) -> Item:
        geometry = metadata["geometry"]
        bbox = metadata["bbox"]

        coordinates = geometry["coordinates"][0]
        # Remove altitude
        for idx, coords in enumerate(coordinates):
            coordinates[idx] = coords[:2]

        centroid = [
            (bbox[0] + bbox[2]) / 2.0,
            (bbox[1] + bbox[3]) / 2.0
        ]

        def parse_dt(dt_str):
            if not dt_str:
                return None
            if dt_str.endswith("Z"):
                dt_str = dt_str[:-1] + "+00:00"
            return datetime.fromisoformat(dt_str).replace(tzinfo=None)

        props = metadata.get("properties", {})
        
        start_dt_str = props.get("start_datetime")
        if start_dt_str is not None:
            start_datetime = dateutil.parser.parse(start_dt_str)
        else:
            start_datetime = None

        end_dt_str = props.get("end_datetime")
        if end_dt_str is not None:
            end_datetime = parse_dt(end_dt_str)
        else:
            end_datetime = None

        item = Item(
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=dateutil.parser.parse(props.get("datetime")),
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                constellation=props.get("constellation", "opencosmos").upper(),
                sensor_type=SensorType.OPTIC.value,
                item_format=ItemFormat.opencosmos.value,
                item_type=ResourceType.gridded.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.optic.value
            ),
            assets={asset.name: asset for asset in assets}
        )
        source_assets = metadata.get("assets", {})
        for a in source_assets:
            if a in item.assets:
                item.assets[a].description = source_assets[a].get("description", item.assets[a].description)
                item.assets[a].title = source_assets[a].get("title", item.assets[a].title)
                item.assets[a].type = source_assets[a].get("type", item.assets[a].type)
        return item

    def add_major_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        props = metadata.get("properties", {})
        item.properties.secondary_id = metadata.get("id")
        item.properties.satellite = props.get("platform", None)
        item.properties.gsd = props.get("gsd", None)
        item.properties.proj__epsg = get_epsg(AccessManager.get_gdal_proj(self.data_path))
        item.eo__cloud_cover = props.get("eo:cloud_cover", None)
        return item

    def add_minor_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        props = metadata.get("properties", {})

        item.processing__level = props.get("processing:level", [None])[0],
        item.properties.instrument = item.properties.satellite
        item.properties.sensor = item.properties.satellite

        return item

    def find_file(self, directory, filename):
        for f in AccessManager.listdir(directory):
            if filename.lower() == f.name.lower():
                return f.path
            if f.is_dir:
                result = self.find_file(f.path, filename)
                if result is not None:
                    return result
        return None
        
    def __check_path__(self, path: str):
        self.__init__()
        data_path = None
        product_type = None
        if AccessManager.is_dir(path):
            contents = AccessManager.listdir(path)
            for f in contents:
                if f.is_dir and f.name.lower() == "catalog" and self.md_path is None:
                    self.md_path = self.find_file(f.path, "stac_item.json")
                if f.name.lower().startswith(self.product_types):
                    product_type = f.name

            if self.md_path is not None and product_type is not None:
                common_path = self.md_path.removeprefix(path).removeprefix("/").removeprefix("catalog").removeprefix("/").removesuffix("stac_item.json")
                data_path = os.path.join(path, common_path)
                if AccessManager.exists(data_path):
                    for f in AccessManager.listdir(data_path):
                        if not f.is_dir and f.name.lower().endswith((".tif", ".tiff")):
                            if f.name.lower().startswith("tci"):
                                self.tci_path = f.path
                            elif f.name.lower().startswith("pan"):
                                self.pan_path = f.path
                            else:
                                self.tif_paths.append(f.path)
                        elif not f.is_dir and f.name.lower().endswith("metadata.json"):
                            self.extra_md_path = f.path
                        elif not f.is_dir and f.name.lower().endswith("rpc.txt"):
                            self.rpc_path = f.path
                        elif not f.is_dir and (f.name.lower().endswith("thumbnail.webp")):
                            self.thumbnail_path = f.path
            if self.md_path is not None and (self.tif_paths or self.tci_path is not None or self.pan_path is not None):
                self.data_path = self.tci_path if self.tci_path is not None else (self.pan_path if self.pan_path is not None else self.tif_paths[0])
                self.main_asset_role = Role.tci.value if self.tci_path is not None else (Role.pan.value if self.pan_path is not None else Role.data.value)
                return True
        return False
