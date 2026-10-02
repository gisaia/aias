import re
import xml.etree.ElementTree as ET
from datetime import datetime

from aias_common.access.file import File
from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Band, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    find_or_none, get_epsg, get_geom_bbox_centroid_from_coordinates,
    raster_to_jpg)
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

DATA_ASSET_REGEX = r"_(.{3}(_\d{2}m)?)\.jp2$"


class Driver(IngestDriver):

    def __init__(self):
        super().__init__()
        self.md_path = None
        self.quicklook_path = None
        # Store bands per key (B01, B02, AOT, TCI, ...)
        self.band_paths: dict[str, list[str]] = {}
        self.tci_path = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        ImageDriverHelper.init(Driver, configuration)

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets: list[Asset] = []
        ImageDriverHelper.add_archive(assets, url)

        # It is put as a thumbnail as the resolution is low
        ImageDriverHelper.add_asset(assets, self.quicklook_path, Role.thumbnail,
                                    MimeType.JPG, AssetFormat.jpg, ResourceType.other, airs__managed=True)
        ImageDriverHelper.add_asset(assets, self.md_path, Role.metadata,
                                    MimeType.XML, AssetFormat.xml, ResourceType.other)
        tci_asset = ImageDriverHelper.add_asset(assets, self.tci_path, Role.data,
                                                MimeType.JPEG2000, AssetFormat.jpg2000, ResourceType.gridded)
        tci_asset.roles.append(Role.visual.data)

        for asset_type, bands in self.band_paths.items():
            is_data_band = re.match(r"B.{2}", asset_type) is not None

            # Lowest resolution is first in alphabetical order
            sorted_bands = sorted(bands)
            for idx, band in enumerate(sorted_bands):

                # Single out the lowest resolution band as the reference for the band
                if idx == 0 and is_data_band:
                    name = asset_type
                else:
                    asset_type_with_resolution = re.findall(DATA_ASSET_REGEX, band)
                    name = asset_type_with_resolution[0][0]

                asset = Asset(href=band, size=AccessManager.get_size(band),
                              name=name, type=MimeType.JPEG2000.value, description=name,
                              airs__managed=False, asset_format=AssetFormat.jpg2000.value,
                              asset_type=ResourceType.gridded.value)

                if is_data_band:
                    asset.roles = [Role.data.value]
                    eo_band = Band(name=asset_type, eo__common_name=BANDS_NAME[asset_type])
                    # Try to get resolution
                    resolution_matches = re.findall(r"_(\d{2})m.jp2$", band)
                    if len(resolution_matches) > 0:
                        eo_band.eo__gsd = int(resolution_matches[0])

                    asset.eo__bands = [eo_band]
                elif asset_type == "TCI":
                    asset.roles = [Role.data.value, Role.visual.value]
                elif asset_type == "AOT":
                    asset.roles = [Role.aerosol_optical_thickness.value]
                elif asset_type == "CLD":
                    asset.roles = [Role.cloud.value]
                elif asset_type == "SCL":
                    asset.roles = [Role.scene_classification.value]
                elif asset_type == "SNW":
                    asset.roles = [Role.snow_ice.value]
                elif asset_type == "WVP":
                    asset.roles = [Role.water_vapour.value]
                else:
                    raise DriverException(f"Unrecognised asset type found in Sentinel2 archive {asset_type}")
                assets.append(asset)

        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if IngestDriver.must_build_preview(Driver.configuration, self.tci_path, local_remote_both="local"):
            Driver.LOGGER.debug(f"Building overview for local TCI {self.tci_path}")
            overview = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
            raster_to_jpg(self.tci_path, Driver.OVERVIEW_SIZE, Driver.OVERVIEW_SIZE, overview.href, [1, 2, 3], stretch=Driver.configuration.get('overview_stretch', False))
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
                raster_to_jpg(local_tci_path, Driver.OVERVIEW_SIZE, Driver.OVERVIEW_SIZE, overview.href, [1, 2, 3], stretch=Driver.configuration.get('overview_stretch', False))
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
                physical_band = band.get('physicalBand', None)
                # If there is only 2 characters, then there is a 0 missing between B and the only digit
                if physical_band is not None and len(physical_band) == 2:
                    physical_band = physical_band[0] + "0" + physical_band[1]
                resolutions.append(find_or_none(band, 'RESOLUTION'))
                item.properties.eo__bands.append(Band(
                    asset=physical_band,
                    name=physical_band,
                    eo__common_name=BANDS_NAME.get(physical_band, None),
                    # In the metadata, it is in nm but should be in µm
                    eo__center_wavelength=find_or_none(band, 'Wavelength/CENTRAL', process=lambda x: x / 1000)
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
                    if file.name == 'GRANULE':
                        for granule in AccessManager.listdir(file.path):
                            if granule.is_dir:
                                for data in AccessManager.listdir(granule.path):
                                    if data.is_dir and data.name == 'IMG_DATA':
                                        self.__find_bands(data)

                                        # All bands have been detected, find the finest resolution TCI
                                        tci_paths = self.band_paths.get("TCI", [])
                                        if len(tci_paths) > 0:
                                            sorted_tci_paths = sorted(tci_paths)
                                            self.tci_path = sorted_tci_paths[0]
                                            # Remove from the list of bands to not declare it twice
                                            tci_paths.remove(self.tci_path)

            return self.quicklook_path is not None \
                and self.md_path is not None \
                and self.tci_path is not None \
                and len(self.band_paths) > 0
        return False

    def __find_bands(self, folder: File) -> None:
        """
        Browses the IMG_DATA folder and subfolders to find all the bands
        """
        for band in AccessManager.listdir(folder.path):
            # Limit the allowed folders to limit recursivity
            if band.is_dir:
                if band.name in ["R10m", "R20m", "R60m"]:
                    self.__find_bands(band)
            # Keep all the jp2 files (bands but also AOT, TCI, ...)
            elif band.name.endswith('.jp2'):
                matches = re.findall(DATA_ASSET_REGEX, band.name)
                if len(matches) > 0:
                    if isinstance(matches[0], tuple):
                        asset_type = matches[0][0].split("_")[0]
                    else:
                        asset_type = matches[0]
                    asset_files = self.band_paths.get(asset_type, [])
                    asset_files.append(band.path)
                    self.band_paths[asset_type] = asset_files
