import re
import xml.etree.ElementTree as ET

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from dateutil import parser
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    downsample_image, find_or_none, get_bbox, get_centroid, get_epsg,
    get_epsg_from_gdal_info_gcps)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver
from extensions.aproc.proc.utils.polarized import (DriverWithPolarizedAssets,
                                                   PolarizedAsset)


class Driver(IngestDriver, DriverWithPolarizedAssets):

    configuration: dict = {}

    def __init__(self):
        super().__init__()
        self.measurements: list[PolarizedAsset] = []
        self.quicklook_path = None
        self.main_asset_description = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)
        Driver.configuration = configuration or {}

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        ImageDriverHelper.add_archive(assets, url)

        for pol in self.measurements:
            assets.append(Asset(href=pol.path, size=AccessManager.get_size(pol.path), proj__epsg=get_epsg_from_gdal_info_gcps(pol.path),
                                roles=[Role.data.value], name=pol.name, type=MimeType.GEOTIFF.value, sar__polarizations=[pol.polarization],
                                description=pol.description, airs__managed=False, asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value))
            assets.append(Asset(href=pol.metadata, size=AccessManager.get_size(pol.metadata),
                                roles=[Role.metadata.value], name=pol.polarization + '_metadata', type=MimeType.XML.value,
                                description=pol.description + ' metadata', airs__managed=False, asset_format=AssetFormat.xml.value, asset_type=ResourceType.other.value))

        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        quicklook = ImageDriverHelper.make_local_preview_asset(self, url, self.quicklook_path, MimeType.PNG, AssetFormat.png)
        self.quicklook_path = quicklook.href
        assets.append(quicklook)

        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.PNG, AssetFormat.png)
        downsample_image(self.quicklook_path, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR)
        thumbnail.size = AccessManager.get_size(thumbnail.href)
        assets.append(thumbnail)

        return assets

    def load_metadata(self, url: str) -> ET.Element:
        with AccessManager.make_local(self.main_asset_description.metadata) as local_metadata_path:
            tree = ET.parse(local_metadata_path)
            root = tree.getroot()

        return root

    def build_core_item(self, url: str, assets: list[Asset], root: ET.Element) -> Item:
        geometry = ImageDriverHelper.gdal_geometry(self, self.main_asset_description.path, url)

        centroid = get_centroid(geometry)
        bbox = get_bbox(geometry["coordinates"][0])

        start_time = root.find("./Channel/SwathInfo/AcquisitionStartTime").text
        start_time = parser.parse(start_time)

        item = Item(
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=start_time,
                constellation="SOACOM",
                sensor_type=SensorType.SAR.value,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.soacom.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=self.main_asset_description.name,
                observation_type=ObservationType.radar.value
            ),
            assets={asset.name: asset for asset in assets}
        )

        return item

    def add_major_metadata(self, url: str, item: Item, root: ET.Element) -> Item:
        item.properties.satellite = find_or_none(root, "./Channel/DataSetInfo/SensorName")

        line_step = find_or_none(root, "./Channel/RasterInfo/LinesStep")
        sample_step = find_or_none(root, "./Channel/RasterInfo/SamplesStep")
        if line_step is not None and sample_step is not None:
            item.properties.gsd = (abs(float(line_step)) + abs(float(sample_step))) / 2

        description = find_or_none(root, "./Channel/DataSetInfo/Description")
        if description is not None:
            description_parts = description.split(" ")
            if len(description_parts) > 2:
                item.properties.processing__level = "L" + description_parts[1]

        item.properties.proj__epsg = get_epsg(AccessManager.get_gdal_proj(self.main_asset_description.path))

        return item

    def add_minor_metadata(self, url: str, item: Item, root: ET.Element) -> Item:
        item.properties.instrument = item.properties.satellite
        item.properties.sensor = item.properties.satellite
        item.properties.acq__acquisition_mode = find_or_none(root, "./Channel/DataSetInfo/AcquisitionMode")

        orbit_number = find_or_none(root, "./Channel/StateVectorData/OrbitNumber")
        if orbit_number is not None and orbit_number != "NOT_AVAILABLE":
            item.properties.acq__acquisition_orbit = int(orbit_number)

        orbit_direction = find_or_none(root, "./Channel/StateVectorData/OrbitDirection")
        if orbit_direction is not None and orbit_direction != "NOT_AVAILABLE":
            item.properties.acq__acquisition_orbit_direction = int(orbit_direction)

        item.properties.processing__facility = find_or_none(root, "./Channel/DataSetInfo/ProcessingCenter")

        return item

    def __check_path__(self, path: str):
        self.__init__()

        if not AccessManager.is_dir(path):
            return False

        data_file_regex = re.compile(r"([hv][hv])-h$")

        for file in AccessManager.listdir(path):
            if not file.is_dir:
                continue

            # Data folder
            if file.name == 'Data':
                for data_file in AccessManager.listdir(file.path):
                    data_file_match = data_file_regex.findall(data_file.name)
                    # If the file respects the pattern and has a metadata file
                    if len(data_file_match) > 0 and AccessManager.exists(data_file.path + '.xml'):
                        polarization = data_file_match[0]
                        Driver.LOGGER.warn(polarization)
                        self.add_measurement(self.measurements, polarization, data_file.path, metadata=data_file.path + ".xml")

            # Images folder
            elif file.name == 'Images':
                for image_file in AccessManager.listdir(file.path):
                    if image_file.name.endswith('.png'):
                        self.quicklook_path = image_file.path

        self.main_asset_description = self.pick_data_asset(self.measurements)
        return len(self.measurements) > 0 \
            and self.quicklook_path is not None
