import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo
import os

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
        self.data_path = None
        self.main_asset_role = None
        self.overview_path = None
        self.thumbnail_path = None
        self.cloud_shape_path = None

        self.mux_rcps_path = None
        self.mux_xml_path = None
        self.mux_tif_path = None
        self.mux_overview_path = None
        self.mux_thumbnail_path = None

        self.pan_rcps_path = None
        self.pan_xml_path = None
        self.pan_tif_path = None
        self.pan_overview_path = None
        self.pan_thumbnail_path = None

        self.psh_rcps_path = None
        self.psh_xml_path = None
        self.psh_tif_path = None
        self.psh_overview_path = None
        self.psh_thumbnail_path = None

    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)
        Driver.configuration = configuration

    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        ImageDriverHelper.add_archive(assets, url)

        # Main image
        assets.append(Asset(href=self.data_path, size=AccessManager.get_size(self.data_path),
                            roles=[Role.data.value, Role.visual.value, self.main_asset_role], name=Role.data.value, type=MimeType.GEOTIFF.value,
                            description=Role.data.value, airs__managed=False, asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value))

        if self.mux_tif_path:
            assets.append(Asset(href=self.mux_tif_path, size=AccessManager.get_size(self.mux_tif_path),
                                roles=[Role.data.value, Role.visual.value, Role.multispectral.value], name=Role.multispectral.value, type=MimeType.GEOTIFF.value,
                                description=Role.multispectral.value, airs__managed=False, asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value))

        if self.psh_tif_path:
            assets.append(Asset(href=self.psh_tif_path, size=AccessManager.get_size(self.psh_tif_path),
                                roles=[Role.data.value, Role.visual.value, Role.pan_sharpened.value], name=Role.pan_sharpened.value, type=MimeType.GEOTIFF.value,
                                description=Role.pan_sharpened.value, airs__managed=False, asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value))

        if self.pan_tif_path:
            assets.append(Asset(href=self.pan_tif_path, size=AccessManager.get_size(self.pan_tif_path),
                                roles=[Role.data.value, Role.visual.value, Role.pan.value], name=Role.pan.value, type=MimeType.GEOTIFF.value,
                                description=Role.pan.value, airs__managed=False, asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value))

        # Overviews
        if self.mux_overview_path:
            assets.append(Asset(href=self.mux_overview_path, size=AccessManager.get_size(self.mux_overview_path),
                                roles=[Role.overview.value, Role.visual.value, Role.multispectral.value], name=Role.overview.value + "-mux", type=MimeType.JPEG.value,
                                description=Role.overview.value + "for multispectral", airs__managed=False, asset_format=AssetFormat.jpg.value, asset_type=ResourceType.gridded.value))

        if self.pan_overview_path:
            assets.append(Asset(href=self.pan_overview_path, size=AccessManager.get_size(self.pan_overview_path),
                                roles=[Role.overview.value, Role.visual.value, Role.pan_sharpened.value], name=Role.overview.value + "-pan", type=MimeType.JPEG.value,
                                description=Role.overview.value + "for pan", airs__managed=False, asset_format=AssetFormat.jpg.value, asset_type=ResourceType.gridded.value))

        if self.psh_overview_path:
            assets.append(Asset(href=self.psh_overview_path, size=AccessManager.get_size(self.psh_overview_path),
                                roles=[Role.overview.value, Role.visual.value, Role.visual.value, Role.pan_sharpened.value], name=Role.overview.value + "-psh", type=MimeType.JPEG.value,
                                description=Role.overview.value + "for pan sharpened", airs__managed=False, asset_format=AssetFormat.jpg.value, asset_type=ResourceType.gridded.value))
        # Metadata
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

        if self.psh_xml_path:
            assets.append(Asset(href=self.psh_xml_path, size=AccessManager.get_size(self.psh_xml_path),
                                roles=[Role.metadata.value], name=Role.metadata.value + "-psh", type=MimeType.XML.value,
                                description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.xml.value, asset_type=ResourceType.other.value))

        # RPCs
        if self.mux_rcps_path:
            assets.append(Asset(href=self.mux_rcps_path, size=AccessManager.get_size(self.mux_rcps_path),
                                roles=[Role.rpc.value], name=Role.rpc.value + "-mux", type=MimeType.TEXT.value,
                                description=Role.rpc.value, airs__managed=False, asset_format=AssetFormat.rpb.value, asset_type=ResourceType.other.value))

        if self.pan_rcps_path:
            assets.append(Asset(href=self.pan_rcps_path, size=AccessManager.get_size(self.pan_rcps_path),
                                roles=[Role.rpc.value], name=Role.rpc.value + "-pan", type=MimeType.TEXT.value,
                                description=Role.rpc.value, airs__managed=False, asset_format=AssetFormat.rpb.value, asset_type=ResourceType.other.value))

        if self.psh_rcps_path:
            assets.append(Asset(href=self.psh_rcps_path, size=AccessManager.get_size(self.psh_rcps_path),
                                roles=[Role.rpc.value], name=Role.rpc.value + "-psh", type=MimeType.TEXT.value,
                                description=Role.rpc.value, airs__managed=False, asset_format=AssetFormat.rpb.value, asset_type=ResourceType.other.value))

        # SHAPE Clouds
        if self.cloud_shape_path:
            assets.append(Asset(href=self.cloud_shape_path, size=AccessManager.get_size(self.cloud_shape_path),
                                roles=[Role.cloud.value, Role.mask.value], name=Role.cloud.value, type=MimeType.SHP.value,
                                description=Role.cloud.value, airs__managed=False, asset_format=AssetFormat.shape.value, asset_type=ResourceType.vector.value))

        return assets

    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if self.overview_path is not None:
            overview = ImageDriverHelper.make_local_preview_asset(self, url, self.overview_path, MimeType.JPG, AssetFormat.jpg)
            self.overview_path = overview.href
            assets.append(overview)
            Driver.LOGGER.debug(f"Using existing quicklook at {self.overview_path}")
        if self.thumbnail_path is not None:
            thumbnail = ImageDriverHelper.make_local_preview_asset(self, url, self.thumbnail_path, MimeType.JPG, AssetFormat.jpg, role=Role.thumbnail)
            self.overview_path = thumbnail.href
            assets.append(thumbnail)
            Driver.LOGGER.debug(f"Using existing thumbnail at {self.thumbnail_path}")
        return assets

    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if self.overview_path is None:
            if self.overview_path and AccessManager.is_local(self.overview_path) and Driver.configuration.get('build_overview_when_local', True):
                Driver.LOGGER.debug(f"Use {self.overview_path} for quicklook")
                overview = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
                geotiff_to_jpg(self.overview_path, Driver.OVERVIEW_FROM_TIFF_PCT, Driver.OVERVIEW_FROM_TIFF_PCT, overview.href, stretch=Driver.configuration.get('overview_stretch', False))
                overview.size = AccessManager.get_size(overview.href)
                self.overview_path = overview.href
                assets.append(overview)
            elif Driver.configuration and Driver.configuration.get('build_overview_when_remote', False):
                Driver.LOGGER.debug(f"Building overview for remote {self.overview_path}")
                overview_folder = self.assets_dir + '/superview/' + self.get_item_id(url) + '/overview'
                AccessManager.makedir(overview_folder)
                overview_path = overview_folder + '/overview.jpg'
                # File is processed locally as it significantly speeds up processing time
                with AccessManager.make_local(overview_path) as local_big_preview_path:
                    overview = ImageDriverHelper.prepare_preview_asset(self, overview_path, Role.overview, MimeType.JPG, AssetFormat.jpg)
                    geotiff_to_jpg(local_big_preview_path, Driver.OVERVIEW_FROM_LARGE_TIFF_PCT, Driver.OVERVIEW_FROM_LARGE_TIFF_PCT, overview.href, [1, 1, 1], Driver.configuration.get('overview_stretch', True))
                    overview.size = AccessManager.get_size(overview.href)
                    self.overview_path = overview.href
                    assets.append(overview)
            else:
                Driver.LOGGER.debug("Skipping overview generation for TCI {}".format(self.overview_path))

        if self.thumbnail_path is None and self.overview_path is not None:
            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.JPG, AssetFormat.jpg)
            downsample_image(self.overview_path, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR)
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)
        return assets

    def load_metadata(self, url: str) -> object:
        with AccessManager.make_local(self.xml_path) as local_md_path:
            tree = ET.parse(local_md_path)
            root = tree.getroot()

        return root

    def build_core_item(self, url: str, assets: list[Asset], metadata: ET.Element) -> Item:

        geometry = ImageDriverHelper.gdal_geometry(self, self.data_path)
        Driver.LOGGER.debug(f"Extracted geometry for item {url}: {geometry}")
        if geometry is None:
            Driver.LOGGER.error(f"No geometry found for item {url}")
            raise DriverException(f"Missing required 'geometry' for {url}")

        bbox = get_bbox(geometry["coordinates"][0])

        centroid = metadata.get("properties", {}).get("proj:centroid")
        if centroid is None and geometry is not None:
            centroid = get_centroid(geometry)

        start_time_str = find_or_none(metadata, "StartTime", alt_keys=["ProductInfo/StartTime"])
        end_time_str = find_or_none(metadata, "EndTime", alt_keys=["ProductInfo/EndTime"])
        end_time = None
        if start_time_str:
            start_time = int(datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
                             .replace(tzinfo=ZoneInfo("Asia/Shanghai"))  # Beijing Time to UTC
                             .astimezone(ZoneInfo("UTC"))
                             .timestamp())
            date_time = start_time
        else:
            Driver.LOGGER.error(f"No date time found for item {url}")
            raise DriverException(f"Missing required 'StartTime' for {url}")
        if end_time_str:
            end_time = int(datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
                           .replace(tzinfo=ZoneInfo("Asia/Shanghai"))  # Beijing Time to UTC
                           .astimezone(ZoneInfo("UTC"))
                           .timestamp())

        observation_type = ObservationType.optic.value
        # Use XML file name to determine satellite and constellation
        satellite: str = os.path.basename(self.xml_path).split('_')[0]
        if satellite.lower() == "sv-2":
            constellation = "Gaofen Duomo"
        elif satellite.lower().startswith('svn'):
            constellation = "Superview Neo"
            if satellite.lower().startswith('svn2'):
                observation_type = ObservationType.radar.value
        else:
            constellation = "Superview"

        item = Item(
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                start_datetime=start_time,
                end_datetime=end_time,
                constellation=constellation,
                satellite=satellite,
                sensor_type=SensorType.OPTIC.value,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.superview.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                observation_type=observation_type
            ),
            assets={asset.name: asset for asset in assets}
        )
        return item

    def add_major_metadata(self, url: str, item: Item, metadata: ET.Element) -> Item:

        item.properties.processing__level = find_or_none(metadata, "ProductLevel", alt_keys=["ProductInfo/ProductLevel"])
        item.properties.gsd = find_or_none(metadata, "GSDX", float, alt_keys=["ProductInfo/GSDX"])

        item.properties.secondary_id = find_or_none(metadata, "ProductID", alt_keys=["ProductInfo/ProductID"])

        proj = AccessManager.get_gdal_proj(self.data_path)
        if proj:
            item.properties.proj__epsg = get_epsg(proj)
        else:
            item.properties.proj__epsg = get_epsg_from_gdal_info_gcps(self.data_path)

        return item

    def add_minor_metadata(self, url: str, item: Item, metadata: ET.Element) -> Item:

        item.properties.instrument = find_or_none(metadata, "SensorID", alt_keys=["ProductInfo/SensorID"])
        item.properties.sensor = item.properties.instrument

        item.properties.view__azimuth = find_or_none(metadata, "SatelliteAzimuth", float, alt_keys=["SatelliteElevation", "ProductInfo/SatelliteAzimuth", "ProductInfo/SatelliteElevation"])
        item.properties.view__sun_azimuth = find_or_none(metadata, "SolarAzimuth", float, alt_keys=["ProductInfo/SolarAzimuth"])

        sun_zenith = find_or_none(metadata, "SolarZenith", float, alt_keys=["SolarElevation", "ProductInfo/SolarZenith", "ProductInfo/SolarElevation"])
        if sun_zenith is not None:
            item.properties.view__sun_elevation = 90.0 - sun_zenith

        item.properties.view__off_nadir = find_or_none(metadata, "ViewAngle", float, alt_keys=["ProductInfo/ViewAngle"])
        item.properties.view__off_nadir = find_or_none(metadata, "ViewAngle", float, alt_keys=["Viewangle", "ProductInfo/ViewAngle", "ProductInfo/Viewangle"])
        item.properties.eo__cloud_cover = find_or_none(metadata, "CloudPercent", float, alt_keys=["ProductInfo/CloudPercent"])
        item.properties.eo__snow_cover = find_or_none(metadata, "SnowPercent", float, alt_keys=["ProductInfo/SnowPercent"])

        item.properties.acq__acquisition_orbit = find_or_none(metadata, "OrbitID", alt_keys=["ProductInfo/OrbitID"])
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
                    if fname.endswith('-mux.tiff'):
                        self.mux_tif_path = file.path
                    elif fname.endswith(('-mux.jpg', '-mux.jpeg')):
                        self.mux_overview_path = file.path
                    elif fname.endswith('-mux.xml'):
                        self.mux_xml_path = file.path
                    elif fname.endswith('-mux.rpb'):
                        self.mux_rcps_path = file.path
                    elif fname.endswith(('-mux_thumb.jpg', '-mux_thumb.jpeg')):
                        self.mux_thumbnail_path = file.path

                    elif fname.endswith(('-pan.tiff', '-pan.tif')):
                        self.pan_tif_path = file.path
                    elif fname.endswith(('-pan.jpg', '-pan.jpeg')):
                        self.pan_overview_path = file.path
                    elif fname.endswith('-pan.xml'):
                        self.pan_xml_path = file.path
                    elif fname.endswith('-pan.rpb'):
                        self.pan_rcps_path = file.path
                    elif fname.endswith(('-pan_thumb.jpg', '-pan_thumb.jpeg')):
                        self.pan_thumbnail_path = file.path

                    elif fname.endswith(('-psh.tiff', '-psh.tif')):
                        self.psh_tif_path = file.path
                    elif fname.endswith(('-psh.jpg', '-psh.jpeg')):
                        self.psh_overview_path = file.path
                    elif fname.endswith('-psh.xml'):
                        self.psh_xml_path = file.path
                    elif fname.endswith('-psh.rpb'):
                        self.psh_rcps_path = file.path
                    elif fname.endswith(('-psh_thumb.jpg', '-psh_thumb.jpeg')):
                        self.psh_thumbnail_path = file.path

                    elif fname.endswith('-cloud.shp'):
                        self.cloud_shape_path = file.path

            # the metadata reference is in order of priority: mux, psh, pan
            if self.pan_xml_path and self.pan_tif_path:
                self.xml_path = self.pan_xml_path
                self.data_path = self.pan_tif_path
                self.main_asset_role = Role.pan.value
                self.overview_path = self.pan_overview_path
                self.thumbnail_path = self.pan_thumbnail_path

            if self.psh_xml_path and self.psh_tif_path:
                self.xml_path = self.psh_xml_path
                self.data_path = self.psh_tif_path
                self.main_asset_role = Role.pan_sharpened.value
                self.overview_path = self.psh_overview_path
                self.thumbnail_path = self.psh_thumbnail_path

            if self.mux_xml_path and self.mux_tif_path:
                self.xml_path = self.mux_xml_path
                self.data_path = self.mux_tif_path
                self.main_asset_role = Role.multispectral.value
                self.overview_path = self.mux_overview_path
                self.thumbnail_path = self.mux_thumbnail_path

            if self.xml_path is not None and self.data_path is not None:
                return True
        return False
