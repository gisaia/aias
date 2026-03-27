import os
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import subprocess

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    downsample_image, find_or_none, geotiff_to_jpg, get_bbox, get_centroid, get_epsg, get_epsg_from_gdal_info_gcps)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):

    configuration: dict = {}

    def __init__(self):
        super().__init__()
        self.xml_path = None

        self.mux_rcps_path = None
        self.mux_xml_path = None
        self.mux_tif_path = None
        self.mux_jpg_path = None

        self.pan_rcps_path = None
        self.pan_xml_path = None
        self.pan_tif_path = None
        self.pan_jpg_path = None

        self.cloud_shape_path = None
        self.shape_path = None
        self.rpcs_path = None
        self.quicklook_path = None


    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)
        Driver.configuration = configuration

    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        ImageDriverHelper.add_archive(assets, url)

        # Images
        assets.append(Asset(href=self.mux_tif_path, size=AccessManager.get_size(self.mux_tif_path),
                            roles=[Role.data.value, Role.visual.value], name=Role.data.value, type=MimeType.GEOTIFF.value,
                            description=Role.data.value, airs__managed=False, asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value))

        if self.pan_tif_path:
            assets.append(Asset(href=self.pan_tif_path, size=AccessManager.get_size(self.pan_tif_path),
                                roles=[Role.data.value, Role.pan_sharpened.value], name=Role.pan_sharpened.value, type=MimeType.GEOTIFF.value,
                                description=Role.data.value, airs__managed=False, asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value))

        if self.mux_jpg_path:
            assets.append(Asset(href=self.mux_jpg_path, size=AccessManager.get_size(self.mux_jpg_path),
                                roles=[Role.overview.value, Role.visual.value], name=Role.overview.value + "-mux", type=MimeType.JPEG.value,
                                description=Role.overview.value, airs__managed=False, asset_format=AssetFormat.jpg.value, asset_type=ResourceType.gridded.value))

        if self.pan_jpg_path:
            assets.append(Asset(href=self.pan_jpg_path, size=AccessManager.get_size(self.pan_jpg_path),
                                roles=[Role.overview.value, Role.pan_sharpened.value], name=Role.overview.value + "-pan", type=MimeType.JPEG.value,
                                description=Role.overview.value, airs__managed=False, asset_format=AssetFormat.jpg.value, asset_type=ResourceType.gridded.value))
        # Metadata
        if self.xml_path:
            assets.append(Asset(href=self.xml_path, size=AccessManager.get_size(self.xml_path),
                                roles=[Role.metadata.value], name=Role.metadata.value, type=MimeType.XML.value,
                                description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.xml.value, asset_type=ResourceType.other.value))

        if self.mux_xml_path:
            assets.append(Asset(href=self.mux_xml_path, size=AccessManager.get_size(self.mux_xml_path),
                                roles=[Role.metadata.value], name=Role.metadata.value + "-mux", type=MimeType.XML.value,
                                description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.xml.value, asset_type=ResourceType.other.value))

        if self.pan_xml_path:
            assets.append(Asset(href=self.pan_xml_path, size=AccessManager.get_size(self.pan_xml_path),
                                roles=[Role.metadata.value], name=Role.metadata.value + "-pan", type=MimeType.XML.value,
                                description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.xml.value, asset_type=ResourceType.other.value))

        # RPCs
        if self.mux_rcps_path:
            assets.append(Asset(href=self.mux_rcps_path, size=AccessManager.get_size(self.mux_rcps_path),
                                roles=[Role.rpc.value], name=os.path.basename(self.mux_rcps_path), type=MimeType.TEXT.value,
                                description=Role.rpc.value, airs__managed=False, asset_format=AssetFormat.rpb.value, asset_type=ResourceType.other.value))

        if self.pan_rcps_path:
            assets.append(Asset(href=self.pan_rcps_path, size=AccessManager.get_size(self.pan_rcps_path),
                                roles=[Role.rpc.value], name=os.path.basename(self.pan_rcps_path), type=MimeType.TEXT.value,
                                description=Role.rpc.value, airs__managed=False, asset_format=AssetFormat.rpb.value, asset_type=ResourceType.other.value))

        # SHAPE Extent
        if self.shape_path:
            assets.append(Asset(href=self.shape_path, size=AccessManager.get_size(self.shape_path),
                                roles=[Role.extent.value], name=os.path.basename(self.shape_path), type=MimeType.SHP.value,
                                description=Role.extent.value, airs__managed=False, asset_format=AssetFormat.shape.value, asset_type=ResourceType.vector.value))

        # SHAPE Clouds
        if self.cloud_shape_path:
            assets.append(Asset(href=self.cloud_shape_path, size=AccessManager.get_size(self.cloud_shape_path),
                                roles=[Role.cloud.value, Role.mask.value], name=os.path.basename(self.cloud_shape_path), type=MimeType.SHP.value,
                                description=Role.cloud.value, airs__managed=False, asset_format=AssetFormat.shape.value, asset_type=ResourceType.vector.value))

        return assets

    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if self.quicklook_path:
            quicklook = ImageDriverHelper.make_local_overview_asset(self, url, self.quicklook_path, MimeType.JPG, AssetFormat.jpg)
            self.quicklook_path = quicklook.href
            assets.append(quicklook)
        return assets

    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        image_for_quicklook = self.mux_jpg_path if self.mux_jpg_path else self.pan_jpg_path if self.pan_jpg_path else self.mux_tif_path if self.mux_tif_path else self.pan_tif_path if self.pan_tif_path else None
        if self.quicklook_path is None and image_for_quicklook and AccessManager.is_local(image_for_quicklook) and Driver.configuration.get('build_overview_when_local', True):
            Driver.LOGGER.debug(f"Use {image_for_quicklook} for quicklook")
            quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
            geotiff_to_jpg(image_for_quicklook, Driver.OVERVIEW_FROM_TIFF_PCT, Driver.OVERVIEW_FROM_TIFF_PCT, quicklook.href, stretch=Driver.configuration.get('overview_stretch', False))
            quicklook.size = AccessManager.get_size(quicklook.href)
            self.quicklook_path = quicklook.href
            assets.append(quicklook)
        elif Driver.configuration and Driver.configuration.get('build_overview_when_remote', False):
            Driver.LOGGER.debug(f"Building overview for remote {image_for_quicklook}")
            overview_folder = self.assets_dir + '/superview/' + self.get_item_id(url) + '/overview'
            AccessManager.makedir(overview_folder)
            overview_path = overview_folder + '/overview.jpg'
            # File is processed locally as it significantly speeds up processing time
            with AccessManager.make_local(image_for_quicklook) as local_big_preview_path:
                overview = ImageDriverHelper.prepare_preview_asset(self, overview_path, Role.overview, MimeType.JPG, AssetFormat.jpg)
                geotiff_to_jpg(local_big_preview_path, Driver.OVERVIEW_FROM_LARGE_TIFF_PCT, Driver.OVERVIEW_FROM_LARGE_TIFF_PCT, overview.href, [1, 1, 1], Driver.configuration.get('overview_stretch', True))
                overview.size = AccessManager.get_size(overview.href)
                self.quicklook_path = overview.href
                assets.append(overview)
        else:
            Driver.LOGGER.debug("Skipping overview generation for TCI {}".format(self.big_preview_path))

        if self.quicklook_path is not None:
            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.JPG, AssetFormat.jpg)
            downsample_image(self.quicklook_path, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR)
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)
        return assets

    def load_metadata(self, url: str) -> object:
        with AccessManager.make_local(self.xml_path) as local_md_path:
            tree = ET.parse(local_md_path)
            root = tree.getroot()

        return root

    def build_core_item(self, url: str, assets: list[Asset], metadata: ET.Element) -> Item:

        geometry = ImageDriverHelper.gdal_geometry(self, self.mux_tif_path)
        Driver.LOGGER.debug(f"Extracted geometry for item {url}: {geometry}")
        if geometry is None:
            Driver.LOGGER.error(f"No geometry found for item {url}")
            raise DriverException(f"Missing required 'geometry' for {url}")

        bbox = get_bbox(geometry["coordinates"][0])

        centroid = metadata.get("properties", {}).get("proj:centroid")
        if centroid is None and geometry is not None:
            centroid = get_centroid(geometry)

        start_time_str = find_or_none(metadata, "StartTime")
        end_time_str = find_or_none(metadata, "EndTime")
        end_time = None
        if start_time_str:
            start_time = int(datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S").timestamp())
            date_time = start_time
        else:
            Driver.LOGGER.error(f"No date time found for item {url}")
            raise DriverException(f"Missing required 'StartTime' for {url}")
        if end_time_str:
            end_time = int(datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S").timestamp())

        constellation = find_or_none(metadata, "SatelliteID")

        item = Item(
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                start_datetime=start_time,
                end_datetime=end_time,
                constellation=constellation,
                satellite=constellation,
                sensor_type=SensorType.OPTIC.value,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.superview.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.optic.value,
            ),
            assets={asset.name: asset for asset in assets}
        )
        return item

    def add_major_metadata(self, url: str, item: Item, metadata: ET.Element) -> Item:

        item.properties.processing__level = find_or_none(metadata, "ProductLevel")
        item.properties.gsd = find_or_none(metadata, "GSDX", float)
        
        proj = AccessManager.get_gdal_proj(self.mux_tif_path)
        if proj:
            item.properties.proj__epsg = get_epsg(proj)
        else:
            item.properties.proj__epsg = get_epsg_from_gdal_info_gcps(self.mux_tif_path)

        item.properties.secondary_id = find_or_none(metadata, "ProductID")
        return item

    def add_minor_metadata(self, url: str, item: Item, metadata: ET.Element) -> Item:
        
        item.properties.instrument = find_or_none(metadata, "SensorID")
        item.properties.sensor = item.properties.instrument

        item.properties.view__azimuth = find_or_none(metadata, "SatelliteAzimuth", float)
        item.properties.view__sun_azimuth = find_or_none(metadata, "SolarAzimuth", float)
        
        sun_zenith = find_or_none(metadata, "SolarZenith", float)
        if sun_zenith is not None:
            item.properties.view__sun_elevation = 90.0 - sun_zenith

        item.properties.view__off_nadir = find_or_none(metadata, "ViewAngle", float)
        item.properties.eo__cloud_cover = find_or_none(metadata, "CloudPercent", float)
        item.properties.eo__snow_cover = find_or_none(metadata, "SnowPercent", float)

        item.properties.acq__acquisition_orbit = find_or_none(metadata, "OrbitID")
        od = find_or_none(metadata, "OrbitDirection")
        item.properties.acq__acquisition_orbit_direction = "DESCENDING" if od == "D" else "ASCENDING" if od == "A" else None

        return item

    def __check_path__(self, path: str):
        self.__init__()
        if AccessManager.is_dir(path):
            files = AccessManager.listdir(path)
            for file in files:
                if not file.is_dir:
                    fname = file.name.lower()
                    if fname.endswith('_thumb.jpg'):
                        self.quicklook_path = file.path

                    elif fname.endswith('-mux.tiff'):
                        self.mux_tif_path = file.path
                        self.xml_path = self.mux_tif_path[:-9] + ".xml"
                    elif fname.endswith(('-mux.jpg', '-mux.jpeg')):
                        self.mux_jpg_path = file.path
                    elif fname.endswith('-mux.xml'):
                        self.mux_xml_path = file.path
                    elif fname.endswith('-mux.rpb'):
                        self.mux_rcps_path = file.path

                    elif fname.endswith(('-pan.tiff', '-pan.tif')):
                        self.pan_tif_path = file.path
                    elif fname.endswith(('-pan.jpg', '-pan.jpeg')):
                        self.pan_jpg_path = file.path
                    elif fname.endswith('-pan.xml'):
                        self.pan_xml_path = file.path
                    elif fname.endswith('-pan.rpb'):
                        self.pan_rcps_path = file.path

                    elif fname.endswith('-cloud.shp'):
                        self.cloud_shape_path = file.path

            if self.xml_path:
                shape_path_if_exists = self.xml_path.removesuffix('.xml') + ".shp"
                if AccessManager.exists(shape_path_if_exists):
                    self.shape_path = shape_path_if_exists

            if self.mux_tif_path is not None and self.xml_path is not None and AccessManager.exists(self.xml_path):
                return True
        return False
