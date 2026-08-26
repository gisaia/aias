import os
import tempfile
import xml.etree.ElementTree as ET
from contextlib import contextmanager
from datetime import datetime
from typing import Literal

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    downsample_image, geotiff_to_jpg, get_epsg,
    get_geom_bbox_centroid_from_corners)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


def get_value_by_prefix_suffix_or_none(dictionary: dict, prefixes: list[str], suffix: str):
    for key, value in dictionary.items():
        if key.endswith(suffix) and (not prefixes or any(key.startswith(p) for p in prefixes)):
            return value
    return None


@contextmanager
def csk_h5_scenes_to_geotiffs(h5_path: str, metadata: dict):
    import h5py
    import numpy as np
    import rasterio
    from rasterio.control import GroundControlPoint
    from rasterio.transform import from_gcps

    # Parse the QLK scenes to get their values
    with AccessManager.make_local(h5_path) as f:
        with h5py.File(f) as h5f:
            values = []

            for v in h5f.values():
                if isinstance(v, h5py.Dataset) and v.name.endswith("QLK"):
                    data: np.ndarray = v[()]
                    values.append(data)
                elif isinstance(v, h5py.Group):
                    for vv in v.values():
                        if isinstance(vv, h5py.Dataset) and vv.name.endswith("QLK"):
                            data: np.ndarray = vv[()]
                            values.append(data)

    tiffs = []
    for idx, data in enumerate(values):
        # For each scene, get the GCPs to compute its transform
        if idx + 1 < 10:
            scene = f"S0{idx + 1}_SBI"
        else:
            scene = f"S{idx + 1}_SBI"

        ul = get_value_by_prefix_suffix_or_none(metadata["metadata"][""], [scene], "Top_Left_Geodetic_Coordinates")
        ur = get_value_by_prefix_suffix_or_none(metadata["metadata"][""], [scene], "Top_Right_Geodetic_Coordinates")
        lr = get_value_by_prefix_suffix_or_none(metadata["metadata"][""], [scene], "Bottom_Right_Geodetic_Coordinates")
        ll = get_value_by_prefix_suffix_or_none(metadata["metadata"][""], [scene], "Bottom_Left_Geodetic_Coordinates")

        gcps = [
            GroundControlPoint(0, 0, float(ul.split(" ")[1]), float(ul.split(" ")[0])),
            GroundControlPoint(0, data.shape[1], float(ur.split(" ")[1]), float(ur.split(" ")[0])),
            GroundControlPoint(data.shape[0], data.shape[1], float(lr.split(" ")[1]), float(lr.split(" ")[0])),
            GroundControlPoint(data.shape[0], 0, float(ll.split(" ")[1]), float(ll.split(" ")[0]))
        ]

        width = data.shape[1]
        height = data.shape[0]

        transform = from_gcps(gcps)
        profile = {
            "driver": "GTiff",
            "dtype": data.dtype,
            "width": width,
            "height": height,
            "count": 1,
            "crs": "EPSG:4326",
            "transform": transform
        }

        # Create a tif from the h5 scene data in EPSG:4326
        tmp_tif = tempfile.NamedTemporaryFile("w+", suffix=".tif", delete=False).name
        with rasterio.open(tmp_tif, "w", **profile) as dst:
            dst.write(data, indexes=1)
        tiffs.append(tmp_tif)

    # Handle clean-up of created files
    try:
        yield tiffs
    finally:
        for tif in tiffs:
            os.remove(tif)  # !DELETE!


