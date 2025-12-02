import re
import xml.etree.ElementTree as ET
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Band, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    geotiff_to_jpg, get_epsg, get_geom_bbox_centroid, setup_gdal)
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
        Driver.output_folder = configuration['tmp_directory']  # todo: this should use self.get_asset_filepath instead

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets: list[Asset] = []
        assets.append(
            Asset(
                href=url,
                roles=[Role.archive.value],
                name=Role.archive.value,
                type=MimeType.DIRECTORY.value,
                description=Role.archive.value,
                airs__managed=False,
                asset_format=AssetFormat.directory.value
            )
        )

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
        overview_folder = self.output_folder + '/sentinel2/' + self.get_item_id(url) + '/overview'
        AccessManager.makedir(overview_folder)
        overview_path = overview_folder + '/overview.jpg'
        # File is processed locally as it significantly speeds up processing time
        with AccessManager.make_local(self.tci_path) as local_tci_path:
            geotiff_to_jpg(local_tci_path, 10, 10, overview_path, [1, 2, 3])
        ImageDriverHelper.add_asset(assets, overview_path, Role.overview, MimeType.JPG, AssetFormat.jpg, ResourceType.other, airs__managed=True)

        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        setup_gdal()

        with AccessManager.make_local(self.md_path) as local_md_path:
            tree = ET.parse(local_md_path)
            root = tree.getroot()

            for p_info in root.iter('Product_Info'):
                start_time = Driver.__get_property(p_info, 'PRODUCT_START_TIME')
                start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%fZ")
                stop_time = Driver.__get_property(p_info, 'PRODUCT_STOP_TIME')
                stop_time = datetime.strptime(stop_time, "%Y-%m-%dT%H:%M:%S.%fZ")
                level = Driver.__get_property(p_info, 'PROCESSING_LEVEL')
                secondary_id = Driver.__get_property(p_info, "PRODUCT_URI")
                satellite = Driver.__get_property(p_info, 'Datatake/SPACECRAFT_NAME')
                orbit_direction = Driver.__get_property(p_info, 'Datatake/SENSING_ORBIT_DIRECTION')
                orbit_number = Driver.__get_property(p_info, "Datatake/SENSING_ORBIT_NUMBER")

            for p_info in root.iter('Cloud_Coverage_Assessment'):
                cloud_cover = p_info.text
            for p_info in root.iter('Snow_Coverage_Assessment'):
                snow_cover = p_info.text

            for coords in root.iter('EXT_POS_LIST'):
                corners = coords.text.removesuffix(' ').split(' ')
                lats = [float(c) for (i, c) in enumerate(corners) if i % 2 == 0]
                lons = [float(c) for (i, c) in enumerate(corners) if i % 2 == 1]

                geometry, bbox, centroid = get_geom_bbox_centroid(
                    lons[0], lats[0], lons[1], lats[1], lons[2], lats[2], lons[3], lats[3]
                )

            eo__bands: list[Band] = []
            for bands in root.iter("Spectral_Information_List"):
                for band in bands.iter('Spectral_Information'):
                    band_id = band.get('bandId')
                    eo__bands.append(Band(
                        asset=band.get('physicalBand'),
                        name=band.get('physicalBand'),
                        eo__common_name=BANDS_NAME.get(band_id, ''),
                        eo__center_wavelength=Driver.__get_property(band, 'Wavelength/CENTRAL')
                    ))

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
                satellite=satellite,
                secondary_id=secondary_id,
                item_format=ItemFormat.safe,
                main_asset_format=AssetFormat.jpg2000,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.optic.value,
                eo__cloud_cover=cloud_cover,
                eo__snow_cover=snow_cover,
                processing__level=level,
                acq__acquisition_orbit_direction=orbit_direction,
                acq__acquisition_orbit=orbit_number,
                proj__epsg=get_epsg(AccessManager.get_gdal_proj(self.tci_path))
            ),
            assets=dict([(asset.name, asset) for asset in assets])
        )

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
            return self.quicklook_path and self.md_path and self.tci_path and len(self.band_paths) > 0
        return False

    @staticmethod
    def __get_property(n: ET.Element, key: str):
        element = n.find(key)
        if element is not None:
            return element.text
        return None
