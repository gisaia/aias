import json
import os
from datetime import datetime
from math import sqrt

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (downsample_image,
                                                             geotiff_to_jpg,
                                                             get_bbox,
                                                             get_centroid,
                                                             get_epsg)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):
    def __init__(self):
        super().__init__()

        self.tif_path = None
        self.udm_path = None
        self.md_path = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        assets.append(
            Asset(
                href=url,
                roles=[Role.archive.value],
                name=Role.archive.value,
                type=MimeType.TIFF.value,
                description=Role.archive.value,
                airs__managed=False,
                asset_format=AssetFormat.geotiff.value
            )
        )

        ImageDriverHelper.add_asset(assets, self.tif_path, Role.data,
                                    MimeType.TIFF, AssetFormat.geotiff, ResourceType.gridded)
        ImageDriverHelper.add_asset(assets, self.md_path, Role.metadata,
                                    MimeType.JSON, AssetFormat.json, ResourceType.other)
        ImageDriverHelper.add_asset(assets, self.udm_path, Role.cloud,
                                    MimeType.TIFF, AssetFormat.geotiff, ResourceType.gridded)
        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if AccessManager.is_local(self.tif_path):
            quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
            geotiff_to_jpg(self.tif_path, Driver.OVERVIEW_FROM_TIFF_PCT, Driver.OVERVIEW_FROM_TIFF_PCT, output_path=quicklook.href, bands_list=[1, 2, 3])
            quicklook.size = AccessManager.get_size(quicklook.href)
            assets.append(quicklook)

            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.JPG, AssetFormat.jpg)
            downsample_image(quicklook.href, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR)
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)

        return assets

    def load_metadata(self, url: str) -> dict:
        with AccessManager.stream(self.md_path) as fb:
            md = json.load(fb)

        return md

    def build_core_item(self, url: str, assets: list[Asset], metadata: dict) -> Item:
        from pyproj import Transformer

        try:
            tile_md = metadata["imageTileMetadata"][os.path.basename(self.tif_path)]

            # Convert geometry to correct projection
            epsg = metadata["productMetadata"]["spatialReferenceSystem"]["EPSGCode"]
            transformer = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4326")
            coordinates = tile_md["imageLocation"]["coordinates"][0]
            xx, yy = transformer.transform([c[0] for c in coordinates], [c[1] for c in coordinates])
            geometry = {"type": "Polygon", "coordinates": [[[y, x] for (x, y) in zip(xx, yy)]]}

            centroid = get_centroid(geometry)
            bbox = get_bbox(geometry["coordinates"][0])

            start_date_time = metadata["EOMetadata"]["acquisitionDateTime"]["acquisitionStartDateTime"]
            start_date_time = datetime.strptime(start_date_time, "%Y-%m-%dT%H:%M:%S%z")
            end_date_time = metadata["EOMetadata"]["acquisitionDateTime"]["acquisitionEndDateTime"]
            end_date_time = datetime.strptime(end_date_time, "%Y-%m-%dT%H:%M:%S.%f%z")

        except KeyError as ke:
            raise DriverException(f"Invalid metadata file {self.md_path}: a key is missing: {ke.args[0]}")

        item = Item(
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=start_date_time,
                start_datetime=start_date_time,
                end_datetime=end_date_time,
                constellation="Axelspace",
                sensor_type=SensorType.OPTIC.value,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.axelspace.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.optic.value
            ),
            assets={asset.name: asset for asset in assets}
        )

        return item

    def add_major_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        try:
            # Is necessarily a dictionary as the core item was built using it
            tile_md = metadata["imageTileMetadata"][os.path.basename(self.tif_path)]

            if tile_md.get("rowGSD", None) and tile_md.get("columnGSD", None):
                item.properties.gsd = sqrt(tile_md["rowGSD"]**2 + tile_md["columnGSD"]**2)

            item.properties.satellite = metadata.get("EOMetadata", {}).get("satelliteName", None)
            item.properties.instrument = item.properties.satellite
            item.properties.sensor = item.properties.satellite
        except KeyError as ke:
            raise DriverException(f"Invalid metadata file {self.md_path}: a key is missing: {ke.args[0]}")

        item.properties.proj__epsg = get_epsg(AccessManager.get_gdal_proj(self.tif_path))

        return item

    def add_minor_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        tile_md = metadata["imageTileMetadata"][os.path.basename(self.tif_path)]
        item.properties.eo__cloud_cover = tile_md.get("cloudCoverPercentage", None)

        item.properties.view__sun_elevation = metadata.get("EOMetadata", {}).get("solarElevationAngleNominal", None)
        item.properties.view__sun_azimuth = metadata.get("EOMetadata", {}).get("solarAzimuthAngleNominal", None)

        item.properties.acq__acquisition_orbit_direction = metadata.get("EOMetadata", {}).get("orbitDirection", None)

        return item

    def __check_path__(self, path: str):
        self.__init__()

        file_name = os.path.basename(path)

        if file_name.endswith(".tif") and file_name.find("_UDM_") < 0 and AccessManager.is_file(path):
            self.tif_path = path
            dir_name = AccessManager.dirname(path)

            core = "_".join(file_name.removesuffix(".tif").split("_")[:-1])
            tile = file_name.removesuffix(".tif").split("_")[-1]

            md_path = os.path.join(dir_name, core + "_metadata.json")
            if AccessManager.exists(md_path):
                self.md_path = md_path

            udm_path = os.path.join(dir_name, core + "_UDM_" + tile + ".tif")
            if AccessManager.exists(udm_path):
                self.udm_path = udm_path

            return self.tif_path is not None \
                and self.md_path is not None \
                and self.udm_path is not None
        return False
