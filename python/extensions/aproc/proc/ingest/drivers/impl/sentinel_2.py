import re
import xml.etree.ElementTree as ET
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Band, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    find_or_none, raster_to_jpg, get_epsg, get_geom_bbox_centroid_from_coordinates)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver

RED_EDGE = "Vegetation red edge"
BANDS_NAME = {
    "B01": "Coastal aerosol",
    "B02": "Blue",
    "B03": "Green",
    "B04": "Red",
    "B05": RED_EDGE,
    "B06": RED_EDGE,
    "B07": RED_EDGE,
    "B08": "NIR",
    "B8A": "Narrow NIR",
    "B09": "Water vapour",
    "B10": "Cirrus",
    "B11": "SWIR",
    "B12": "SWIR"
}


class Driver(IngestDriver):

    configuration: dict = {}

    def __init__(self):
        super().__init__()
        self.md_path = None
        self.quicklook_path = None
        self.band_paths: list[str] = []
        self.tci_path = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)
        Driver.configuration = configuration or {}

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets: list[Asset] = []
        ImageDriverHelper.add_archive(assets, url)

        # It is put as a thumbnail as the resolution is low
        ImageDriverHelper.add_asset(assets, self.quicklook_path, Role.thumbnail,
                                    MimeType.JPG, AssetFormat.jpg, ResourceType.other, airs__managed=True)
        ImageDriverHelper.add_asset(assets, self.md_path, Role.metadata,
                                    MimeType.XML, AssetFormat.xml, ResourceType.other)
        ImageDriverHelper.add_asset(assets, self.tci_path, Role.data,
                                    MimeType.JPEG2000, AssetFormat.jpg2000, ResourceType.gridded)

        for band in self.band_paths:
            matches = re.findall(r"_(B.{2})\.jp2$", band)
            if len(matches) > 0:
                name = matches[0]

                assets.append(Asset(href=band, size=AccessManager.get_size(band), roles=[Role.data.value],
                                    name=name, type=MimeType.JPEG2000.value, description=name,
                                    airs__managed=False, asset_format=AssetFormat.jpg2000.value,
                                    asset_type=ResourceType.gridded.value,
                                    eo__bands=[Band(name=name, eo__common_name=BANDS_NAME[name])]))
        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if IngestDriver.must_build_preview(Driver.configuration, self.tci_path, local_remote_both="local"):
            Driver.LOGGER.debug(f"Building overview for local TCI {self.tci_path}")
            overview = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
            raster_to_jpg(self.tci_path, Driver.OVERVIEW_FROM_LARGE_TIFF_PCT, Driver.OVERVIEW_FROM_LARGE_TIFF_PCT, overview.href, [1, 2, 3], stretch=Driver.configuration.get('overview_stretch', False))
            overview.size = AccessManager.get_size(overview.href)
            assets.append(overview)
        elif IngestDriver.must_build_preview(Driver.configuration, self.tci_path, local_remote_both="remote"):
            Driver.LOGGER.debug(f"Building overview for remote TCI {self.tci_path}")
            overview_folder = self.assets_dir + '/sentinel2/' + self.get_item_id(url) + '/overview'
            AccessManager.makedir(overview_folder)
            overview_path = overview_folder + '/overview.jpg'
            # File is processed locally as it significantly speeds up processing time
            with AccessManager.make_local(self.tci_path) as local_tci_path:
                overview = ImageDriverHelper.prepare_preview_asset(self, overview_path, Role.overview, MimeType.JPG, AssetFormat.jpg)
                raster_to_jpg(local_tci_path, Driver.OVERVIEW_FROM_LARGE_TIFF_PCT, Driver.OVERVIEW_FROM_LARGE_TIFF_PCT, overview.href, [1, 2, 3], stretch=Driver.configuration.get('overview_stretch', False))
                overview.size = AccessManager.get_size(overview.href)
                assets.append(overview)
        else:
            Driver.LOGGER.debug("Skipping overview generation for TCI {}".format(self.tci_path))
        return assets

    def load_metadata(self, url: str) -> object:
        with AccessManager.make_local(self.md_path) as local_md_path:
            tree = ET.parse(local_md_path)
            root = tree.getroot()

        return root

    def build_core_item(self, url: str, assets: list[Asset], root: ET.Element) -> Item:
        for coords in root.iter('EXT_POS_LIST'):
            coords_raw = coords.text.strip().split()
            coords_float = list(map(float, coords_raw))
            # WARNING IN EXT_POS_LIST order is lat lon , in geojson we need lon lat
            points = [[coords_float[i+1], coords_float[i]] for i in range(0, len(coords_float), 2)]
            geometry, bbox, centroid = get_geom_bbox_centroid_from_coordinates(points)

        for p_info in root.iter('Product_Info'):
            start_time = find_or_none(p_info, 'PRODUCT_START_TIME')
            start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            stop_time = find_or_none(p_info, 'PRODUCT_STOP_TIME')
            stop_time = datetime.strptime(stop_time, "%Y-%m-%dT%H:%M:%S.%fZ")

            secondary_id = find_or_none(p_info, "PRODUCT_URI")

        item = Item(
            id=self.get_item_id(url),
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=start_time,
                start_datetime=start_time,
                end_datetime=stop_time,
                constellation="Sentinel 2",
                sensor_type=SensorType.OPTIC.value,
                secondary_id=secondary_id,
                item_format=ItemFormat.safe,
                item_type=ResourceType.gridded.value,
                main_asset_format=AssetFormat.jpg2000,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.optic.value
            ),
            assets={asset.name: asset for asset in assets}
        )

        return item

    def add_major_metadata(self, url: str, item: Item, root: ET.Element) -> Item:
        for p_info in root.iter('Product_Info'):
            item.properties.processing__level = find_or_none(p_info, 'PROCESSING_LEVEL')
            item.properties.satellite = find_or_none(p_info, 'Datatake/SPACECRAFT_NAME')
            item.properties.secondary_id = find_or_none(p_info, "PRODUCT_URI")
        item.properties.proj__epsg = get_epsg(AccessManager.get_gdal_proj(self.tci_path))

        resolutions: list[float] = []
        item.properties.eo__bands: list[Band] = []
        for bands in root.iter("Spectral_Information_List"):
            for band in bands.iter('Spectral_Information'):
                band_id = band.get('bandId', None)
                resolutions.append(find_or_none(band, 'RESOLUTION'))
                item.properties.eo__bands.append(Band(
                    asset=band.get('physicalBand', None),
                    name=band.get('physicalBand', None),
                    eo__common_name=BANDS_NAME.get(band_id, ''),
                    eo__center_wavelength=find_or_none(band, 'Wavelength/CENTRAL')
                ))

        if len(resolutions) > 0:
            item.properties.gsd = min(resolutions)

        return item

    def add_minor_metadata(self, url: str, item: Item, root: ET.Element) -> Item:
        item.properties.instrument = item.properties.satellite
        item.properties.sensor = item.properties.satellite

        for p_info in root.iter('Product_Info'):
            item.properties.acq__acquisition_orbit_direction = find_or_none(p_info, 'Datatake/SENSING_ORBIT_DIRECTION')
            item.properties.acq__acquisition_orbit = find_or_none(p_info, "Datatake/SENSING_ORBIT_NUMBER")

        for p_info in root.iter('Cloud_Coverage_Assessment'):
            item.properties.eo__cloud_cover = p_info.text
        for p_info in root.iter('Snow_Coverage_Assessment'):
            item.properties.eo__snow_cover = p_info.text

        return item

    def __check_path__(self, path: str):
        self.__init__()
        if AccessManager.is_dir(path):
            for file in AccessManager.listdir(path):
                if not file.is_dir:
                    if file.name.endswith('-ql.jpg'):
                        self.quicklook_path = file.path
                    if file.name.startswith('MTD_') and file.name.endswith('.xml'):
                        self.md_path = file.path
                else:
                    # Not too convinced by this, when things are in the MTD file
                    if file.name == 'GRANULE':
                        for granule in AccessManager.listdir(file.path):
                            if granule.is_dir:
                                for data in AccessManager.listdir(granule.path):
                                    if data.is_dir and data.name == 'IMG_DATA':
                                        for band in AccessManager.listdir(data.path):
                                            if band.name.endswith('_TCI.jp2'):
                                                self.tci_path = band.path
                                            elif band.name.endswith('.jp2'):
                                                self.band_paths.append(band.path)
            return self.quicklook_path is not None and self.md_path is not None and self.tci_path is not None and len(self.band_paths) > 0
        return False
