import os
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    downsample_image, geotiff_to_jpg, get_epsg,
    get_geom_bbox_centroid_from_corners)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):
    synonyms = {
        "UPPERLEFTCORNERLATITUDE": "NORTHBOUNDINGCOORDINATE",
        "UPPERLEFTCORNERLONGITUDE": "WESTBOUNDINGCOORDINATE",
        "UPPERRIGHTCORNERLATITUDE": "NORTHBOUNDINGCOORDINATE",
        "UPPERRIGHTCORNERLONGITUDE": "EASTBOUNDINGCOORDINATE",
        "LOWERRIGHTCORNERLATITUDE": "SOUTHBOUNDINGCOORDINATE",
        "LOWERRIGHTCORNERLONGITUDE": "EASTBOUNDINGCOORDINATE",
        "LOWERLEFTCORNERLATITUDE": "SOUTHBOUNDINGCOORDINATE",
        "LOWERLEFTCORNERLONGITUDE": "WESTBOUNDINGCOORDINATE",
    }

    configuration: dict = {}

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)
        Driver.configuration = configuration or {}

    def __init__(self):
        super().__init__()
        self.met_path = None
        self.tif_path = None
        self.tfw_path = None

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        ImageDriverHelper.add_archive(assets, url)

        ImageDriverHelper.add_asset(assets, self.tif_path, Role.data, MimeType.TIFF, AssetFormat.geotiff, ResourceType.gridded)
        ImageDriverHelper.add_asset(assets, self.met_path, Role.metadata, MimeType.PVL, AssetFormat.pvl, ResourceType.other)

        if self.tfw_path:
            ImageDriverHelper.add_asset(assets, self.tfw_path, Role.extent, MimeType.TEXT, AssetFormat.tfw, ResourceType.other)
        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if (self.tif_path and AccessManager.is_local(self.tif_path) and Driver.configuration.get('build_overview_when_local', True)) or (self.tif_path and not AccessManager.is_local(self.tif_path) and Driver.configuration.get('build_overview_when_remote', False)):
            quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
            geotiff_to_jpg(self.tif_path, Driver.OVERVIEW_FROM_TIFF_PCT, Driver.OVERVIEW_FROM_TIFF_PCT, quicklook.href, stretch=Driver.configuration.get('overview_stretch', False))
            quicklook.size = AccessManager.get_size(quicklook.href)
            assets.append(quicklook)

            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.JPG, AssetFormat.jpg)
            downsample_image(quicklook.href, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR)
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)
        return assets

    def load_metadata(self, url: str) -> dict:
        import pvl

        with AccessManager.make_local(self.met_path) as local_met_path:
            data = pvl.load(local_met_path)

        return data

    def build_core_item(self, url: str, assets: list[Asset], metadata: dict) -> Item:
        ul_lat = float(self.__get_corner_coord__(metadata, "UPPERLEFTCORNERLATITUDE"))
        ul_lon = float(self.__get_corner_coord__(metadata, "UPPERLEFTCORNERLONGITUDE"))
        ur_lat = float(self.__get_corner_coord__(metadata, "UPPERRIGHTCORNERLATITUDE"))
        ur_lon = float(self.__get_corner_coord__(metadata, "UPPERRIGHTCORNERLONGITUDE"))
        lr_lat = float(self.__get_corner_coord__(metadata, "LOWERRIGHTCORNERLATITUDE"))
        lr_lon = float(self.__get_corner_coord__(metadata, "LOWERRIGHTCORNERLONGITUDE"))
        ll_lat = float(self.__get_corner_coord__(metadata, "LOWERLEFTCORNERLATITUDE"))
        ll_lon = float(self.__get_corner_coord__(metadata, "LOWERLEFTCORNERLONGITUDE"))
        geometry, bbox, centroid = get_geom_bbox_centroid_from_corners(
            ul_lon, ul_lat, ur_lon, ur_lat, lr_lon, lr_lat, ll_lon, ll_lat
        )

        time = metadata["INVENTORYMETADATA"]["SINGLEDATETIME"]["TIMEOFDAY"]["VALUE"]
        date = metadata["INVENTORYMETADATA"]["SINGLEDATETIME"]["CALENDARDATE"]["VALUE"]
        date_time = int(
            datetime.strptime(
                (date + " " + time).rstrip("Z").rstrip("0"), "%Y-%m-%d %H:%M:%S.%f"
            ).timestamp()
        )

        constellation = (
            metadata["INVENTORYMETADATA"]
            .get("PLATFORMINSTRUMENTSENSOR", {})
            .get("PLATFORMSHORTNAME", {})
            .get("VALUE", None))

        item = Item(
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                constellation=constellation,
                satellite=constellation,
                sensor_type=SensorType.OPTIC.value,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.ast_dem.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.dem.value,
            ),
            assets={asset.name: asset for asset in assets}
        )

        return item

    def add_major_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        item.properties.secondary_id = (
            metadata.get("INVENTORYMETADATA", {})
            .get("ECSDATAGRANULE", {})
            .get("LOCALGRANULEID", {})
            .get("VALUE", None))

        item.properties.processing__level = (
            metadata.get("INVENTORYMETADATA", {})
            .get("COLLECTIONDESCRIPTIONCLASS", {})
            .get("SHORTNAME", {})
            .get("VALUE", None))

        gsd_row = (
            metadata.get("INVENTORYMETADATA", {})
            .get("SWATHSTRUCTUREINFO", {})
            .get("CROSSTRACKPIXELRESOLUTION", {})
            .get("VALUE", None))
        if gsd_row:
            gsd_row = float(gsd_row)
        gsd_col = (
            metadata.get("INVENTORYMETADATA", {})
            .get("SWATHSTRUCTUREINFO", {})
            .get("ALONGTRACKPIXELRESOLUTION", {})
            .get("VALUE", None))
        if gsd_col:
            gsd_col = float(gsd_col)
        gsd = None
        if gsd_col and gsd_row:
            gsd = (gsd_col + gsd_row) / 2
        item.properties.gsd = gsd

        item.properties.proj__epsg = get_epsg(AccessManager.get_gdal_proj(self.tif_path))

        return item

    def add_minor_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        eo__cloud_cover = (
            metadata.get("INVENTORYMETADATA", {})
            .get("CLOUDCOVERAGE", {})
            .get("SCENECLOUDCOVERAGE", {})
            .get("VALUE", None))
        if eo__cloud_cover:
            item.properties.eo__cloud_cover = float(eo__cloud_cover)

        item.properties.instrument = (
            metadata.get("INVENTORYMETADATA", {})
            .get("PLATFORMINSTRUMENTSENSOR", {})
            .get("INSTRUMENTSHORTNAME", {})
            .get("VALUE", None))

        item.properties.sensor = (
            metadata.get("INVENTORYMETADATA", {})
            .get("PLATFORMINSTRUMENTSENSOR", {})
            .get("PLATFORMSHORTNAME", {})
            .get("VALUE", None)
        )

        view__sun_azimuth = (
            metadata.get("INVENTORYMETADATA", {})
            .get("PRODUCTSPECIFICMETADATA", {})
            .get("SOLAR_AZIMUTH_ANGLE", {})
            .get("VALUE", None))
        if view__sun_azimuth:
            item.properties.view__sun_azimuth = float(view__sun_azimuth)

        view__sun_elevation = (
            metadata.get("INVENTORYMETADATA", {})
            .get("PRODUCTSPECIFICMETADATA", {})
            .get("SOLAR_ELEVATION_ANGLE", {})
            .get("VALUE", None))
        if view__sun_elevation:
            item.properties.view__sun_elevation = float(view__sun_elevation)

        return item

    def __check_path__(self, path: str):
        self.__init__()
        if AccessManager.is_dir(path):
            for f in AccessManager.listdir(path):
                self.tif_path = f.path
                if AccessManager.is_file(self.tif_path) and self.tif_path.lower().endswith((".tif", ".tiff")):
                    tfw_path = os.path.splitext(self.tif_path)[0] + ".tfw"
                    if AccessManager.exists(tfw_path):
                        self.tfw_path = tfw_path
                    met_path = os.path.splitext(self.tif_path)[0] + ".tif.met"
                    if AccessManager.exists(met_path):
                        self.met_path = met_path
                    return self.tif_path is not None and self.met_path is not None
        return False

    def __get_corner_coord__(self, data, corner: str):
        if data["INVENTORYMETADATA"]["SPATIALDOMAINCONTAINER"][
            "HORIZONTALSPATIALDOMAINCONTAINER"
        ].get("BOUNDINGBOX"):
            return data["INVENTORYMETADATA"]["SPATIALDOMAINCONTAINER"][
                "HORIZONTALSPATIALDOMAINCONTAINER"
            ]["BOUNDINGBOX"][corner]["VALUE"]
        if data["INVENTORYMETADATA"]["SPATIALDOMAINCONTAINER"][
            "HORIZONTALSPATIALDOMAINCONTAINER"
        ].get("BOUNDINGRECTANGLE"):
            return data["INVENTORYMETADATA"]["SPATIALDOMAINCONTAINER"][
                "HORIZONTALSPATIALDOMAINCONTAINER"
            ]["BOUNDINGRECTANGLE"][Driver.synonyms.get(corner)]["VALUE"]
        return None
