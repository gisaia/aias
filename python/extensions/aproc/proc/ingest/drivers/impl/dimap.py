import xml.etree.ElementTree as ET
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    downsample_image, find_or_none, geotiff_to_jpg, get_epsg,
    get_geom_bbox_centroid_from_coordinates, setup_gdal)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver
from airs.core.models.model import SensorType


class Driver(IngestDriver):

    configuration: dict = {}

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
        Driver.configuration = configuration or {}

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        ImageDriverHelper.add_archive(assets, url)

        if self.thumbnail_path is not None:
            assets.append(Asset(href=self.thumbnail_path,
                                roles=[Role.thumbnail.value], name=Role.thumbnail.value, type=MimeType.JPG.value,
                                description=Role.thumbnail.value, size=AccessManager.get_size(self.thumbnail_path), asset_format=AssetFormat.jpg.value))

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
                mime = MimeType.JPEG2000
            if self.image_path.lower().endswith("tif") or self.image_path.lower().endswith("tiff"):
                asset_format = AssetFormat.geotiff.value
                mime = MimeType.TIFF
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
        if self.quicklook_path:
            quicklook = ImageDriverHelper.make_local_preview_asset(self, url, self.quicklook_path, MimeType.PNG, AssetFormat.png)
            self.quicklook_path = quicklook.href
            assets.append(quicklook)

        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if self.quicklook_path is None and IngestDriver.must_build_preview(Driver.configuration, self.image_path, local_remote_both="both"):
            quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
            geotiff_to_jpg(self.image_path, Driver.OVERVIEW_FROM_TIFF_PCT, Driver.OVERVIEW_FROM_TIFF_PCT, quicklook.href, stretch=Driver.configuration.get('overview_stretch', False))
            quicklook.size = AccessManager.get_size(quicklook.href)
            self.quicklook_path = quicklook.href
            assets.append(quicklook)

        if self.thumbnail_path is None and self.quicklook_path is not None:
            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.JPG, AssetFormat.jpg)
            downsample_image(self.quicklook_path, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR)
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)
        return assets

    def load_metadata(self, url: str) -> object:
        with AccessManager.make_local(self.dim_path) as local_dim_path:
            tree = ET.parse(local_dim_path)
            root = tree.getroot()

        return root

    def build_core_item(self, url: str, assets: list[Asset], root: ET.Element) -> Item:
        from osgeo import ogr, osr
        from osgeo.osr import OAMS_TRADITIONAL_GIS_ORDER
        setup_gdal()

        coords = []
        # Calculate bbox
        for vertex in root.iter('Vertex'):
            coord = [float(vertex.find('LON').text), float(vertex.find('LAT').text)]
            coords.append(coord)
        coords.append(coords[0])
        geometry, bbox, centroid = get_geom_bbox_centroid_from_coordinates(coords)

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
                        # We suppose that the first word in the srs expression is the EPSG code
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

        # Open the XML dimap file with gdal to retrieve the metadata
        metadata = AccessManager.get_gdal_md(self.dim_path)

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

        constellation = "AIRBUS"
        if "MISSION" in metadata:
            constellation = metadata["MISSION"]
        elif "DATASET_PRODUCER_NAME" in metadata:
            constellation = metadata["DATASET_PRODUCER_NAME"]
        satellite = constellation
        if metadata["MISSION_INDEX"]:
            satellite = satellite + "-" + metadata["MISSION_INDEX"]

        item = Item(
            id="",
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                constellation=constellation,
                satellite=satellite,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.dimap.value,
                sensor_type=SensorType.OPTIC.value,
                main_asset_format=self.get_main_asset_format(root),
                main_asset_name=Role.data.value,
                observation_type=ObservationType.optic.value
            ),
            assets={asset.name: asset for asset in assets}
        )

        return item

    def add_major_metadata(self, url: str, item: Item, root: ET.Element) -> Item:
        # Open the XML dimap file with gdal to retrieve the metadata
        metadata = AccessManager.get_gdal_md(self.dim_path)

        # We calculate the GSD as the mean of GSD_ACROSS_TRACK and  GSD_ALONG_TRACK
        if "GSD_ACROSS_TRACK" in metadata and "GSD_ALONG_TRACK" in metadata:
            item.properties.gsd = (float(metadata["GSD_ACROSS_TRACK"]) + float(metadata["GSD_ALONG_TRACK"])) / 2
        
        item.properties.processing__level = find_or_none(root, "PROCESSING_LEVEL")
        item.properties.proj__epsg = get_epsg(AccessManager.get_gdal_proj(self.dim_path))
        item.properties.secondary_id = root.find("Dataset_Identification/DATASET_NAME").text
        return item

    def add_minor_metadata(self, url: str, item: Item, root: ET.Element) -> Item:
        # Open the XML dimap file with gdal to retrieve the metadata
        metadata = AccessManager.get_gdal_md(self.dim_path)

        # We set the cloud_cover to None to cover the case of SPOT 7 and Pleaide 50cm wich dont have cloud cover info
        if "CLOUDCOVER_CLOUD_NOTATION" in metadata:
            item.properties.eo__cloud_cover = float(metadata["CLOUDCOVER_CLOUD_NOTATION"])
        else:
            for cloud in root.iter('Dataset_Content'):
                item.properties.eo__cloud_cover = find_or_none(cloud, "CLOUD_COVERAGE", lambda x: float(x))

        item.properties.sensor = item.properties.constellation
        item.properties.view__azimuth = find_or_none(root, "AZIMUTH_ANGLE")
        item.properties.view__incidence_angle = find_or_none(root, "INCIDENCE_ANGLE")
        item.properties.view__sun_azimuth = find_or_none(root, "SUN_AZIMUTH")
        item.properties.view__sun_elevation = find_or_none(root, "SUN_ELEVATION")

        # To fit the case of PNEO 30 cm with no instrument metadata
        item.properties.instrument = metadata.get("INSTRUMENT", metadata.get("MISSION", None))
        if item.properties.instrument:
                    item.properties.instrument = item.properties.instrument + "-" + metadata.get("INSTRUMENT_INDEX", metadata.get("MISSION_INDEX", "?"))


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
                if not file.is_dir:
                    if file.name.endswith('.XML') and file.name.startswith('RPC'):
                        self.rpc_file = file.path
                    elif file.name.endswith('.XML') and file.name.startswith('DIM'):
                        self.dim_path = file.path
                    elif file.name.endswith('.JPG') and file.name.startswith('PREVIEW'):
                        raw_all_quick_path = file.path

                    # Data and georef
                    elif file.name.lower().endswith(('.jpg', 'jp2')) and file.name.startswith('IMG_'):
                        self.image_path = file.path
                    elif file.name.lower().endswith('.tfw') and file.name.startswith('IMG_'):
                        self.georef_path = file.path
                    elif file.name.lower().endswith('.j2w') and file.name.startswith('IMG_'):
                        self.georef_path = file.path
                    elif file.name.lower().endswith(('.tiff', '.tif')) and file.name.startswith('IMG_'):
                        self.image_path = file.path

                    elif file.name.endswith('.JPG') and file.name.startswith('ICON'):
                        raw_all_thumb_path = file.path
                    elif file.name.endswith('.JPG') and file.name.startswith('CAT_QL'):
                        cat_all_quick_path = file.path
                    elif file.name.endswith('.JPG') and file.name.startswith('CAT_TB'):
                        cat_all_thumb_path = file.path
            if cat_all_thumb_path is not None:
                self.thumbnail_path = cat_all_thumb_path
            else:
                self.thumbnail_path = raw_all_thumb_path
            if cat_all_quick_path is not None:
                self.quicklook_path = cat_all_quick_path
            else:
                self.quicklook_path = raw_all_quick_path
            return self.roi_path is not None and self.dim_path is not None and self.image_path is not None
        return False

    @staticmethod
    def get_main_asset_format(root):
        file_format = root.find('./Raster_Data/Data_Access/DATA_FILE_FORMAT').text
        if file_format == "image/jp2":
            main_asset_format = AssetFormat.jpg2000.value
        else:
            main_asset_format = AssetFormat.geotiff.value
        return main_asset_format
