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


def helper_build_cog(source: str, target: str, params: dict[str, str] = {}, downscale_factor: int = -1, max_resolution_m: int = -1):
    from osgeo import gdal
    kwargs = {'format': 'COG', 'dstSRS': 'EPSG:3857'}

    storage: AnyStorage = AccessManager.resolve_storage(source)
    source = storage.gdal_transform_href_vsi(source)
    with gdal.config_options(storage.get_gdal_stream_options()):
        if downscale_factor > 0 or max_resolution_m > 0:
            with gdal.Open(source) as ds:
                original_x_res = ds.GetGeoTransform()[1]  # Pixel width
                original_y_res = abs(ds.GetGeoTransform()[5])  # Pixel height (absolute value)
            new_x_res = original_x_res * downscale_factor
            new_y_res = original_y_res * downscale_factor
            if max_resolution_m > 0:
                if max_resolution_m > new_x_res:
                    decrease_factor = new_x_res / max_resolution_m
                    new_x_res = max_resolution_m
                    new_y_res = new_y_res * decrease_factor
            kwargs['resampleAlg'] = 'average'
            kwargs["xRes"] = str(new_x_res)
            kwargs["yRes"] = str(new_y_res)

        if params:
            kwargs.update(params)
        print(f"Warping {source} to {target} with options: {kwargs}")
        gdal.Warp(target, source, **kwargs)
