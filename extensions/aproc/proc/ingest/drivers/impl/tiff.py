import os
import json
import dateutil.parser


from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    Properties, ResourceType,
                                    Role, Band)
from aproc.core.settings import Configuration
from extensions.aproc.proc.ingest.drivers.driver import Driver as ProcDriver
from extensions.aproc.proc.ingest.drivers.exceptions import DriverException
from extensions.aproc.proc.ingest.drivers.impl.utils import get_hash_url


class Driver(ProcDriver):

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
        return [Asset(href=url,
                      roles=[Role.data.value], name=Role.data.value, type="image/tiff",
                      description=Role.data.value, airs__managed=False)]

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        from PIL import Image

        # we try to build a thumbnail and an overview. A failure should not stop the registration.
        try:
            thumbnail = Asset(href=None,
                              roles=[Role.thumbnail.value], name=Role.thumbnail.value, type="image/png",
                              description=Role.thumbnail.value)
            thumbnail.href = self.get_asset_filepath(url, thumbnail)
            image = Image.open(url)
            image.thumbnail([self.thumbnail_size, self.thumbnail_size])
            image.save(thumbnail.href, 'PNG')
            assets.append(thumbnail)
        except Exception as e:
            Driver.LOGGER.warn("Couldn't create the thumbnail of {}".format(url))
            Driver.LOGGER.error(e)
        try:
            overview = Asset(href=None,
                             roles=[Role.overview.value], name=Role.overview.value, type="image/png",
                             description=Role.overview.value)
            overview.href = self.get_asset_filepath(url, overview)
            image = Image.open(url)
            image.thumbnail([self.overview_size, self.overview_size])
            image.save(overview.href, 'PNG')
            assets.append(overview)
        except Exception as e:
            Driver.LOGGER.error(e)
        return assets

    # Implements drivers method
    def get_item_id(self, url: str) -> str:
        return get_hash_url(url)

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        from shapely import geometry
        from shapely import ops
        from shapely import centroid
        from shapely import to_geojson
        from osgeo import gdal
        import rasterio
        import rasterio.features
        import rasterio.warp

        geoms = []
        bands = []

        gdalOptions = gdal.InfoOptions(format='json')
        gdalInfo = gdal.Info(url, options=gdalOptions)
        metadata_keys = list(gdalInfo.get("metadata", {}))
        if metadata_keys:
            description = gdalInfo.get("metadata", {}).get(metadata_keys[0], {}).get("title", "TIFF file")
            try:
                creation_time = dateutil.parser.parse(gdalInfo.get("metadata", {}).get(metadata_keys[0], {}).get("creation_time", ""))
            except dateutil.parser.ParserError:
                creation_time = None
        else:
            description = "TIFF file"
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
            except rasterio.errors.CRSError:
                # It is mandatory to get a crs to get the geometry of the extent
                raise DriverException("Invalid CRS for {}".format(url))
            geom = ops.unary_union(geoms)
            a, b, c, d = geom.bounds
            bbox = [a, b, c, d]
            c = centroid(geom)

        date_time = os.path.getctime(url)
        item = Item(
            id=self.get_item_id(url),
            geometry=json.loads(to_geojson(geom)),
            bbox=bbox,
            centroid=[c.x, c.y],
            properties=Properties(
                datetime=creation_time.timestamp() if creation_time else date_time,
                proj__epsg=crs.to_epsg(),
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.geotiff.value,
                main_asset_format=self.get_main_asset_format(url),
                main_asset_name=Role.data.value,
                description=description
            ),
            assets=dict(map(lambda asset: (asset.name, asset), assets))
        )
        item.properties.instrument = "Unknown"
        item.properties.constellation = "Unknown"
        item.properties.sensor = "Unknown"
        tif_asset: Asset = Asset()
        if os.path.exists(url):
            tif_asset.size = os.stat(url).st_size
        tif_asset.airs__managed = False
        tif_asset.asset_format = AssetFormat.geotiff.value
        tif_asset.asset_type = ResourceType.gridded.value
        item.properties.eo__bands = bands
        return item

    def __check_path__(path: str):
        return (path.lower().endswith(".tif") or path.lower().endswith(".tiff")) and os.path.isfile(path) and os.path.exists(path)

    @staticmethod
    def get_main_asset_format(root):
        return AssetFormat.geotiff.value