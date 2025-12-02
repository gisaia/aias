import os
import xml.etree.ElementTree as ET
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    get_epsg_from_gdal_info, get_geom_bbox_centroid, get_product_values)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):
    def __init__(self):
        super().__init__()
        self.name = None
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

        ImageDriverHelper.add_asset(assets, self.thumbnail_path, Role.thumbnail,
                                    MimeType.PNG, AssetFormat.png, ResourceType.other, airs__managed=True)
        ImageDriverHelper.add_asset(assets, self.quicklook_path, Role.overview,
                                    MimeType.PNG, AssetFormat.png, ResourceType.other, airs__managed=True)
        ImageDriverHelper.add_asset(assets, self.md_path, Role.metadata,
                                    MimeType.XML, AssetFormat.xml, ResourceType.other)

        for measurement in self.measurements:
            # Polarization of the measure is used as name
            polarization = os.path.basename(measurement).split('-')[3]
            name = ' '.join(os.path.basename(measurement).split('-')[1:4])

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

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
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

        with AccessManager.make_local(self.md_path) as local_md_path:
            tree = ET.parse(local_md_path)
            root = tree.getroot()

        coords = root.find(".//safe:footPrint/gml:coordinates", ns).text
        [ul_lat, ul_lon, ur_lat, ur_lon, lr_lat, lr_lon, ll_lat, ll_lon] = ",".join(coords.split(" ")).split(",")
        geometry, bbox, centroid = get_geom_bbox_centroid(float(ul_lon), float(ul_lat), float(ur_lon), float(ur_lat), float(lr_lon), float(lr_lat), float(ll_lon), float(ll_lat))

        start_time = root.find(".//safe:acquisitionPeriod/safe:startTime", ns).text
        start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%f")
        stop_time = root.find(".//safe:acquisitionPeriod/safe:stopTime", ns).text
        stop_time = datetime.strptime(stop_time, "%Y-%m-%dT%H:%M:%S.%f")

        satellite = os.path.dirname(self.md_path).split("_")[0]
        level = root.find(".//xfdu:contentUnit", ns).attrib["textInfo"].split(" ")[2]
        orbit_number = float(root.find(".//safe:orbitReference/safe:orbitNumber", ns).text)
        orbit_direction = root.find(".//safe:orbitReference//safe:extension/s1:orbitProperties/s1:pass", ns).text

        item = Item(
            id=self.get_item_id(url),
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=start_time,
                start_datetime=start_time,
                end_datetime=stop_time,
                constellation="Sentinel 1",
                satellite=satellite,
                instrument=satellite,
                sensor=satellite,
                sensor_type=SensorType.SAR,
                item_format=ItemFormat.safe,
                main_asset_format=AssetFormat.geotiff,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.radar,
                processing__level=level,
                acq__acquisition_orbit_direction=orbit_direction,
                acq__acquisition_orbit=orbit_number,
                proj__epsg=get_epsg_from_gdal_info(self.main_asset_path)
            ),
            assets=dict([(asset.name, asset) for asset in assets])
        )
        product_values = get_product_values(self.name)
        if product_values and "max_pixel_spacing" in product_values:
            item.properties.gsd = product_values["max_pixel_spacing"]
        return item

    def __check_path__(self, path: str):
        self.__init__()
        name = os.path.basename(path)

        if AccessManager.is_dir(path) and name.startswith("S1") and name.endswith(".SAFE"):
            self.name = name
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
