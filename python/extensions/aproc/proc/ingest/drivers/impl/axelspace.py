import json
import os
from datetime import datetime
from math import sqrt
import tempfile

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (downsample_image)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):
    configuration: dict = {}

    def __init__(self):
        super().__init__()

        self.tif_paths: list[str] = []
        self.md_path = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)
        Driver.configuration = configuration or {}

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        ImageDriverHelper.add_archive(assets, url)

        ImageDriverHelper.add_asset(assets, self.md_path, Role.metadata,
                                    MimeType.JSON, AssetFormat.json, ResourceType.other)

        for tif in self.tif_paths:
            asset = Asset(href=tif, size=AccessManager.get_size(tif),
                          roles=[Role.data.value, Role.visual.value], name=self.__get_asset_name(tif, Role.data), type=MimeType.TIFF.value,
                          description=Role.data.value, airs__managed=False, asset_format=AssetFormat.geotiff, asset_type=ResourceType.gridded)

            # Get asset's GSD
            tile_md = self.__load_tile_md(tif)
            if tile_md.get("rowGSD", None) and tile_md.get("columnGSD", None):
                asset.eo__gsd = sqrt(tile_md["rowGSD"]**2 + tile_md["columnGSD"]**2)

            assets.append(asset)
        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if IngestDriver.must_build_preview(Driver.configuration, url):
            from osgeo import gdal
            gdal.SetConfigOption('CPL_TMPDIR', tempfile.gettempdir())
            # Minify all the tiffs
            minified_tiffs = []
            options = gdal.TranslateOptions(format="GTiff", bandList=[1, 2, 3], widthPct=Driver.OVERVIEW_FROM_TIFF_PCT, heightPct=Driver.OVERVIEW_FROM_TIFF_PCT)
            for tif in self.tif_paths:
                mini_tif = os.path.join(AccessManager.tmp_dir, os.path.basename(tif))
                Driver.LOGGER.debug(f"Minifying {tif} to {Driver.OVERVIEW_FROM_TIFF_PCT}% in dir {AccessManager.tmp_dir}")
                gdal.Translate(mini_tif, AccessManager.get_gdal_src(tif), options=options)
                if not AccessManager.exists(mini_tif):
                    raise DriverException(f"Failed to minify {tif} to {Driver.OVERVIEW_FROM_TIFF_PCT}% in dir {AccessManager.tmp_dir}")
                minified_tiffs.append(mini_tif)

            # Create quicklook
            quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
            Driver.LOGGER.debug(f"Creating quicklook {quicklook.href} from minified tiffs {minified_tiffs}")
            gdal.Warp(quicklook.href, minified_tiffs, format="JPEG")
            if not AccessManager.exists(quicklook.href):
                raise DriverException(f"Failed to create quicklook {quicklook.href} from minified tiffs {minified_tiffs}")
            quicklook.size = AccessManager.get_size(quicklook.href)
            Driver.LOGGER.debug(f"Quicklook {quicklook.href} created with size {quicklook.size}")
            assets.append(quicklook)

            # Remove minified tiffs
            for t in minified_tiffs:
                AccessManager.clean(t)

            # Create thumbnail
            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.JPG, AssetFormat.jpg)
            Driver.LOGGER.debug(f"Creating thumbnail {thumbnail.href} from quicklook {quicklook.href}")
            downsample_image(quicklook.href, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR)
            if not AccessManager.exists(thumbnail.href):
                raise DriverException(f"Failed to create thumbnail {thumbnail.href} from quicklook {quicklook.href}")
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            Driver.LOGGER.debug(f"Thumbnail {thumbnail.href} created with size {thumbnail.size}")

            assets.append(thumbnail)

        return assets

    def load_metadata(self, url: str) -> dict:
        with AccessManager.stream(self.md_path) as fb:
            md = json.load(fb)

        return md

    def build_core_item(self, url: str, assets: list[Asset], metadata: dict) -> Item:
        from pyproj import Transformer
        from shapely import union_all, Polygon, to_geojson

        try:
            # The extent of the archive is the union of all extents
            epsg = metadata["productMetadata"]["spatialReferenceSystem"]["EPSGCode"]
            transformer = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4326")

            geometries = []
            for tif in self.tif_paths:
                tile_md = self.__load_tile_md(tif)

                # Convert geometry to correct projection
                coordinates = tile_md["imageLocation"]["coordinates"][0]
                xx, yy = transformer.transform([c[0] for c in coordinates], [c[1] for c in coordinates])
                geometries.append(Polygon([[y, x] for (x, y) in zip(xx, yy)]))

            merged_polygons: Polygon = union_all(geometries).normalize()
            centroid = merged_polygons.centroid.xy
            bbox = merged_polygons.bounds

            start_date_time = self._parse_dt(metadata["EOMetadata"]["acquisitionDateTime"]["acquisitionStartDateTime"])
            end_date_time = self._parse_dt(metadata["EOMetadata"]["acquisitionDateTime"]["acquisitionEndDateTime"])

        except KeyError as ke:
            raise DriverException(f"Invalid metadata file {self.md_path}: a key is missing: {ke.args[0]}")

        item = Item(
            geometry=json.loads(to_geojson(merged_polygons)),
            bbox=bbox,
            centroid=[centroid[0][0], centroid[1][0]],
            properties=Properties(
                datetime=start_date_time,
                start_datetime=start_date_time,
                end_datetime=end_date_time,
                constellation="Axelspace",
                sensor_type=SensorType.OPTIC.value,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.axelspace.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=self.__get_asset_name(self.tif_paths[0], Role.data),
                observation_type=ObservationType.optic.value
            ),
            assets={asset.name: asset for asset in assets}
        )

        return item

    def add_major_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        # Item's gsd is the minimum of all assets gsd
        gsd = None
        for asset in item.assets.values():
            if Role.data.value in asset.roles:
                if gsd is None:
                    gsd = asset.eo__gsd
                elif asset.eo__gsd is not None:
                    gsd = min(asset.eo__gsd, gsd)

        item.properties.satellite = metadata.get("EOMetadata", {}).get("satelliteName", None)
        item.properties.instrument = item.properties.satellite
        item.properties.sensor = item.properties.satellite

        item.properties.proj__epsg = metadata.get("productMetadata", {}).get("spatialReferenceSystem", {}).get("EPSGCode", None)

        return item

    def add_minor_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        item.properties.view__sun_elevation = metadata.get("EOMetadata", {}).get("solarElevationAngleNominal", None)
        item.properties.view__sun_azimuth = metadata.get("EOMetadata", {}).get("solarAzimuthAngleNominal", None)

        item.properties.acq__acquisition_orbit_direction = metadata.get("EOMetadata", {}).get("orbitDirection", None)
        if item.properties.acq__acquisition_orbit_direction is not None:
            item.properties.acq__acquisition_orbit_direction = item.properties.acq__acquisition_orbit_direction.upper()

        return item

    def __check_path__(self, path: str):
        self.__init__()

        if AccessManager.is_dir(path):
            for f in AccessManager.listdir(path):
                if not f.is_dir:
                    # Only keep one md_path
                    if self.md_path is None and f.name.lower().endswith("_udm_metadata.json"):
                        self.md_path = f.path
                    # Only keep the TCI tif. There should be a metadata UDM file associated
                    if f.name.lower().endswith("tci.tif") and AccessManager.exists(f.path.replace("tci.tif", "msi_udm_metadata.json")):
                        self.tif_paths.append(f.path)

            return self.md_path is not None \
                and len(self.tif_paths) > 0
        return False

    def __get_asset_name(self, path: str, role: Role):
        file_name = os.path.basename(path)

        # Asset name is id_role
        return f"{role.value}_{file_name.split('_')[1]}"

    def __load_tile_md(self, tif: str) -> dict:
        tile_md_file = tif.replace("tci.tif", "msi_udm_metadata.json")
        with AccessManager.stream(tile_md_file) as fb:
            tile_md = json.load(fb)["imageTileMetadata"]

        return tile_md

    def _parse_dt(self, value: str) -> datetime:
        for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                pass
        raise ValueError(f"Unsupported datetime format: {value}")
