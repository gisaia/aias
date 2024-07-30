import json
import os
from pathlib import Path

import dateutil.parser

from airs.core.models.model import (Asset, AssetFormat, Band, Item, ItemFormat,
                                    Properties, ResourceType, Role)
from extensions.aproc.proc.ingest.drivers.driver import Driver as ProcDriver
from extensions.aproc.proc.ingest.drivers.exceptions import DriverException
from extensions.aproc.proc.ingest.drivers.impl.utils import get_file_size, get_hash_url


class ImageDriverHelper:
    def identify_assets(driver: ProcDriver, format: str, url: str) -> list[Asset]:
        assets = []
        assets.append(Asset(href=url,
                      roles=[Role.data.value], name=Role.data.value, type=format,
                      description=Role.data.value, airs__managed=False))
        tfw_path = Path(url).with_suffix(".tfw")
        if tfw_path.exists():
            assets.append(Asset(href=str(tfw_path), size=get_file_size(str(tfw_path)),
                                roles=[Role.extent.value], name=Role.extent.value, type="text/plain",
                                description=Role.extent.value, airs__managed=False, asset_format=AssetFormat.tfw.value, asset_type=ResourceType.other.value))

        j2w_path = Path(url).with_suffix(".j2w")
        if j2w_path.exists():
            assets.append(Asset(href=str(j2w_path), size=get_file_size(str(j2w_path)),
                                roles=[Role.extent.value], name=Role.extent.value, type="text/plain",
                                description=Role.extent.value, airs__managed=False, asset_format=AssetFormat.j2w.value, asset_type=ResourceType.other.value))
        return assets

    def add_overview_if_you_can(driver: ProcDriver, url: str, role: Role, size: int, to_assets: list[Asset]) -> Asset:
        try:
            from PIL import Image
            asset = Asset(href=None,
                          roles=[role.value], name=role.value, type="image/png",
                          description=role.value, asset_format=AssetFormat.png.value)
            asset.href = driver.get_asset_filepath(url, asset)
            image = Image.open(url)
            image.thumbnail([size, size])
            image.save(asset.href, 'PNG')
            asset.size = get_file_size(asset.href)
            to_assets.append(asset)
        except Exception as e:
            driver.LOGGER.warn("Couldn't create the thumbnail of {}".format(url))
            driver.LOGGER.error(e)

    # Implements drivers method
    def fetch_assets(driver: ProcDriver, url: str, assets: list[Asset]) -> list[Asset]:
        ImageDriverHelper.add_overview_if_you_can(driver, url, Role.thumbnail, driver.thumbnail_size, assets)
        ImageDriverHelper.add_overview_if_you_can(driver, url, Role.overview, driver.overview_size, assets)
        return assets

    # Implements drivers method
    def get_item_id(driver: ProcDriver, url: str) -> str:
        return get_hash_url(url)

    # Implements drivers method
    def transform_assets(driver: ProcDriver, format: str, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def to_item(driver: ProcDriver, itemFormat: ItemFormat, assetFormat: AssetFormat, url: str, assets: list[Asset]) -> Item:
        import rasterio
        import rasterio.features
        import rasterio.warp
        from osgeo import gdal
        from shapely import centroid, geometry, ops, to_geojson

        geoms = []
        bands = []

        gdalOptions = gdal.InfoOptions(format='json')
        try:
            gdalInfo = gdal.Info(url, options=gdalOptions)
        except Exception as e:
            raise DriverException("Can not read image metadata from {}: {}".format(url, e))
        metadata_keys = list(gdalInfo.get("metadata", {}))
        if metadata_keys:
            description = gdalInfo.get("metadata", {}).get(metadata_keys[0], {}).get("title", "Image file")
            try:
                creation_time = dateutil.parser.parse(gdalInfo.get("metadata", {}).get(metadata_keys[0], {}).get("creation_time", ""))
            except dateutil.parser.ParserError:
                creation_time = None
        else:
            description = "Image file"
            creation_time = None

        with rasterio.open(url) as dataset:
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

        date_time = os.path.getctime(url)
        item = Item(
            id=driver.get_item_id(url),
            geometry=json.loads(to_geojson(geom)),
            bbox=bbox,
            centroid=[c.x, c.y],
            properties=Properties(
                datetime=creation_time.timestamp() if creation_time else date_time,
                proj__epsg=crs.to_epsg(),
                item_type=ResourceType.gridded.value,
                item_format=itemFormat.value,
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
        if os.path.exists(url):
            image_asset.size = os.stat(url).st_size
        else:
            driver.LOGGER.warn("{} does not exist, size not found".format(url))
        image_asset.airs__managed = False
        image_asset.asset_format = assetFormat.value
        image_asset.asset_type = ResourceType.gridded.value
        item.properties.eo__bands = bands
        return item
