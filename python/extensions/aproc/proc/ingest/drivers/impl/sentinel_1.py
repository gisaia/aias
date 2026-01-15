import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    find_or_none, get_epsg_from_gdal_info, get_geom_bbox_centroid_from_corners)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver

# Level-1 Product Family Summary Table Dictionary
level1_summary = {
    'SM': {
        'SLC': {'resolution': '1.7-3.6 m x 4.3-4.9 m', 'pixel_spacing': '1.5-3.1 m x 3.6-4.1 m', 'looks': '1 x 1', 'ENL': 1},
        'GRD_FR': {'resolution': '9 x 9 m', 'pixel_spacing': '3.5 x 3.5 m', 'looks': '2 x 2', 'ENL': 3.7},
        'GRD_HR': {'resolution': '23 x 23 m', 'pixel_spacing': '10 x 10 m', 'looks': '6 x 6', 'ENL': 29.7},
        'GRD_MR': {'resolution': '84 x 84 m', 'pixel_spacing': '40 x 40 m', 'looks': '22 x 22', 'ENL': 398.4},
    },
    'IW': {
        'SLC': {'resolution': '2.7-3.5 m x 22 m', 'pixel_spacing': '2.3 m x 14.1 m', 'looks': '1 x 1', 'ENL': 1},
        'GRD_HR': {'resolution': '20 x 22 m', 'pixel_spacing': '10 x 10 m', 'looks': '5 x 1', 'ENL': 4.4},
        'GRD_MR': {'resolution': '88 x 87 m', 'pixel_spacing': '40 x 40 m', 'looks': '22 x 5', 'ENL': 81.8},
    },
    'EW': {
        'SLC': {'resolution': '7.9-15 m x 43 m', 'pixel_spacing': '5.9 x 19.9 m', 'looks': '1 x 1', 'ENL': 1},
        'GRD_HR': {'resolution': '50 x 50 m', 'pixel_spacing': '25 x 25 m', 'looks': '3 x 1', 'ENL': 2.8},
        'GRD_MR': {'resolution': '93 x 87 m', 'pixel_spacing': '40 x 40 m', 'looks': '6 x 2', 'ENL': 10.7},
    },
    'WV': {
        'SLC': {'resolution': '2.0-3.1 m x 4.8 m', 'pixel_spacing': '1.7-2.7 m x 4.1 m', 'looks': '1 x 1', 'ENL': 1},
        'GRD_MR': {'resolution': '52 x 51 m', 'pixel_spacing': '25 x 25 m', 'looks': '13 x 13', 'ENL': 123.7},
    }
}


def parse_sentinel1_filename(filename):
    base = filename.split('/')[-1]
    parts = base.split('_')

    if len(parts) < 3:
        raise ValueError("Invalid name File")

    satellite = parts[0]  # S1A, S1B, S1C
    mode = parts[1]       # SM, IW, EW, WV
    product_type = parts[2]  # SLC, GRD

    res_pol = parts[3] if len(parts) > 3 else ''

    return satellite, mode, product_type, res_pol


def extract_pixel_spacing_numbers(pixel_spacing_str):
    """
    Extracts the numerical values of the pixel spacing (range x azimuth)
    """
    # Remove the units and separate by x
    nums = re.findall(r'[\d\.]+', pixel_spacing_str)
    if len(nums) >= 2:
        return float(nums[0]), float(nums[1])
    else:
        return float(nums[0]), float(nums[0])  # if only one number, we repeat


def get_product_values(filename):
    sat, mode, prod_type, _ = parse_sentinel1_filename(filename)

    if prod_type.startswith('GRD'):
        if 'FR' in filename:
            prod_key = 'GRD_FR'
        elif 'HR' in filename:
            prod_key = 'GRD_HR'
        elif 'MR' in filename:
            prod_key = 'GRD_MR'
        else:
            prod_key = 'GRD_MR'
    else:
        prod_key = prod_type

    try:
        values = level1_summary[mode][prod_key]
    except KeyError:
        raise ValueError(f"Mode {mode} or type {prod_key} unknown in the Level-1 array.")

    range_ps, azimuth_ps = extract_pixel_spacing_numbers(values['pixel_spacing'])
    max_pixel_spacing = max(range_ps, azimuth_ps)

    result = {
        'satellite': sat,
        'mode': mode,
        'product_type': prod_type,
        'resolution': values['resolution'],
        'pixel_spacing': values['pixel_spacing'],
        'looks': values['looks'],
        'ENL': values['ENL'],
        'max_pixel_spacing': max_pixel_spacing
    }

    return result


