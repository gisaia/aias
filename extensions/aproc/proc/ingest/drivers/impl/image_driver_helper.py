import json
import os

import dateutil.parser

from airs.core.models.model import (Asset, AssetFormat, Band, Item, ItemFormat,
                                    MimeType, Properties, ResourceType, Role)
from extensions.aproc.proc.access.manager import AccessManager
from extensions.aproc.proc.drivers.abstract_driver import AbstractDriver
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.ingest.drivers.impl.utils import get_hash_url
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class ImageDriverHelper:
    @staticmethod
    def identify_assets(driver: IngestDriver, format: str, url: str) -> list[Asset]:
        assets = []
        assets.append(Asset(href=url,
                      roles=[Role.data.value], name=Role.data.value, type=format,
                      description=Role.data.value, airs__managed=False))
        tfw_path = os.path.splitext(url)[0] + ".tfw"
        if AccessManager.exists(tfw_path):
            assets.append(Asset(href=tfw_path, size=AccessManager.get_file_size(tfw_path),
                                roles=[Role.extent.value], name=Role.extent.value, type=MimeType.TEXT.value,
                                description=Role.extent.value, airs__managed=False, asset_format=AssetFormat.tfw.value, asset_type=ResourceType.other.value))

        j2w_path = os.path.splitext(url)[0] + ".j2w"
        if AccessManager.exists(j2w_path):
            assets.append(Asset(href=j2w_path, size=AccessManager.get_file_size(j2w_path),
                                roles=[Role.extent.value], name=Role.extent.value, type=MimeType.TEXT.value,
                                description=Role.extent.value, airs__managed=False, asset_format=AssetFormat.j2w.value, asset_type=ResourceType.other.value))
        return assets

    @staticmethod
    def add_overview_if_you_can(driver: AbstractDriver, url: str, role: Role, size: int, to_assets: list[Asset]) -> Asset:
        driver.LOGGER.debug("Try to create the thumbnail of {}".format(url))
        try:
            from PIL import Image
            Image.MAX_IMAGE_PIXELS = 2000000000
            asset = Asset(href=None,
                          roles=[role.value], name=role.value, type=MimeType.PNG.value,
                          description=role.value, asset_format=AssetFormat.png.value)
            asset.href = driver.get_asset_filepath(url, asset)
            driver.LOGGER.debug("Try to create the thumbnail of {} in {}".format(url, asset.href))
            local_url = AccessManager.prepare(url)
            image = Image.open(local_url)
            image.thumbnail([size, size])
            image.save(asset.href, 'PNG')
            asset.size = AccessManager.get_file_size(asset.href)
            to_assets.append(asset)
            image.close()

            if local_url != url:
                os.remove(local_url)
        except Exception as e:
            driver.LOGGER.warn("Couldn't create the thumbnail of {}".format(url))
            driver.LOGGER.error(e)

    # Implements drivers method
    @staticmethod
    def fetch_assets(driver: IngestDriver, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    @staticmethod
    def get_item_id(driver: IngestDriver, url: str) -> str:
        return get_hash_url(url)

    # Implements drivers method
    @staticmethod
    def transform_assets(driver: IngestDriver, format: str, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    @staticmethod
    def to_item(driver: IngestDriver, item_format: ItemFormat, asset_format: AssetFormat, url: str, assets: list[Asset]) -> Item:
        import rasterio
        import rasterio.features
        import rasterio.warp
        from osgeo import gdal
        from shapely import centroid, geometry, ops, to_geojson

        geoms = []
        bands = []

        gdal_options = gdal.InfoOptions(format='json')
        try:
            local_url = AccessManager.prepare(url)
            gdal_info = gdal.Info(local_url, options=gdal_options)
        except Exception as e:
            raise DriverException("Can not read image metadata from {}: {}".format(url, e))
        metadata_keys = list(gdal_info.get("metadata", {}))
        if metadata_keys:
            description = gdal_info.get("metadata", {}).get(metadata_keys[0], {}).get("title", "Image file")
            try:
                creation_time = dateutil.parser.parse(gdal_info.get("metadata", {}).get(metadata_keys[0], {}).get("creation_time", ""))
            except dateutil.parser.ParserError:
                creation_time = None
        else:
            description = "Image file"
            creation_time = None

        with rasterio.open(local_url) as dataset:
            for v in zip(dataset.indexes, dataset.descriptions):
                bands.append(Band(name="Band " + str(v[0]), common_name="Band " + str(v[0]), description=v[1] if v[1] else "Band " + str(v[0])))
            # GET THE GEO EXTENT
            # Read the dataset's valid data mask as a ndarray.
            mask = dataset.dataset_mask()
            # Extract feature shapes and values from the array.
            try:
                crs = dataset.crs
                for geom, val in rasterio.features.shapes(
                        mask, transform=dataset.transform):
                    geom = rasterio.warp.transform_geom(
                        dataset.crs, 'EPSG:4326', geom, precision=6)
                    geoms.append(geometry.shape(geom))
            except rasterio.errors.CRSError as e:
                # It is mandatory to get a crs to get the geometry of the extent
                raise DriverException("Invalid CRS for {}: {}".format(url, e))
            geom = ops.unary_union(geoms)
            a, b, c, d = geom.bounds
            bbox = [a, b, c, d]
            c = centroid(geom)

        date_time = AccessManager.get_creation_time(url)
        item = Item(
            id=driver.get_item_id(url),
            geometry=json.loads(to_geojson(geom)),
            bbox=bbox,
            centroid=[c.x, c.y],
            properties=Properties(
                datetime=creation_time.timestamp() if creation_time else date_time,
                proj__epsg=crs.to_epsg(),
                item_type=ResourceType.gridded.value,
                item_format=item_format.value,
                main_asset_format=driver.get_main_asset_format(url),
                main_asset_name=Role.data.value,
                description=description
            ),
            assets=dict(map(lambda asset: (asset.name, asset), assets))
        )
        item.properties.instrument = None
        item.properties.constellation = None
        item.properties.sensor = None
        image_asset: Asset = item.assets.get(Role.data.value)
        image_asset.size = os.stat(local_url).st_size
        image_asset.airs__managed = False

        image_asset.asset_format = asset_format.value
        image_asset.asset_type = ResourceType.gridded.value
        item.properties.eo__bands = bands

        if local_url != url:
            os.remove(local_url)
        return item
