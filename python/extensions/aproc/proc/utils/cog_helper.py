from aias_common.access.manager import AccessManager, AnyStorage
from airs.core.models.model import Role, ResourceType, AssetFormat, MimeType, Item, Asset
from extensions.aproc.proc.enrich.drivers.enrich_driver import EnrichDriver
from time import time
import os


def helper_create_asset_from_location(item: Item, asset_type: str, asset_location: str, resource_type=ResourceType.gridded.value, asset_format=AssetFormat.geotiff.value, mime_type=MimeType.TIFF.value) -> Asset:
    asset = Asset(
        name=Role.cog.value,
        size=AccessManager.get_size(asset_location),     # set once asset created
        href=asset_location,  # set below
        asset_type=resource_type,
        asset_format=asset_format,
        roles=[asset_type],
        type=mime_type,
        title="{} for {}/{}".format(asset_type, item.collection, item.id),
        description="{} for {}/{}".format(asset_type, item.collection, item.id),
        proj__epsg=3857,
        airs__managed=True
    )
    return asset



def helper_build_cog(source: str, target: str, params: dict[str, str]={}):
    from osgeo import gdal
    kwargs = {'format': 'COG', 'dstSRS': 'EPSG:3857'}
    if params:
        kwargs.update(params)

    storage: AnyStorage = AccessManager.resolve_storage(source)
    source = storage.gdal_transform_href_vsi(source)
    with gdal.config_options(storage.get_gdal_stream_options()):
        gdal.Warp(target, source, **kwargs)