class Driver(IngestDriver):
    ns = {
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "gml": "http://www.opengis.net/gml",
        "xfdu": "urn:ccsds:schema:xfdu:1",
        "safe": "http://www.esa.int/safe/sentinel-1.0",
        "s1": "http://www.esa.int/safe/sentinel-1.0/sentinel-1",
        "s1sar": "http://www.esa.int/safe/sentinel-1.0/sentinel-1/sar",
        "s1sarl1": "http://www.esa.int/safe/sentinel-1.0/sentinel-1/sar/level-1",
        "s1sarl2": "http://www.esa.int/safe/sentinel-1.0/sentinel-1/sar/level-2",
        "gx": "http://www.google.com/kml/ext/2.2"
    }

    def __init__(self):
        super().__init__()
        self.file_name = None
        self.md_path = None
        self.quicklook_path = None
        self.thumbnail_path = None
        self.measurements: list[str] = []
        self.main_asset_path = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        ImageDriverHelper.add_archive(assets, url)

        ImageDriverHelper.add_asset(assets, self.thumbnail_path, Role.thumbnail,
                                    MimeType.PNG, AssetFormat.png, ResourceType.other, airs__managed=True)
        ImageDriverHelper.add_asset(assets, self.quicklook_path, Role.overview,
                                    MimeType.PNG, AssetFormat.png, ResourceType.other, airs__managed=True)
        ImageDriverHelper.add_asset(assets, self.md_path, Role.metadata,
                                    MimeType.XML, AssetFormat.xml, ResourceType.other)

        for measurement in self.measurements:
            # Polarization of the measure is used as name
            polarization = os.path.basename(measurement).split('-')[3]
            name = self.__get_measurement_name__(measurement)

            # According to copernicus website, could end in .cog.tiff
            assets.append(Asset(href=measurement, size=AccessManager.get_size(measurement), roles=[Role.data.value],
                                name=name, type=MimeType.GEOTIFF.value, description=name,
                                airs__managed=False, asset_format=AssetFormat.geotiff.value,
                                asset_type=ResourceType.gridded.value, sar__polarizations=[polarization.upper()]))

        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    def load_metadata(self, url: str) -> object:
        with AccessManager.make_local(self.md_path) as local_md_path:
            tree = ET.parse(local_md_path)
            root = tree.getroot()

        return root

    def build_core_item(self, url: str, assets: list[Asset], root: ET.Element) -> Item:
        coords = root.find(".//safe:footPrint/gml:coordinates", Driver.ns).text
        [ul_lat, ul_lon, ur_lat, ur_lon, lr_lat, lr_lon, ll_lat, ll_lon] = ",".join(coords.split(" ")).split(",")
        geometry, bbox, centroid = get_geom_bbox_centroid_from_corners(float(ul_lon), float(ul_lat), float(ur_lon), float(ur_lat), float(lr_lon), float(lr_lat), float(ll_lon), float(ll_lat))

        start_time = root.find(".//safe:acquisitionPeriod/safe:startTime", Driver.ns).text
        start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%f")
        stop_time = root.find(".//safe:acquisitionPeriod/safe:stopTime", Driver.ns).text
        stop_time = datetime.strptime(stop_time, "%Y-%m-%dT%H:%M:%S.%f")

        constellation = root.find(".//safe:platform/safe:familyName", Driver.ns).text

        item = Item(
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=start_time,
                start_datetime=start_time,
                end_datetime=stop_time,
                constellation=constellation,
                sensor_type=SensorType.SAR,
                item_format=ItemFormat.safe,
                item_type=ResourceType.gridded.value,
                main_asset_format=AssetFormat.geotiff,
                main_asset_name=self.__get_measurement_name__(self.measurements[0]),
                observation_type=ObservationType.radar
            ),
            assets={asset.name: asset for asset in assets}
        )

        return item

    def add_major_metadata(self, url: str, item: Item, root: ET.Element) -> Item:
        satellite_number = find_or_none(root, ".//safe:platform/safe:number", ns=Driver.ns)
        if satellite_number:
            item.properties.satellite = item.properties.constellation + satellite_number

        processing__level = root.find(".//xfdu:contentUnit", Driver.ns)
        if processing__level:
            textInfo = processing__level.attrib.get("textInfo", None)
            if textInfo:
                item.properties.processing__level = textInfo.split(" ")[2]

        item.properties.proj__epsg = get_epsg_from_gdal_info(self.main_asset_path)

        product_values = get_product_values(self.file_name)
        if product_values and "max_pixel_spacing" in product_values:
            item.properties.gsd = product_values["max_pixel_spacing"]

        return item

    def add_minor_metadata(self, url: str, item: Item, root: ET.Element) -> Item:
        item.properties.instrument = item.properties.satellite
        item.properties.acq__acquisition_orbit_direction = find_or_none(root, ".//safe:orbitReference//safe:extension/s1:orbitProperties/s1:pass", ns=Driver.ns)
        item.properties.acq__acquisition_orbit = find_or_none(root, ".//safe:orbitReference/safe:orbitNumber", lambda x: float(x), ns=Driver.ns)

        sensor = root.find(".//s1sarl1:mode", Driver.ns)
        if sensor is None:
            sensor = root.find(".//s1sarl2:mode", Driver.ns)
        if sensor is not None:
            item.properties.sensor = sensor.text

        return item

    def __check_path__(self, path: str):
        self.__init__()
        name = os.path.basename(path)

        if AccessManager.is_dir(path) and name.startswith("S1") and name.endswith(".SAFE"):
            self.file_name = name
            for file in AccessManager.listdir(path):
                if not file.is_dir and file.name == "manifest.safe":
                    self.md_path = file.path

                if file.is_dir:
                    if file.name == "preview":
                        for preview in AccessManager.listdir(file.path):
                            if preview.name == "quick-look.png":
                                self.quicklook_path = preview.path
                            if preview.name == "thumbnail.png":
                                self.thumbnail_path = preview.path

                    if file.name == "measurement":
                        for measurement in AccessManager.listdir(file.path):
                            if measurement.name.endswith(".tiff"):
                                self.measurements.append(measurement.path)

                                # Arbitrarily choose the main asset as the first one encountered
                                if self.main_asset_path is None:
                                    self.main_asset_path = measurement.path

            return self.md_path is not None \
                and self.quicklook_path is not None \
                and self.thumbnail_path is not None \
                and self.main_asset_path is not None \
                and len(self.measurements) > 0

        return False

    def __get_measurement_name__(self, measurement: str):
        return '_'.join(os.path.basename(measurement).split('-')[1:4])
