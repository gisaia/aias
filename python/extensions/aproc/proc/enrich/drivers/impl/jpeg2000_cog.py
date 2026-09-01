import tempfile
from typing import Any

from aias_common.access.manager import AccessManager
from airs.core.models.model import Asset, AssetFormat, Item, MimeType, Role
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.enrich.drivers.enrich_driver import EnrichDriver
from extensions.aproc.proc.enrich.drivers.impl.cog_builder_helper import \
    CogBuilderHelper


# TODO: move that to utils
def includes_case_insensitive(value: str, allowed_values: list[str]) -> bool:
    return any(s.lower() == value.lower() for s in allowed_values)


class Driver(EnrichDriver):

    SUPPORTED_ASSET_TYPES = [AssetFormat.cog.value.lower(), AssetFormat.overview_cog.value.lower()]
    SUPPORTED_SOURCE_MIME_TYPES = [MimeType.JPEG2000.value]
    SUPPORTED_SOURCE_ASSET_FORMAT = [AssetFormat.jpg2000.value]

    def __init__(self):
        super().__init__()

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        CogBuilderHelper.init(Driver, configuration)

    # Implements drivers method
    def supports(self, resource: Item, extra_params: dict[str, Any] = {}) -> bool:
        if self.supports_format(resource, extra_params, Driver.SUPPORTED_ASSET_TYPES):
            asset_source = resource.assets.get(Role.data.value)
            if asset_source is not None and asset_source.href:
                if includes_case_insensitive(asset_source.type, Driver.SUPPORTED_SOURCE_MIME_TYPES) or includes_case_insensitive(asset_source.asset_format, Driver.SUPPORTED_SOURCE_ASSET_FORMAT):
                    return True
        return False

    # Implements drivers method
    def create_enrichment(self, item: Item, enrichment: str) -> list[Asset]:
        from osgeo import gdal
        gdal.SetConfigOption('CPL_TMPDIR', tempfile.gettempdir())

        data_asset = item.assets.get(Role.data.value)
        if not data_asset or not data_asset.href:
            raise DriverException("Data asset not found for {}/{}".format(item.collection, item.id))

        source = data_asset.href
        target = self.get_target_asset_filepath(item.id, enrichment)

        cog_max_width_or_height = Driver.configuration['cog_max_width_or_height']
        if enrichment == AssetFormat.overview_cog.value.lower():
            cog_max_width_or_height = Driver.configuration['cog_overview_max_width_or_height']

        # There is an issue when trying to create the COG directly from remote storage:
        # - the jpeg2000 file can be not georeferenced, failing the creation of the VRT file
        # - reading the data fails to build the COG
        with AccessManager.make_local(source) as local_source:
            self.LOGGER.info("Building cog from {}".format(source))
            CogBuilderHelper.build(local_source, target, max_px_width_or_height=cog_max_width_or_height)

        return [CogBuilderHelper.create_asset(item, enrichment, target)]
