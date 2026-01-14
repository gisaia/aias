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
from extensions.aproc.proc.ingest.drivers.impl.utils import (downsample_image, geotiff_to_jpg,
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
        ImageDriverHelper.add_archive(assets, url)

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
            downsample_image(quicklook.href, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR
                             )
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)

        return assets

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        from pyproj import Transformer

        with AccessManager.stream(self.md_path) as fb:
            md = json.load(fb)

        try:
            tile_md = md["imageTileMetadata"][os.path.basename(self.tif_path)]

            # Convert geometry to correct projection
            epsg = md["productMetadata"]["spatialReferenceSystem"]["EPSGCode"]
            transformer = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4326")
            coordinates = tile_md["imageLocation"]["coordinates"][0]
            xx, yy = transformer.transform([c[0] for c in coordinates], [c[1] for c in coordinates])
            geometry = {"type": "Polygon", "coordinates": [[[y, x] for (x, y) in zip(xx, yy)]]}

            centroid = get_centroid(geometry)
            bbox = get_bbox(geometry["coordinates"][0])

            start_date_time = md["EOMetadata"]["acquisitionDateTime"]["acquisitionStartDateTime"]
            start_date_time = datetime.strptime(start_date_time, "%Y-%m-%dT%H:%M:%S%z")
            end_date_time = md["EOMetadata"]["acquisitionDateTime"]["acquisitionEndDateTime"]
            end_date_time = datetime.strptime(end_date_time, "%Y-%m-%dT%H:%M:%S.%f%z")
            eo__cloud_cover = tile_md["cloudCoverPercentage"]
            gsd = sqrt(tile_md["rowGSD"]**2 + tile_md["columnGSD"]**2)

            satellite = md["EOMetadata"]["satelliteName"]
            view__sun_elevation = md["EOMetadata"]["solarElevationAngleNominal"]
            view__sun_azimuth = md["EOMetadata"]["solarAzimuthAngleNominal"]

            orbit_direction = md["EOMetadata"]["orbitDirection"]
        except KeyError as ke:
            raise DriverException(f"Invalid metadata file {self.md_path}: a key is missing: {ke.args[0]}")

        item = Item(
            id=self.get_item_id(url),
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=start_date_time,
                start_datetime=start_date_time,
                end_datetime=end_date_time,
                eo__cloud_cover=eo__cloud_cover,
                gsd=gsd,
                proj__epsg=get_epsg(AccessManager.get_gdal_proj(self.tif_path)),
                instrument=satellite,
                constellation="Axelspace",
                satellite=satellite,
                sensor=satellite,
                sensor_type=SensorType.OPTIC.value,
                view__sun_azimuth=view__sun_azimuth,
                view__sun_elevation=view__sun_elevation,
                acq__acquisition_orbit_direction=orbit_direction,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.axelspace.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.optic.value
            ),
            assets={asset.name: asset for asset in assets}
        )

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
