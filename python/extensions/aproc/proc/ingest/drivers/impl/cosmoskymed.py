import os
from typing import Literal
import xml.etree.ElementTree as ET
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    downsample_image, geotiff_to_jpg, get_epsg, get_geom_bbox_centroid)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):
    output_folder: str | None = None  # todo: this should use self.get_asset_filepath instead

    def __init__(self):
        super().__init__()
        self.data_path = None
        self.data_format: Literal[AssetFormat.geotiff] | Literal[AssetFormat.h5] = None

        self.tfw_path = None
        self.met_path = None
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
        Driver.output_folder = configuration['tmp_directory']

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []

        assets.append(Asset(href=self.data_path, size=AccessManager.get_size(self.data_path),
                            roles=[Role.data.value], name=Role.data.value, type=MimeType.TIFF.value if self.data_format == AssetFormat.geotiff else MimeType.HDF5.value,
                            description=Role.data.value, airs__managed=False, asset_format=self.data_format, asset_type=ResourceType.gridded.value))
        assets.append(Asset(href=self.h5met_path, size=AccessManager.get_size(self.h5met_path),
                            roles=[Role.metadata.value], name="h5", type=MimeType.XML.value,
                            description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.xml.value, asset_type=ResourceType.other.value))

        if self.met_path:
            assets.append(Asset(href=self.met_path, size=AccessManager.get_size(self.met_path),
                                roles=[Role.metadata.value], name=Role.metadata.value, type=MimeType.XML.value,
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
        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if self.browse_path is not None:
            self.__prepare_thumbnail__(url)
            geotiff_to_jpg(self.browse_path, 50, 50, self.thumbnail_path)

            self.__prepare_quicklook__(url)
            geotiff_to_jpg(self.browse_path, 250, 250, self.quicklook_path)
        elif self.data_format == AssetFormat.h5:
            import h5py
            import numpy as np
            from PIL import Image

            self.__prepare_quicklook__(url)

            with AccessManager.stream(self.data_path) as f:
                with h5py.File(f) as h5f:
                    max_height = -np.inf
                    values = []

                    # Find QLK in HDF5 file
                    for v in h5f.values():
                        data: np.ndarray = v['QLK'][()]
                        max_height = max(max_height, data.shape[0])
                        values.append(data)

                    for idx, data in enumerate(values):
                        if data.shape[0] < max_height:
                            values[idx] = np.pad(data, pad_width=(max_height - data.shape[0], 0), mode='edge')

                    img = Image.fromarray(np.concatenate(values, axis=1))
                    img.save(self.quicklook_path)

            # Downsample quicklook for thumbnail
            self.__prepare_thumbnail__(url)
            downsample_image(self.quicklook_path, self.thumbnail_path, 8)
        else:
            return assets

        # Register assets
        ImageDriverHelper.add_asset(assets, self.quicklook_path, Role.overview, MimeType.JPG, AssetFormat.jpg, ResourceType.other, airs__managed=True)
        ImageDriverHelper.add_asset(assets, self.thumbnail_path, Role.thumbnail, MimeType.JPG, AssetFormat.jpg, ResourceType.other, airs__managed=True)

        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        from osgeo import gdal

        options = gdal.InfoOptions(format="json")
        info = AccessManager.get_gdal_info(self.data_path, options)
        metadata = info["metadata"][""]

        geometry, bbox, centroid = self.__get_geometries__(info)

        try:
            near_incidence_angle = float(metadata["MBI_Near_Incidence_Angle"])
            far_incidence_angle = float(metadata["MBI_Far_Incidence_Angle"])
            view__incidence_angle = (near_incidence_angle + far_incidence_angle) / 2
        except Exception:
            near_incidence_angle = None
            far_incidence_angle = None
            view__incidence_angle = None

        gsd = float(metadata["Ground_Range_Geometric_Resolution"])
        instrument = metadata["Satellite_ID"]
        sensor = instrument

        date_time = int(datetime.strptime(metadata["Scene_Sensing_Start_UTC"][:-3], "%Y-%m-%d %H:%M:%S.%f").timestamp())

        orbit_direction = metadata["Orbit_Direction"]
        orbit_number = metadata["Orbit_Number"]

        with AccessManager.make_local(self.h5met_path) as local_h5met_path:
            h5_tree = ET.parse(local_h5met_path)
            h5_root = h5_tree.getroot()
        processing__level = h5_root.find("ProcessingInfo/ProcessingLevel").text

        item = Item(
            id=self.get_item_id(url),
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                processing__level=processing__level,
                gsd=gsd,
                proj__epsg=self.__get_proj__(metadata, centroid),
                instrument=instrument,
                constellation="COSMO-SkyMed",
                sensor=sensor,
                sensor_type=SensorType.SAR,
                view__incidence_angle=view__incidence_angle,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.csk.value,
                main_asset_format=self.data_format.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.radar.value,
                acq__acquisition_orbit_direction=orbit_direction,
                acq__acquisition_orbit=orbit_number
            ),
            assets=dict(map(lambda asset: (asset.name, asset), assets))
        )

        return item

    def __check_path__(self, file_path: str):
        self.__init__()
        file_name = os.path.basename(file_path)
        path = AccessManager.dirname(file_path)

        if AccessManager.is_file(file_path):
            condition = True

            met_path = file_path + '.aux.xml'
            if AccessManager.is_file(met_path):
                self.met_path = met_path

            # If the CSK archive is tif based
            if file_name.endswith(".tif") and file_name.find(".QLK.") < 0:
                self.data_path = file_path
                self.data_format = AssetFormat.geotiff

                browse_path = path + '/' + file_name.split(".")[0] + "." + file_name.split(".")[1] + '.QLK.tif'
                if AccessManager.is_file(browse_path):
                    self.browse_path = browse_path

                attr_path = path + '/' + file_name.split(".")[0] + ".attribs.xml"
                if AccessManager.is_file(attr_path):
                    self.attr_path = attr_path

                tfw_path = os.path.splitext(self.data_path)[0] + ".tfw"
                if AccessManager.exists(tfw_path):
                    self.tfw_path = tfw_path

                condition = (
                    self.attr_path is not None
                    and self.browse_path is not None
                    and self.met_path is not None
                )
            # If the CSK archive is h5 based
            elif file_name.endswith(".h5"):
                self.data_path = file_path
                self.data_format = AssetFormat.h5
            else:
                return False

            h5met_path = path + '/' + "DFDN_" + file_name.split(".")[0] + ".h5.xml"
            if AccessManager.is_file(h5met_path):
                self.h5met_path = h5met_path

            h5pdf_path = path + '/' + "DFDN_" + file_name.split(".")[0] + ".h5.pdf"
            if AccessManager.is_file(h5pdf_path):
                self.h5pdf_path = h5pdf_path

            return (
                condition
                and self.data_path is not None
                and self.data_format is not None
                and self.h5met_path is not None
            )
        return False

    def __get_proj__(self, metadata: object, centroid: tuple[float, float]):
        if self.data_format == AssetFormat.geotiff:
            return get_epsg(AccessManager.get_gdal_proj(self.data_path))
        else:
            try:
                from pyproj import CRS

                proj_id: str = metadata["Projection_ID"]
                proj_zone = int(metadata["Map_Projection_Zone"])
                is_south = centroid[1] < 0

                crs = CRS.from_dict({'proj': proj_id.lower(), 'zone': proj_zone, 'south': is_south})
                return int(crs.to_authority()[1])
            except Exception:
                return None

    def __get_geometries__(self, gdal_info_json: object):
        metadata = gdal_info_json["metadata"][""]
        try:
            ul_lat = float(metadata["MBI_Top_Left_Geodetic_Coordinates"].split(" ")[0])
            ul_lon = float(metadata["MBI_Top_Left_Geodetic_Coordinates"].split(" ")[1])
            ur_lat = float(metadata["MBI_Top_Right_Geodetic_Coordinates"].split(" ")[0])
            ur_lon = float(metadata["MBI_Top_Right_Geodetic_Coordinates"].split(" ")[1])
            lr_lat = float(metadata["MBI_Bottom_Right_Geodetic_Coordinates"].split(" ")[0])
            lr_lon = float(metadata["MBI_Bottom_Right_Geodetic_Coordinates"].split(" ")[1])
            ll_lat = float(metadata["MBI_Bottom_Left_Geodetic_Coordinates"].split(" ")[0])
            ll_lon = float(metadata["MBI_Bottom_Left_Geodetic_Coordinates"].split(" ")[1])
        except Exception:
            # Not all products have those coordinates in this format
            # Some have their measures split up in multiple scenes

            # 2 datasets per scene, with each a name and description
            last_scene = int(len(gdal_info_json["metadata"]["SUBDATASETS"]) / 4)

            # Top left and bottom left of first scene
            ul_lat = float(metadata["S01_SBI_Top_Left_Geodetic_Coordinates"].split(" ")[0])
            ul_lon = float(metadata["S01_SBI_Top_Left_Geodetic_Coordinates"].split(" ")[1])
            ll_lat = float(metadata["S01_SBI_Bottom_Left_Geodetic_Coordinates"].split(" ")[0])
            ll_lon = float(metadata["S01_SBI_Bottom_Left_Geodetic_Coordinates"].split(" ")[1])
            # Top right and bottom right of last scene
            ur_lat = float(metadata[f"S0{last_scene}_SBI_Top_Right_Geodetic_Coordinates"].split(" ")[0])
            ur_lon = float(metadata[f"S0{last_scene}_SBI_Top_Right_Geodetic_Coordinates"].split(" ")[1])
            lr_lat = float(metadata[f"S0{last_scene}_SBI_Bottom_Right_Geodetic_Coordinates"].split(" ")[0])
            lr_lon = float(metadata[f"S0{last_scene}_SBI_Bottom_Right_Geodetic_Coordinates"].split(" ")[1])

        return get_geom_bbox_centroid(ul_lon, ul_lat, ur_lon, ur_lat, lr_lon, lr_lat, ll_lon, ll_lat)

    def __prepare_quicklook__(self, url: str):
        quicklook_path = Driver.output_folder + '/' + self.get_item_id(url) + '/quicklook'
        AccessManager.makedir(quicklook_path)
        self.quicklook_path = quicklook_path + '/quicklook.jpg'

    def __prepare_thumbnail__(self, url: str):
        thumbnail_path = Driver.output_folder + '/' + self.get_item_id(url) + '/thumbnail'
        AccessManager.makedir(thumbnail_path)
        self.thumbnail_path = thumbnail_path + '/thumbnail.jpg'
