import os
import xml.etree.ElementTree as ET
from datetime import datetime

from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    ObservationType, Properties, ResourceType,
                                    Role)
from aproc.core.settings import Configuration
from extensions.aproc.proc.ingest.drivers.driver import Driver as ProcDriver
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    get_file_size, get_geom_bbox_centroid, setup_gdal, get_hash_url, get_epsg)


class Driver(ProcDriver):
    quicklook_path = None
    thumbnail_path = None
    dim_path = None
    roi_path = None
    image_path = None
    georef_path = None

    # Implements drivers method
    def init(configuration: Configuration):
         return

    # Implements drivers method
    def supports(url: str) -> bool:
        try:
            result = Driver.__check_path__(url)
            return result
        except Exception as e:
            Driver.LOGGER.debug(e)
            return False

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        if self.thumbnail_path is not None:
            assets.append(Asset(href=self.thumbnail_path,
                                roles=[Role.thumbnail.value], name=Role.thumbnail.value, type="image/jpg",
                                description=Role.thumbnail.value, size=get_file_size(self.thumbnail_path), asset_format=AssetFormat.jpg.value))
        if self.quicklook_path is not None:
            assets.append(Asset(href=self.quicklook_path,
                                roles=[Role.overview.value], name=Role.overview.value, type="image/jpg",
                                description=Role.overview.value, size=get_file_size(self.quicklook_path), asset_format=AssetFormat.jpg.value))
        assets.append(Asset(href=self.dim_path, size=get_file_size(self.dim_path),
                            roles=[Role.metadata.value], name=Role.metadata.value, type="text/xml",
                            description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.xml.value))
        assets.append(Asset(href=self.roi_path, size=get_file_size(self.roi_path),
                            roles=[Role.data_mask.value], name=Role.data_mask.value, type="application/gml+xml",
                            description=Role.data_mask.value, airs__managed=False, asset_format=AssetFormat.gml.value))

        if Driver.image_path:
            format = AssetFormat.other.value
            mime = None
            if Driver.image_path.lower().endswith("jp2"):
                format = AssetFormat.jpg2000.value
                mime = "image/jp2"
            if Driver.image_path.lower().endswith("tif") or Driver.image_path.lower().endswith("tiff"):
                format = AssetFormat.geotiff.value
                mime = "image/tif"
            assets.append(Asset(href=self.image_path, size=get_file_size(self.image_path),
                                roles=[Role.data.value], name=Role.data.value, type=mime,
                                description=Role.data.value, airs__managed=False, asset_format=format))

        if Driver.georef_path:
            format = AssetFormat.other.value
            if Driver.georef_path.lower().endswith("j2w"):
                format = AssetFormat.j2w.value
            if Driver.georef_path.lower().endswith("tfw"):
                format = AssetFormat.tfw.value
            assets.append(Asset(href=self.georef_path, size=get_file_size(self.georef_path),
                                roles=[Role.extent.value], name=Role.extent.value, type="text/plain",
                                description=Role.metadata.value, airs__managed=False, asset_format=format, asset_type=ResourceType.other.value))
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
        from osgeo.osr import OAMS_TRADITIONAL_GIS_ORDER
        from osgeo import gdal, ogr, osr
        from osgeo.gdalconst import GA_ReadOnly
        setup_gdal()
        tree = ET.parse(self.dim_path)
        root = tree.getroot()
        coords = []
        # Calculate bbox
        for vertex in root.iter('Vertex'):
            coord = [float(vertex.find('LON').text), float(vertex.find('LAT').text)]
            coords.append(coord)
        geometry, bbox, centroid = get_geom_bbox_centroid(coords[0][0], coords[0][1], coords[1][0], coords[1][1],
                                                          coords[2][0], coords[2][1], coords[3][0], coords[3][1])

        # Open ROI GML file to find the real footprint of the product
        driver = ogr.GetDriverByName("GML")
        component_source = driver.Open(self.roi_path, 0)  # read-only
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
            tree_gml = ET.parse(self.roi_path)
            root_gml = tree_gml.getroot()
            for srs in root_gml.iter():
                if len(srs.items()) > 0:
                    if (srs.items()[0][0] == "srsName"):
                        # We suppose to the first word in the srs expression is the EPSG code
                        # Because the string in the GML is not a classic SRS expression
                        in_spatial_ref_code = srs.items()[0][1].split(" ")[0]
                        break
        component_geometry = component_feature.geometry()
        # output SpatialReference
        if in_spatial_ref_code is not None and in_spatial_ref_code.isdigit() and int(in_spatial_ref_code) != "4326":
            outSpatialRef = osr.SpatialReference()
            outSpatialRef.ImportFromEPSG(4326)
            inSpatialRef = osr.SpatialReference()
            inSpatialRef.ImportFromEPSG(int(in_spatial_ref_code))
            inSpatialRef.SetAxisMappingStrategy(OAMS_TRADITIONAL_GIS_ORDER)
            # create the CoordinateTransformation
            coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
            component_geometry.Transform(coordTrans)
            # Retrieve geometry and centroid
            geometry = component_feature.ExportToJson(as_object=True)["geometry"]
            centroid_geom = component_geometry.Centroid()
            centroid_geom_list = str(centroid_geom).replace("(", "").replace(")", "").split(" ")
            centroid = [float(centroid_geom_list[2]), float(centroid_geom_list[1])]

        # Open the XML dimap file with gdal to retrieve the metadata
        src_ds = gdal.Open(self.dim_path, GA_ReadOnly)
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
        gsd = (float(metadata["GSD_ACROSS_TRACK"]) + float(metadata["GSD_ALONG_TRACK"])) / 2
        item = Item(
            id=self.get_item_id(url),
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                processing__level=metadata["PROCESSING_LEVEL"],
                eo__cloud_cover=cloud_cover,
                gsd=gsd,
                proj__epsg=get_epsg(src_ds),
                view__incidence_angle=metadata["INCIDENCE_ANGLE"],
                view__azimuth=metadata["AZIMUTH_ANGLE"],
                view__sun_azimuth=metadata["SUN_AZIMUTH"],
                view__sun_elevation=metadata["SUN_ELEVATION"],
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.dimap.value,
                main_asset_format=self.get_main_asset_format(root),
                main_asset_name=Role.metadata.value,
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

    def __check_path__(path: str):
        # relative_folder_path variable must be a folder path beginning and finishing with a /
        valid_and_exist = os.path.isdir(path) and os.path.exists(path)
        Driver.thumbnail_path = None
        Driver.quicklook_path = None
        Driver.roi_path = None
        Driver.dim_path = None
        cat_all_thumb_path = None
        cat_all_quick_path = None
        raw_all_thumb_path = None
        raw_all_quick_path = None
        if valid_and_exist is True:
            for file in os.listdir(path):
                # check if current file is a dir
                if os.path.isdir(os.path.join(path, file)):
                    if file == 'MASKS':
                        for mask in os.listdir(os.path.join(path, file)):
                            if mask.endswith('.GML') and mask.startswith('ROI'):
                                Driver.roi_path = os.path.join(os.path.join(path, file), mask)
                # check if current file is a file
                if os.path.isfile(os.path.join(path, file)):
                    if file.endswith('.XML') and file.startswith('RPC'):
                        Driver.rpc_file = os.path.join(path, file)
                    if file.endswith('.XML') and file.startswith('DIM'):
                        Driver.dim_path = os.path.join(path, file)
                    if file.endswith('.JPG') and file.startswith('PREVIEW'):
                        raw_all_quick_path = os.path.join(path, file)
                    if file.lower().endswith('.jpg') and file.startswith('IMG_'):
                        Driver.image_path = os.path.join(path, file)
                    if file.lower().endswith('.tfw') and file.startswith('IMG_'):
                        Driver.georef_path = os.path.join(path, file)
                    if file.lower().endswith('.j2w') and file.startswith('IMG_'):
                        Driver.georef_path = os.path.join(path, file)
                    if (file.lower().endswith('.tiff') or file.lower().endswith('.tif')) and file.startswith('IMG_'):
                        Driver.image_path = os.path.join(path, file)
                    if file.endswith('.JPG') and file.startswith('ICON'):
                        raw_all_thumb_path = os.path.join(path, file)
                    if file.endswith('.JPG') and file.startswith('CAT_QL'):
                        cat_all_quick_path = os.path.join(path, file)
                    if file.endswith('.JPG') and file.startswith('CAT_TB'):
                        cat_all_thumb_path = os.path.join(path, file)
            if cat_all_thumb_path is not None:
                Driver.thumbnail_path = cat_all_thumb_path
            else:
                Driver.thumbnail_path = raw_all_thumb_path
            if cat_all_quick_path is not None:
                Driver.quicklook_path = cat_all_quick_path
            else:
                Driver.quicklook_path = raw_all_quick_path
            return Driver.roi_path is not None and Driver.dim_path is not None
        else:
            Driver.LOGGER.debug("The reference {} is not a folder or does not exist.".format(path))
            return False

    @staticmethod
    def get_main_asset_format(root):
        format = root.find('./Raster_Data/Data_Access/DATA_FILE_FORMAT').text
        if format == "image/jp2":
            main_asset_format = AssetFormat.jpg2000.value
        else:
            main_asset_format = AssetFormat.geotiff.value
        return main_asset_format