class Driver(IngestDriver):

    configuration: dict = {}

    def __init__(self):
        super().__init__()
        self.data_path = None
        self.data_format: Literal[AssetFormat.geotiff] | Literal[AssetFormat.h5] = None

        self.tfw_path = None
        self.attr_path = None
        self.browse_path = None
        self.h5met_path = None
        self.h5pdf_path = None
        self.quicklook_path = None
        self.thumbnail_path = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)
        Driver.configuration = configuration or {}

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        ImageDriverHelper.add_archive(assets, url)

        assets.append(Asset(href=self.data_path, size=AccessManager.get_size(self.data_path),
                            roles=[Role.data.value], name=Role.data.value, type=MimeType.TIFF.value if self.data_format == AssetFormat.geotiff else MimeType.HDF5.value,
                            description=Role.data.value, airs__managed=False, asset_format=self.data_format, asset_type=ResourceType.gridded.value))
        assets.append(Asset(href=self.h5met_path, size=AccessManager.get_size(self.h5met_path),
                            roles=[Role.metadata.value], name="h5", type=MimeType.XML.value,
                            description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.xml.value, asset_type=ResourceType.other.value))

        if self.attr_path:
            assets.append(Asset(href=self.attr_path, size=AccessManager.get_size(self.attr_path),
                                roles=[Role.metadata.value], name="attributes", type=MimeType.XML.value,
                                description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.xml.value, asset_type=ResourceType.other.value))
        if self.tfw_path:
            assets.append(Asset(href=self.tfw_path, size=AccessManager.get_size(self.tfw_path),
                                roles=[Role.extent.value], name=Role.extent.value, type=MimeType.TEXT.value,
                                description=Role.extent.value, airs__managed=False, asset_format=AssetFormat.tfw.value, asset_type=ResourceType.other.value))
        if self.h5pdf_path:
            assets.append(Asset(href=self.h5pdf_path, size=AccessManager.get_size(self.h5pdf_path),
                                roles=[Role.metadata.value], name=Role.metadata.value + "_pdf", type=MimeType.PDF.value,
                                description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.pdf.value, asset_type=ResourceType.other.value))
        if self.browse_path:
            ImageDriverHelper.add_asset(assets, self.browse_path, Role.visual, MimeType.TIFF, AssetFormat.geotiff, ResourceType.gridded)

        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if self.browse_path is not None:
            quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
            geotiff_to_jpg(self.browse_path, Driver.OVERVIEW_FROM_TIFF_PCT, Driver.OVERVIEW_FROM_TIFF_PCT, quicklook.href, stretch=Driver.configuration.get('overview_stretch', False))
            quicklook.size = AccessManager.get_size(quicklook.href)
            assets.append(quicklook)

            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.JPG, AssetFormat.jpg)
            downsample_image(quicklook.href, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR)
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)
        else:
            if IngestDriver.must_build_preview(Driver.configuration, url):
                if self.data_format == AssetFormat.h5:
                    from osgeo import gdal
                    gdal.SetConfigOption('CPL_TMPDIR', tempfile.gettempdir())

                    quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.PNG, AssetFormat.png)
                    metadata = self.load_metadata(url)

                    with csk_h5_scenes_to_geotiffs(self.data_path, metadata) as tiffs:
                        Driver.LOGGER.debug(f"Creating quicklook {quicklook.href} from scenes tiffs {tiffs}")
                        # Because of the multiple scenes, the image is wider than high, so only contrain the height
                        gdal.Warp(quicklook.href, tiffs, format="PNG", height=Driver.OVERVIEW_SIZE)
                        if not AccessManager.exists(quicklook.href):
                            raise DriverException(f"Failed to create quicklook {quicklook.href} from scenes tiffs {tiffs}")
                        quicklook.size = AccessManager.get_size(quicklook.href)
                        assets.append(quicklook)

                    # Downsample quicklook for thumbnail
                    thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.PNG, AssetFormat.png)
                    downsample_image(quicklook.href, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR)
                    thumbnail.size = AccessManager.get_size(thumbnail.href)
                    assets.append(thumbnail)

        return assets

    def load_metadata(self, url: str) -> dict:
        from osgeo import gdal

        options = gdal.InfoOptions(format="json")
        info = AccessManager.get_gdal_info(self.data_path, options)

        return info

    def build_core_item(self, url: str, assets: list[Asset], metadata: dict) -> Item:
        geometry, bbox, centroid = self.__get_geometries__(metadata)
        date_time = int(datetime.strptime(metadata["metadata"][""]["Scene_Sensing_Start_UTC"][:-3], "%Y-%m-%d %H:%M:%S.%f").timestamp())

        item = Item(
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                constellation="COSMO-SkyMed",
                sensor_type=SensorType.SAR.value,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.csk.value,
                main_asset_format=self.data_format.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.radar.value,
            ),
            assets={asset.name: asset for asset in assets}
        )

        return item

    def add_major_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        gsd = metadata["metadata"].get("", {}).get("Ground_Range_Geometric_Resolution", None)
        if gsd is None:
            gsd = metadata["metadata"].get("", {}).get("S01_Ground_Range_Instrument_Geometric_Resolution", None)
        if gsd is not None:
            item.properties.gsd = float(gsd)
        item.properties.satellite = metadata["metadata"].get("", {}).get("Satellite_ID", None)
        item.properties.secondary_id = metadata["metadata"].get("", {}).get("Product_Filename", None)

        with AccessManager.make_local(self.h5met_path) as local_h5met_path:
            h5_tree = ET.parse(local_h5met_path)
            h5_root = h5_tree.getroot()
        processing__level = h5_root.find("ProcessingInfo/ProcessingLevel")
        if processing__level is not None and processing__level.text:
            item.properties.processing__level = processing__level.text

        item.properties.proj__epsg = self.__get_proj__(metadata["metadata"].get(""), item.centroid)

        return item

    def add_minor_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        item.properties.instrument = item.properties.satellite
        item.properties.sensor = item.properties.satellite

        near_incidence_angle = metadata["metadata"].get("", {}).get("MBI_Near_Incidence_Angle", None)
        far_incidence_angle = metadata["metadata"].get("", {}).get("MBI_Far_Incidence_Angle", None)
        if near_incidence_angle and far_incidence_angle:
            item.properties.view__incidence_angle = (float(near_incidence_angle) + float(far_incidence_angle)) / 2

        item.properties.acq__acquisition_orbit_direction = metadata["metadata"].get("", {}).get("Orbit_Direction", None)
        item.properties.acq__acquisition_orbit = metadata["metadata"].get("", {}).get("Orbit_Number", None)

        return item

    def __check_path__(self, path: str) -> bool:
        self.__init__()
        if AccessManager.is_dir(path):

            dir_content = AccessManager.listdir(path)
            # Identify data file
            for f in dir_content:
                # If the CSK archive is tif based
                if f.name.lower().endswith(".tif") and f.name.lower().find(".qlk.") < 0:
                    self.data_path = f.path
                    self.data_format = AssetFormat.geotiff
                # If the CSK archive is h5 based
                if f.name.endswith(".h5"):
                    self.data_path = f.path
                    self.data_format = AssetFormat.h5

            if not self.data_path:
                return False

            tfw_path = os.path.basename(self.data_path).lower().removesuffix(".tif") + ".tfw"
            data_file_prefix = os.path.basename(self.data_path).lower().split(".")[0]
            for f in dir_content:
                if f.name.lower().startswith(data_file_prefix):
                    if f.name.lower().endswith(".qlk.tif"):
                        self.browse_path = f.path
                    if f.name.lower().endswith(".attribs.xml"):
                        self.attr_path = f.path
                    if f.name.lower() == tfw_path.lower():
                        self.tfw_path = f.path
                h5_prefix_file = "dfdn_" + data_file_prefix
                if f.name.lower().startswith(h5_prefix_file):
                    if f.name.lower().endswith(".h5.xml"):
                        self.h5met_path = f.path
                    if f.name.lower().endswith(".h5.pdf"):
                        self.h5pdf_path = f.path

            return (
                self.data_path is not None
                and self.data_format is not None
                and self.h5met_path is not None
            )
        return False

    def __get_proj__(self, metadata: object, centroid: tuple[float, float]):
        if self.data_path and self.data_format == AssetFormat.geotiff:
            return get_epsg(AccessManager.get_gdal_proj(self.data_path))
        else:
            try:
                from pyproj import CRS

                proj_id: str = metadata["metadata"]["Projection_ID"]
                proj_zone = int(metadata["metadata"]["Map_Projection_Zone"])
                is_south = centroid[1] < 0

                crs = CRS.from_dict({'proj': proj_id.lower(), 'zone': proj_zone, 'south': is_south})
                return int(crs.to_authority()[1])
            except Exception:
                return None

    def __get_geometries__(self, metadata: dict):
        return get_geom_bbox_centroid_from_corners(*self.__get_corners__(metadata))

    def __get_corners__(self, metadata: dict) -> tuple[float, float, float, float, float, float, float, float]:
        coords = metadata.get("wgs84Extent", {}).get("coordinates", None)
        if coords:
            return (coords[0][0][0], coords[0][0][1], coords[0][1][0], coords[0][1][1], coords[0][2][0], coords[0][2][1], coords[0][3][0], coords[0][3][1])

        ul = get_value_by_prefix_suffix_or_none(metadata["metadata"][""], ["MBI", "IMG"], "Top_Left_Geodetic_Coordinates")
        ur = get_value_by_prefix_suffix_or_none(metadata["metadata"][""], ["MBI", "IMG"], "Top_Right_Geodetic_Coordinates")
        lr = get_value_by_prefix_suffix_or_none(metadata["metadata"][""], ["MBI", "IMG"], "Bottom_Right_Geodetic_Coordinates")
        ll = get_value_by_prefix_suffix_or_none(metadata["metadata"][""], ["MBI", "IMG"], "Bottom_Left_Geodetic_Coordinates")
        if (ul is None or ur is None or lr is None or ll is None) and metadata["metadata"].get("SUBDATASETS") is not None:
            # Not all products have those coordinates in this format
            # Some have their measures split up in multiple scenes

            # 2 datasets per scene, with each a name and description
            last_scene = int(len(metadata["metadata"]["SUBDATASETS"]) / 4)
            ul = get_value_by_prefix_suffix_or_none(metadata["metadata"][""], ["S01_SBI"], "Top_Left_Geodetic_Coordinates")
            ur = get_value_by_prefix_suffix_or_none(metadata["metadata"][""], [f"S0{last_scene}_SBI"], "Top_Right_Geodetic_Coordinates")
            lr = get_value_by_prefix_suffix_or_none(metadata["metadata"][""], [f"S0{last_scene}_SBI"], "Bottom_Right_Geodetic_Coordinates")
            ll = get_value_by_prefix_suffix_or_none(metadata["metadata"][""], ["S01_SBI"], "Bottom_Left_Geodetic_Coordinates")

        if ul and ur and lr and ll:
            ul_lat = float(ul.split(" ")[0])
            ul_lon = float(ul.split(" ")[1])
            ur_lat = float(ur.split(" ")[0])
            ur_lon = float(ur.split(" ")[1])
            lr_lat = float(lr.split(" ")[0])
            lr_lon = float(lr.split(" ")[1])
            ll_lat = float(ll.split(" ")[0])
            ll_lon = float(ll.split(" ")[1])
            return (ul_lon, ul_lat, ur_lon, ur_lat, lr_lon, lr_lat, ll_lon, ll_lat)
        else:
            raise DriverException("Geodetic Coordinates not found in the metadata")
