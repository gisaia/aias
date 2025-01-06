import os
from datetime import datetime
from pathlib import Path


from airs.core.models.model import (
    Asset,
    AssetFormat,
    Item,
    ItemFormat,
    MimeType,
    ObservationType,
    Properties,
    ResourceType,
    Role,
)
from aproc.core.settings import Configuration
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    get_geom_bbox_centroid,
    get_hash_url,
    get_file_size,
    get_epsg,
)
from .image_driver_helper import ImageDriverHelper


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

    def __init__(self):
        super().__init__()
        self.met_path = None
        self.tif_path = None
        self.tfw_path = None

    # Implements drivers method
    def init(self, configuration: Configuration):
        return

    # Implements drivers method
    def supports(self, url: str) -> bool:
        try:
            result = self.__check_path__(url)
            return result
        except Exception as e:
            self.LOGGER.warn(e)
            return False

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        assets.append(
            Asset(
                href=self.tif_path,
                size=get_file_size(self.tif_path),
                roles=[Role.data.value],
                name=Role.data.value,
                type=MimeType.TIFF.value,
                description=Role.data.value,
                airs__managed=False,
                asset_format=AssetFormat.geotiff.value,
                asset_type=ResourceType.gridded.value,
            )
        )
        assets.append(
            Asset(
                href=self.met_path,
                size=get_file_size(self.met_path),
                roles=[Role.metadata.value],
                name=Role.metadata.value,
                type=MimeType.PVL.value,
                description=Role.metadata.value,
                airs__managed=False,
                asset_format=AssetFormat.pvl.value,
                asset_type=ResourceType.other.value,
            )
        )
        if self.tfw_path:
            assets.append(
                Asset(
                    href=self.tfw_path,
                    size=get_file_size(self.tfw_path),
                    roles=[Role.extent.value],
                    name=Role.extent.value,
                    type=MimeType.TEXT.value,
                    description=Role.metadata.value,
                    airs__managed=False,
                    asset_format=AssetFormat.tfw.value,
                    asset_type=ResourceType.other.value,
                )
            )
        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        ImageDriverHelper.add_overview_if_you_can(
            self, self.tif_path, Role.thumbnail, self.thumbnail_size, assets
        )
        ImageDriverHelper.add_overview_if_you_can(
            self, self.tif_path, Role.overview, self.overview_size, assets
        )
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def get_item_id(self, url: str) -> str:
        return get_hash_url(url)

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        import pvl

        data = pvl.load(self.met_path)
        ul_lat = float(self.__get_corner_coord__(data, "UPPERLEFTCORNERLATITUDE"))
        ul_lon = float(self.__get_corner_coord__(data, "UPPERLEFTCORNERLONGITUDE"))
        ur_lat = float(self.__get_corner_coord__(data, "UPPERRIGHTCORNERLATITUDE"))
        ur_lon = float(self.__get_corner_coord__(data, "UPPERRIGHTCORNERLONGITUDE"))
        lr_lat = float(self.__get_corner_coord__(data, "LOWERRIGHTCORNERLATITUDE"))
        lr_lon = float(self.__get_corner_coord__(data, "LOWERRIGHTCORNERLONGITUDE"))
        ll_lat = float(self.__get_corner_coord__(data, "LOWERLEFTCORNERLATITUDE"))
        ll_lon = float(self.__get_corner_coord__(data, "LOWERLEFTCORNERLONGITUDE"))
        geometry, bbox, centroid = get_geom_bbox_centroid(
            ul_lon, ul_lat, ur_lon, ur_lat, lr_lon, lr_lat, ll_lon, ll_lat
        )
        time = data["INVENTORYMETADATA"]["SINGLEDATETIME"]["TIMEOFDAY"]["VALUE"]
        date = data["INVENTORYMETADATA"]["SINGLEDATETIME"]["CALENDARDATE"]["VALUE"]
        date_time = int(
            datetime.strptime(
                (date + " " + time).rstrip("Z").rstrip("0"), "%Y-%m-%d %H:%M:%S.%f"
            ).timestamp()
        )
        processing__level = (
            data["INVENTORYMETADATA"]
            .get("COLLECTIONDESCRIPTIONCLASS", {})
            .get("SHORTNAME", {})
            .get("VALUE", None)
        )
        eo__cloud_cover = (
            data["INVENTORYMETADATA"]
            .get("CLOUDCOVERAGE", {})
            .get("SCENECLOUDCOVERAGE", {})
            .get("VALUE", None)
        )
        if eo__cloud_cover:
            eo__cloud_cover = float(eo__cloud_cover)
        gsdRow = (
            data["INVENTORYMETADATA"]
            .get("SWATHSTRUCTUREINFO", {})
            .get("CROSSTRACKPIXELRESOLUTION", {})
            .get("VALUE", None)
        )
        if gsdRow:
            gsdRow = float(gsdRow)
        gsdCol = (
            data["INVENTORYMETADATA"]
            .get("SWATHSTRUCTUREINFO", {})
            .get("ALONGTRACKPIXELRESOLUTION", {})
            .get("VALUE", None)
        )
        if gsdCol:
            gsdCol = float(gsdCol)
        gsd = None
        if gsdCol and gsdRow:
            gsd = (gsdCol + gsdRow) / 2
        constellation = (
            data["INVENTORYMETADATA"]
            .get("PLATFORMINSTRUMENTSENSOR", {})
            .get("PLATFORMSHORTNAME", {})
            .get("VALUE", None)
        )
        instrument = (
            data["INVENTORYMETADATA"]
            .get("PLATFORMINSTRUMENTSENSOR", {})
            .get("INSTRUMENTSHORTNAME", {})
            .get("VALUE", None)
        )
        sensor = (
            data["INVENTORYMETADATA"]
            .get("PLATFORMINSTRUMENTSENSOR", {})
            .get("PLATFORMSHORTNAME", {})
            .get("VALUE", None)
        )
        view__sun_azimuth = (
            data["INVENTORYMETADATA"]
            .get("PRODUCTSPECIFICMETADATA", {})
            .get("SOLAR_AZIMUTH_ANGLE", {})
            .get("VALUE", None)
        )
        if view__sun_azimuth:
            view__sun_azimuth = float(view__sun_azimuth)
        view__sun_elevation = (
            data["INVENTORYMETADATA"]
            .get("PRODUCTSPECIFICMETADATA", {})
            .get("SOLAR_ELEVATION_ANGLE", {})
            .get("VALUE", None)
        )
        if view__sun_elevation:
            view__sun_elevation = float(view__sun_elevation)
        from osgeo import gdal
        from osgeo.gdalconst import GA_ReadOnly

        src_ds = gdal.Open(self.tif_path, GA_ReadOnly)
        item = Item(
            id=self.get_item_id(url),
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                eo__cloud_cover=eo__cloud_cover,
                processing__level=processing__level,
                gsd=gsd,
                proj__epsg=get_epsg(src_ds),
                instrument=instrument,
                constellation=constellation,
                sensor=sensor,
                view__sun_azimuth=view__sun_azimuth,
                view__sun_elevation=view__sun_elevation,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.ast_dem.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.dem.value,
            ),
            assets=dict(map(lambda asset: (asset.name, asset), assets)),
        )
        return item

    def __check_path__(self, path: str):
        self.tif_path = None
        self.met_path = None
        valid_and_exist = os.path.isdir(path) and os.path.exists(path)
        if valid_and_exist:
            for f in os.listdir(path):
                self.tif_path = os.path.join(path, f)
                if Path(self.tif_path).is_file() and self.tif_path.lower().endswith((".tif", ".tiff")):
                    tfw_path = Path(self.tif_path).with_suffix(".tfw")
                    if tfw_path.exists():
                        self.tfw_path = str(tfw_path)
                    met_path = Path(self.tif_path).with_suffix(".tif.met")
                    if met_path.exists():
                        self.met_path = str(met_path)
                    return self.tif_path is not None and self.met_path is not None
        return False

    def __get_corner_coord__(self, data, corner):
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
