import xml.etree.ElementTree as ET
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    downsample_image, geotiff_to_jpg, get_epsg_from_gdal_info,
    get_geom_bbox_centroid_from_corners)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):

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
            assets.append(Asset(href=pol['path'], size=AccessManager.get_size(pol['path']), proj__epsg=get_epsg_from_gdal_info(pol['path']),
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
        quicklook_pct = 100
        if self.browse_path:
            image_path = self.browse_path
        elif AccessManager.is_local(self.polarizations[0]['path']):
            image_path = self.polarizations[0]['path']
            quicklook_pct = 25

        if image_path:
            quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
            geotiff_to_jpg(image_path, quicklook_pct, quicklook_pct, output_path=quicklook.href)
            quicklook.size = AccessManager.get_size(quicklook.href)
            assets.append(quicklook)

            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.JPG, AssetFormat.jpg)
            downsample_image(quicklook.href, thumbnail.href, 4)
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)
        return assets

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        ns = {"rs2": "http://www.rsi.ca/rs2/prod/xml/schemas"}  # NOSONAR
        with AccessManager.make_local(self.md_path) as local_md_path:
            tree = ET.parse(local_md_path)
            root = tree.getroot()
        tiepoints = []
        # Loop on tie points
        for tp in root.findall(".//rs2:imageTiePoint", ns):
            line = float(tp.find("rs2:imageCoordinate/rs2:line", ns).text)
            pixel = float(tp.find("rs2:imageCoordinate/rs2:pixel", ns).text)
            lat = float(tp.find("rs2:geodeticCoordinate/rs2:latitude", ns).text)
            lon = float(tp.find("rs2:geodeticCoordinate/rs2:longitude", ns).text)
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

        start_time = root.find(".//rs2:zeroDopplerTimeFirstLine", ns).text
        start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        stop_time = root.find(".//rs2:zeroDopplerTimeLastLine", ns).text
        stop_time = datetime.strptime(stop_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        satellite = root.find(".//rs2:satellite", ns).text
        product_level = root.find(".//rs2:productType", ns).text
        orbit_direction = root.find(".//rs2:passDirection", ns).text

        pixel_spacing = root.find(".//rs2:sampledPixelSpacing", ns).text
        line_spacing = root.find(".//rs2:sampledLineSpacing", ns).text
        gsd = max(float(pixel_spacing), float(line_spacing))

        orbit_data_file = root.find(".//rs2:orbitDataFile", ns).text
        orbit_number = orbit_data_file.split('_')[0]
        item = Item(
            id=self.get_item_id(url),
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=start_time,
                start_datetime=start_time,
                end_datetime=stop_time,
                constellation=satellite,
                satellite=satellite,
                instrument=satellite,
                sensor=satellite,
                sensor_type=SensorType.SAR,
                item_format=ItemFormat.radarsat2,
                main_asset_format=AssetFormat.geotiff,
                main_asset_name=self.polarizations[0]['name'],
                observation_type=ObservationType.radar,
                processing__level=product_level,
                gsd=gsd,
                acq__acquisition_orbit_direction=orbit_direction,
                acq__acquisition_orbit=orbit_number,
                sar__polarizations=map(lambda x: x['polarization'], self.polarizations),
                proj__epsg=get_epsg_from_gdal_info(self.polarizations[0]['path'])
            ),
            assets={asset.name: asset for asset in assets}
        )
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
