import json
import os

import dateutil.parser
from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Band, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role)
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.ingest.drivers.impl.utils import compute_simplified_polygon
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver
from aproc.core.logger import Logger

LOGGER = Logger.logger

class ImageDriverHelper:
    @staticmethod
    def identify_assets(driver: IngestDriver, type: MimeType, format: AssetFormat, url: str) -> list[Asset]:
        assets = []
        assets.append(Asset(href=url, size=AccessManager.get_size(url),
                      roles=[Role.data.value], name=Role.data.value, type=type.value,
                      description=Role.data.value, airs__managed=False, asset_format=format.value, asset_type=ResourceType.gridded.value))

        assets.append(Asset(href=url,
                            roles=[Role.archive.value], name=Role.archive.value, type=type.value,
                            description=Role.archive.value, airs__managed=False, asset_format=format.value))

        tfw_path = os.path.splitext(url)[0] + ".tfw"
        if AccessManager.exists(tfw_path):
            assets.append(Asset(href=tfw_path, size=AccessManager.get_size(tfw_path),
                                roles=[Role.extent.value], name=Role.extent.value, type=MimeType.TEXT.value,
                                description=Role.extent.value, airs__managed=False, asset_format=AssetFormat.tfw.value, asset_type=ResourceType.other.value))

        j2w_path = os.path.splitext(url)[0] + ".j2w"
        if AccessManager.exists(j2w_path):
            assets.append(Asset(href=j2w_path, size=AccessManager.get_size(j2w_path),
                                roles=[Role.extent.value], name=Role.extent.value, type=MimeType.TEXT.value,
                                description=Role.extent.value, airs__managed=False, asset_format=AssetFormat.j2w.value, asset_type=ResourceType.other.value))
        return assets

    @staticmethod
    def add_asset(assets: list[Asset], href: str, role: Role, type: MimeType, asset_format: AssetFormat, asset_type: ResourceType, airs__managed=False):
        asset = Asset(href=href, size=AccessManager.get_size(href),
                            roles=[role.value], name=role.value, type=type.value,
                            description=role.value, airs__managed=airs__managed, asset_format=asset_format.value, asset_type=asset_type.value)
        assets.append(asset)
        return asset

    @staticmethod
    def add_archive(assets: list[Asset], href: str):
        assets.append(Asset(href=href, roles=[Role.archive.value], name=Role.archive.value, asset_format=AssetFormat.directory.value,
                            type=MimeType.DIRECTORY.value, description=Role.archive.value, airs__managed=False))

    @staticmethod
    def prepare_preview_asset(driver: IngestDriver, href: str, role: Role, type: MimeType, format: AssetFormat):
        preview = Asset(href=None, name=role.value, description=role.value, roles=[role.value],
                        type=type.value, asset_format=format.value, asset_type=ResourceType.other.value, airs__managed=True)
        preview.href = driver.get_asset_filepath(href, preview) + '.' + format.value.lower()

        return preview

    @staticmethod
    def make_local_overview_asset(driver: IngestDriver, archive_href: str, overview_href: str, type: MimeType, format: AssetFormat) -> Asset:
        overview = ImageDriverHelper.prepare_preview_asset(driver, archive_href, Role.overview, type, format)
        if not AccessManager.is_local(overview_href):
            AccessManager.pull(overview_href, overview.href)
        else:
            overview.href = overview_href
        overview.size = AccessManager.get_size(overview.href)

        return overview

    @staticmethod
    def load_metadata(driver: IngestDriver, url: str) -> object:
        from osgeo import gdal

        gdal_options = gdal.InfoOptions(format='json')
        try:
            gdal_info = AccessManager.get_gdal_info(url, gdal_options)
        except Exception as e:
            raise DriverException("Can not read image metadata from {}: {}".format(url, e))

        return gdal_info

    @staticmethod
    def gdal_geometry(driver: IngestDriver, url: str) -> object:
        from osgeo import gdal
        options = gdal.InfoOptions(format="json")
        gdal_info = AccessManager.get_gdal_info(url, options)
        geometry = gdal_info.get("wgs84Extent", None)
        gcps = gdal_info.get("gcps", {}).get("gcpList", [])
        if geometry is None:
            if gcps:
                LOGGER.debug("No geometry found for {}, trying to compute it from gcps".format(url))
                geometry = {
                    "type": "Polygon",
                    "coordinates": [compute_simplified_polygon(gcps)]
                }
            else:
                LOGGER.warning("No geometry found for {} and no gcps to compute it from".format(url))
        return geometry

    @staticmethod
    def build_core_item(driver: IngestDriver, url: str, item_format: ItemFormat, asset_format: AssetFormat, assets: list[Asset], metadata: object) -> Item:
        import rasterio
        import rasterio.features
        import rasterio.warp
        from shapely import centroid, geometry, is_valid, ops, to_geojson

        bands = []
        geoms = []

        metadata_keys = list(metadata.get("metadata", {}))
        if metadata_keys:
            description = metadata.get("metadata", {}).get(metadata_keys[0], {}).get("title", "Image file")
            try:
                creation_time = dateutil.parser.parse(metadata.get("metadata", {}).get(metadata_keys[0], {}).get("creation_time", ""))
            except dateutil.parser.ParserError:
                creation_time = None
        else:
            description = "Image file"
            creation_time = None

        with rasterio.Env(**AccessManager.get_rasterio_session(url)):
            with rasterio.open(url) as dataset:
                nodata_geoms = []
                for v in zip(dataset.indexes, dataset.descriptions):
                    bands.append(Band(name="Band " + str(v[0]), eo__common_name="Band " + str(v[0]), description=v[1] if v[1] else "Band " + str(v[0])))
                # GET THE GEO EXTENT
                # Read the dataset's valid data mask as a ndarray.
                mask = dataset.dataset_mask()
                nodata = dataset.nodata
                # Extract feature shapes and values from the array.
                try:
                    proj__epsg = dataset.crs.to_epsg()
                    for geom, value in rasterio.features.shapes(
                            mask, transform=dataset.transform):
                        geom = rasterio.warp.transform_geom(
                            dataset.crs, 'EPSG:4326', geom, precision=6)
                        shapely_geom = geometry.shape(geom)

                        if is_valid(shapely_geom):
                            # Only consider the valid geometries that don't represent the nodata
                            if value != nodata:
                                geoms.append(shapely_geom)
                            else:
                            # fallback if no geometry found
                                nodata_geoms.append(shapely_geom)

                except rasterio.errors.CRSError as e:
                    # It is mandatory to get a crs to get the geometry of the extent
                    raise DriverException("Invalid CRS for {}: {}".format(url, e))
                if len(geoms) == 0 and len(nodata_geoms) > 0:
                    geoms = nodata_geoms
                geom = ops.unary_union(geoms)
                a, b, c, d = geom.bounds
                bbox = [a, b, c, d]
                c = centroid(geom)

        item = Item(
            geometry=json.loads(to_geojson(geom)),
            bbox=bbox,
            centroid=[c.x, c.y],
            properties=Properties(
                proj__epsg=proj__epsg,
                constellation="Unknown",
                item_type=ResourceType.gridded.value,
                item_format=item_format.value,
                main_asset_format=asset_format,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.other,
                description=description,
                eo__bands=bands
            ),
            assets={asset.name: asset for asset in assets}
        )

        if creation_time:
            item.properties.datetime = creation_time.timestamp()
        else:
            item.properties.datetime = AccessManager.get_creation_time(url)

        return item

