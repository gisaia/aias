import xml.etree.ElementTree as ET
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    downsample_image, find_or_none, geotiff_to_jpg, get_epsg_from_gdal_info_gcps,
    get_geom_bbox_centroid_from_corners)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):
    ns = {"rs2": "http://www.rsi.ca/rs2/prod/xml/schemas"}  # NOSONAR

    def __init__(self):
        super().__init__()
        self.md_path = None
        self.tif_HH_path = None
        self.tif_HV_path = None
        self.tif_VH_path = None
        self.tif_VV_path = None
        self.polarizations = []
        self.browse_path = None

    def _add_polarization(self, name: str, path: str):
        self.polarizations.append({
            'polarization': name,
            'path': path,
            'name': f'Polarization {name}'
        })

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        ImageDriverHelper.add_archive(assets, url)

        for pol in self.polarizations:
            assets.append(Asset(href=pol['path'], size=AccessManager.get_size(pol['path']), proj__epsg=get_epsg_from_gdal_info_gcps(pol['path']),
                                roles=[Role.data.value], name=pol['name'], type=MimeType.GEOTIFF.value, sar__polarizations=[pol['polarization']],
                                description=pol['name'], airs__managed=False, asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value))
        ImageDriverHelper.add_asset(assets, self.md_path, Role.metadata,
                                    MimeType.XML, AssetFormat.xml, ResourceType.other)

        if self.browse_path:
            ImageDriverHelper.add_asset(assets, self.browse_path, Role.visual, MimeType.TIFF, AssetFormat.geotiff, ResourceType.gridded)
        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        image_path = None
        quicklook_pct = Driver.OVERVIEW_FROM_BROWSE_PCT
        if self.browse_path:
            image_path = self.browse_path
        elif AccessManager.is_local(self.polarizations[0]['path']):
            image_path = self.polarizations[0]['path']
            quicklook_pct = Driver.OVERVIEW_FROM_TIFF_PCT

        if image_path:
            quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
            geotiff_to_jpg(image_path, quicklook_pct, quicklook_pct, output_path=quicklook.href)
            quicklook.size = AccessManager.get_size(quicklook.href)
            assets.append(quicklook)

            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.JPG, AssetFormat.jpg)
            downsample_image(quicklook.href, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR)
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)
        return assets

    def load_metadata(self, url: str) -> object:
        with AccessManager.make_local(self.md_path) as local_md_path:
            tree = ET.parse(local_md_path)
            root = tree.getroot()

        return root

    def build_core_item(self, url: str, assets: list[Asset], root: ET.Element) -> Item:
        tiepoints = []
        # Loop on tie points
        for tp in root.findall(".//rs2:imageTiePoint", Driver.ns):
            line = float(tp.find("rs2:imageCoordinate/rs2:line", Driver.ns).text)
            pixel = float(tp.find("rs2:imageCoordinate/rs2:pixel", Driver.ns).text)
            lat = float(tp.find("rs2:geodeticCoordinate/rs2:latitude", Driver.ns).text)
            lon = float(tp.find("rs2:geodeticCoordinate/rs2:longitude", Driver.ns).text)
            tiepoints.append({
                "line": line,
                "pixel": pixel,
                "lat": lat,
                "lon": lon
            })
        # Find corner
        UL = min(tiepoints, key=lambda t: (t["line"], t["pixel"]))
        UR = min(tiepoints, key=lambda t: (t["line"], -t["pixel"]))
        BL = max(tiepoints, key=lambda t: (t["line"], -t["pixel"]))
        BR = max(tiepoints, key=lambda t: (t["line"], t["pixel"]))

        geometry, bbox, centroid = get_geom_bbox_centroid_from_corners(float(UL["lon"]), float(UL["lat"]), float(UR["lon"]), float(UR["lat"]), float(BR["lon"]), float(BR["lat"]), float(BL["lon"]), float(BL["lat"]))

        start_time = root.find(".//rs2:zeroDopplerTimeFirstLine", Driver.ns).text
        start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        stop_time = root.find(".//rs2:zeroDopplerTimeLastLine", Driver.ns).text
        stop_time = datetime.strptime(stop_time, "%Y-%m-%dT%H:%M:%S.%fZ")

        constellation = root.find(".//rs2:satellite", Driver.ns).text

        item = Item(
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=start_time,
                start_datetime=start_time,
                end_datetime=stop_time,
                constellation=constellation,
                sensor_type=SensorType.SAR.value,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.radarsat2,
                main_asset_format=AssetFormat.geotiff,
                main_asset_name=self.polarizations[0]['name'],
                observation_type=ObservationType.radar
            ),
            assets={asset.name: asset for asset in assets}
        )

        return item

    def add_major_metadata(self, url: str, item: Item, root: ET.Element) -> Item:
        item.properties.satellite = item.properties.constellation
        item.properties.processing__level = find_or_none(root, ".//rs2:productType", ns=Driver.ns)
        item.properties.secondary_id = find_or_none(root, ".//rs2:productId", ns=Driver.ns)

        item.properties.proj__epsg = get_epsg_from_gdal_info_gcps(self.polarizations[0]['path'])

        pixel_spacing = find_or_none(root, ".//rs2:sampledPixelSpacing", ns=Driver.ns)
        line_spacing = find_or_none(root, ".//rs2:sampledLineSpacing", ns=Driver.ns)
        if pixel_spacing and line_spacing:
            item.properties.gsd = max(float(pixel_spacing), float(line_spacing))

        return item

    def add_minor_metadata(self, url: str, item: Item, root: ET.Element) -> Item:
        item.properties.acq__acquisition_orbit_direction = find_or_none(root, ".//rs2:passDirection", ns=Driver.ns)
        item.properties.acq__acquisition_orbit = find_or_none(root, ".//rs2:orbitDataFile", lambda x: x.split('_')[0], ns=Driver.ns)

        item.properties.sar__polarizations = [x['polarization'] for x in self.polarizations]
        item.properties.instrument = item.properties.satellite
        item.properties.sensor = item.properties.satellite

        return item

    def __check_path__(self, path: str):
        self.__init__()  # Reset state
        if not AccessManager.is_dir(path):
            return False
        for file in AccessManager.listdir(path):
            if file.name == "product.xml":
                self.md_path = file.path
            elif file.name.startswith("imagery_") and file.name.endswith(".tif"):
                pol = (file.name.split("_")[1].split(".")[0]).upper()  # HH, VV, HV, VH
                self._add_polarization(pol, file.path)
            elif file.name == "BrowseImage.tif":
                self.browse_path = file.path
        return self.md_path is not None and len(self.polarizations) > 0
