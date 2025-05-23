import os
import xml.etree.ElementTree as ET
from datetime import datetime

from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role)
from aias_common.access.manager import AccessManager
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    get_epsg, get_geom_bbox_centroid, get_hash_url, setup_gdal)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):

    def __init__(self):
        super().__init__()
        self.quicklook_path = None
        self.thumbnail_path = None
        self.dim_path = None
        self.roi_path = None
        self.image_path = None
        self.georef_path = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)

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
        if self.thumbnail_path is not None:
            assets.append(Asset(href=self.thumbnail_path,
                                roles=[Role.thumbnail.value], name=Role.thumbnail.value, type=MimeType.JPG.value,
                                description=Role.thumbnail.value, size=AccessManager.get_size(self.thumbnail_path), asset_format=AssetFormat.jpg.value))
        if self.quicklook_path is not None:
            assets.append(Asset(href=self.quicklook_path,
                                roles=[Role.overview.value], name=Role.overview.value, type=MimeType.JPG.value,
                                description=Role.overview.value, size=AccessManager.get_size(self.quicklook_path), asset_format=AssetFormat.jpg.value))
        assets.append(Asset(href=self.dim_path, size=AccessManager.get_size(self.dim_path),
                            roles=[Role.metadata.value], name=Role.metadata.value, type=MimeType.XML.value,
                            description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.xml.value))
        assets.append(Asset(href=self.roi_path, size=AccessManager.get_size(self.roi_path),
                            roles=[Role.data_mask.value], name=Role.data_mask.value, type=MimeType.GML.value,
                            description=Role.data_mask.value, airs__managed=False, asset_format=AssetFormat.gml.value))

        if self.image_path:
            asset_format = AssetFormat.other.value
            mime = None
            if self.image_path.lower().endswith("jp2"):
                asset_format = AssetFormat.jpg2000.value
                mime = "image/jp2"
            if self.image_path.lower().endswith("tif") or self.image_path.lower().endswith("tiff"):
                asset_format = AssetFormat.geotiff.value
                mime = "image/tif"
            assets.append(Asset(href=self.image_path, size=AccessManager.get_size(self.image_path),
                                roles=[Role.data.value], name=Role.data.value, type=mime,
                                description=Role.data.value, airs__managed=False, asset_format=asset_format))

        if self.georef_path:
            asset_format = AssetFormat.other.value
            if self.georef_path.lower().endswith("j2w"):
                asset_format = AssetFormat.j2w.value
            if self.georef_path.lower().endswith("tfw"):
                asset_format = AssetFormat.tfw.value
            assets.append(Asset(href=self.georef_path, size=AccessManager.get_size(self.georef_path),
                                roles=[Role.extent.value], name=Role.extent.value, type=MimeType.TEXT.value,
                                description=Role.extent.value, airs__managed=False, asset_format=asset_format, asset_type=ResourceType.other.value))
        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def get_item_id(self, url: str) -> str:
        return get_hash_url(url)

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        from osgeo import gdal, ogr, osr
        from osgeo.gdalconst import GA_ReadOnly
        from osgeo.osr import OAMS_TRADITIONAL_GIS_ORDER
        setup_gdal()

        # Open ROI GML file to find the real footprint of the product
        with AccessManager.make_local(self.roi_path) as local_roi_path:
            ogr_d = ogr.GetDriverByName("GML")
            component_source = ogr_d.Open(local_roi_path, 0)  # read-only
            layer = component_source.GetLayer()
            component_feature = layer.GetNextFeature()
            geo_ref = component_feature.GetGeometryRef()
            in_spatial_ref_code = None
            if geo_ref is not None and geo_ref.GetSpatialReference() is not None:
                if geo_ref.GetSpatialReference().GetAuthorityCode("PROJCS") is not None:
                    in_spatial_ref_code = geo_ref.GetSpatialReference().GetAuthorityCode("PROJCS")
                elif geo_ref.GetSpatialReference().GetAuthorityCode("GEOGCS") is not None:
                    in_spatial_ref_code = geo_ref.GetSpatialReference().GetAuthorityCode("GEOGCS")
            else:
                # Find epsg in reading directly the GML File
                tree_gml = ET.parse(local_roi_path)
                root_gml = tree_gml.getroot()
                for srs in root_gml.iter():
                    if len(srs.items()) > 0 and srs.items()[0][0] == "srsName":
                        # We suppose to the first word in the srs expression is the EPSG code
                        # Because the string in the GML is not a classic SRS expression
                        in_spatial_ref_code = srs.items()[0][1].split(" ")[0]
                        break

        component_geometry = component_feature.geometry()
        # output SpatialReference
        if in_spatial_ref_code is not None and in_spatial_ref_code.isdigit() and int(in_spatial_ref_code) != 4326:
            out_spatial_ref = osr.SpatialReference()
            out_spatial_ref.ImportFromEPSG(4326)
            in_spatial_ref = osr.SpatialReference()
            in_spatial_ref.ImportFromEPSG(int(in_spatial_ref_code))
            in_spatial_ref.SetAxisMappingStrategy(OAMS_TRADITIONAL_GIS_ORDER)
            # create the CoordinateTransformation
            coord_transform = osr.CoordinateTransformation(in_spatial_ref, out_spatial_ref)
            component_geometry.Transform(coord_transform)
            # Retrieve geometry and centroid
            geometry = component_feature.ExportToJson(as_object=True)["geometry"]
            centroid_geom = component_geometry.Centroid()
            centroid_geom_list = str(centroid_geom).replace("(", "").replace(")", "").split(" ")
            centroid = [float(centroid_geom_list[2]), float(centroid_geom_list[1])]

        with AccessManager.make_local(self.dim_path) as local_dim_path:
            tree = ET.parse(local_dim_path)
            root = tree.getroot()

            coords = []
            # Calculate bbox
            for vertex in root.iter('Vertex'):
                coord = [float(vertex.find('LON').text), float(vertex.find('LAT').text)]
                coords.append(coord)
            geometry, bbox, centroid = get_geom_bbox_centroid(coords[0][0], coords[0][1], coords[1][0], coords[1][1],
                                                              coords[2][0], coords[2][1], coords[3][0], coords[3][1])

            # If we get the archive NOT locally, then we need to retrieve the files referenced and put them in the right spot
            # In order for GDAL to be able to properly open the dim file
            files_to_make_local = []
            desired_local_path = []

            storage = AccessManager.resolve_storage(self.dim_path)
            if not storage.get_configuration().is_local:
                def list_needed_files(node: str):
                    for vertex in root.iter(node):
                        path = vertex.attrib["href"]

                        dst = os.path.join(AccessManager.tmp_dir, path)
                        # Makedir to prepare for AccessManager.make_local
                        os.makedirs(os.path.dirname(dst), exist_ok=True)

                        files_to_make_local.append(os.path.join(AccessManager.dirname(self.dim_path), path))
                        desired_local_path.append(dst)

                list_needed_files("COMPONENT_PATH")
                list_needed_files("DATASET_TN_PATH")
                list_needed_files("DATASET_QL_PATH")
                list_needed_files("DATA_FILE_PATH")

            # Open the XML dimap file with gdal to retrieve the metadata
            with AccessManager.make_local_list(files_to_make_local, desired_local_path):
                src_ds = gdal.Open(local_dim_path, GA_ReadOnly)
                metadata = src_ds.GetMetadata()
        # We retrieve the time
        if "IMAGING_DATE" in metadata and "IMAGING_TIME" in metadata:
            date = metadata["IMAGING_DATE"]
            time = metadata["IMAGING_TIME"]
            if "Z" in time:
                date_time = int(datetime.strptime(date + time, "%Y-%m-%d%H:%M:%S.%fZ").timestamp())
            elif "." in time:
                date_time = int(datetime.strptime(date + time, "%Y-%m-%d%H:%M:%S.%f").timestamp())
            else:
                date_time = int(datetime.strptime(date + time, "%Y-%m-%d%H:%M:%S").timestamp())
        else:
            # Take the date of the  center of the image
            for lgv in root.iter('Located_Geometric_Values'):
                if lgv.find('LOCATION_TYPE').text == "Center":
                    date_time = int(datetime.strptime(lgv.find('TIME').text, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())
        # We set the cloud_cover to None to cover the case of SPOT 7 and Pleaide 50cm wich dont have cloud cover info
        cloud_cover = None
        if "CLOUDCOVER_CLOUD_NOTATION" in metadata:
            cloud_cover = float(metadata["CLOUDCOVER_CLOUD_NOTATION"])
        else:
            for cloud in root.iter('Dataset_Content'):
                if cloud.find("CLOUD_COVERAGE") is not None:
                    cloud_cover = float(cloud.find("CLOUD_COVERAGE").text)

        # We calculate the GSD as the mean of  GSD_ACROSS_TRACK and  GSD_ALONG_TRACK
        if metadata.get("GSD_ACROSS_TRACK") and metadata.get("GSD_ALONG_TRACK"):
            gsd = (float(metadata["GSD_ACROSS_TRACK"]) + float(metadata["GSD_ALONG_TRACK"])) / 2
        else:
            gsd = None
        item = Item(
            id=self.get_item_id(url),
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                processing__level=metadata.get("PROCESSING_LEVEL"),
                eo__cloud_cover=cloud_cover,
                gsd=gsd,
                proj__epsg=get_epsg(src_ds),
                view__incidence_angle=metadata.get("INCIDENCE_ANGLE"),
                view__azimuth=metadata.get("AZIMUTH_ANGLE"),
                view__sun_azimuth=metadata.get("SUN_AZIMUTH"),
                view__sun_elevation=metadata.get("SUN_ELEVATION"),
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.dimap.value,
                main_asset_format=self.get_main_asset_format(root),
                main_asset_name=Role.data.value,
                observation_type=ObservationType.image.value
            ),
            assets=dict(map(lambda asset: (asset.name, asset), assets))
        )
        # To fit the case of PNEO 30 cm with no instrument metadata
        if "INSTRUMENT" in metadata:
            item.properties.instrument = metadata["INSTRUMENT"]
        if "MISSION" in metadata:
            item.properties.constellation = metadata["MISSION"]
            item.properties.sensor = metadata["MISSION"]
        elif "DATASET_PRODUCER_NAME" in metadata:
            item.properties.constellation = metadata["DATASET_PRODUCER_NAME"]
            item.properties.sensor = metadata["DATASET_PRODUCER_NAME"]
        if "MISSION_INDEX" in metadata:
            item.properties.sensor_type = metadata["MISSION_INDEX"]

        return item

    def __check_path__(self, path: str):
        # relative_folder_path variable must be a folder path beginning and finishing with a /
        self.__init__()
        cat_all_thumb_path = None
        cat_all_quick_path = None
        raw_all_thumb_path = None
        raw_all_quick_path = None

        if AccessManager.is_dir(path):
            for file in AccessManager.listdir(path):
                # check if current file is a dir
                if file.name == 'MASKS':
                    for mask in AccessManager.listdir(file.path):
                        if mask.name.endswith('.GML') and mask.name.startswith('ROI'):
                            self.roi_path = mask.path
                # check if current file is a file
                if AccessManager.is_file(file.path):
                    if file.name.endswith('.XML') and file.name.startswith('RPC'):
                        self.rpc_file = file.path
                    if file.name.endswith('.XML') and file.name.startswith('DIM'):
                        self.dim_path = file.path
                    if file.name.endswith('.JPG') and file.name.startswith('PREVIEW'):
                        raw_all_quick_path = file.path

                    # Data and georef
                    if file.name.lower().endswith(('.jpg', 'jp2')) and file.name.startswith('IMG_'):
                        self.image_path = file.path
                    if file.name.lower().endswith('.tfw') and file.name.startswith('IMG_'):
                        self.georef_path = file.path
                    if file.name.lower().endswith('.j2w') and file.name.startswith('IMG_'):
                        self.georef_path = file.path
                    if file.name.lower().endswith(('.tiff', '.tif')) and file.name.startswith('IMG_'):
                        self.image_path = file.path

                    if file.name.endswith('.JPG') and file.name.startswith('ICON'):
                        raw_all_thumb_path = file.path
                    if file.name.endswith('.JPG') and file.name.startswith('CAT_QL'):
                        cat_all_quick_path = file.path
                    if file.name.endswith('.JPG') and file.name.startswith('CAT_TB'):
                        cat_all_thumb_path = file.path
            if cat_all_thumb_path is not None:
                self.thumbnail_path = cat_all_thumb_path
            else:
                self.thumbnail_path = raw_all_thumb_path
            if cat_all_quick_path is not None:
                self.quicklook_path = cat_all_quick_path
            else:
                self.quicklook_path = raw_all_quick_path
            return self.roi_path is not None and self.dim_path is not None
        return False

    @staticmethod
    def get_main_asset_format(root):
        file_format = root.find('./Raster_Data/Data_Access/DATA_FILE_FORMAT').text
        if file_format == "image/jp2":
            main_asset_format = AssetFormat.jpg2000.value
        else:
            main_asset_format = AssetFormat.geotiff.value
        return main_asset_format
