from typing import Any

from airs.core.models.model import Asset, AssetFormat, Item, MimeType, Role
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.enrich.drivers.enrich_driver import EnrichDriver
from extensions.aproc.proc.enrich.drivers.impl.cog_builder_helper import \
    CogBuilderHelper
from extensions.aproc.proc.utils.compare import includes_case_insensitive


class Driver(EnrichDriver):

    SUPPORTED_ASSET_TYPES = [AssetFormat.cog.value.lower(), AssetFormat.overview_cog.value.lower()]
    SUPPORTED_SOURCE_MIME_TYPES = [MimeType.TIFF.value, MimeType.COG.value]
    SUPPORTED_SOURCE_ASSET_FORMAT = [AssetFormat.geotiff.value, AssetFormat.cog.value]

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
        data_asset = item.assets.get(Role.data.value)
        if not data_asset or not data_asset.href:
            raise DriverException("Data asset not found for {}/{}".format(item.collection, item.id))

        source = data_asset.href
        target = self.get_target_asset_filepath(item.id, enrichment)
        cog_max_width_or_height = Driver.configuration['cog_max_width_or_height']
        if enrichment == AssetFormat.overview_cog.value.lower():
            cog_max_width_or_height = Driver.configuration['cog_overview_max_width_or_height']

        CogBuilderHelper.build(source, target, max_px_width_or_height=cog_max_width_or_height)
        return [CogBuilderHelper.create_asset(item, enrichment, target)]
