import json
import os


from airs.core.models import mapper
from airs.core.models.model import (Asset, AssetFormat, Indicators, Item, ItemFormat, MimeType, Properties,
                                    ResourceType, Role, VariableType)
from extensions.aproc.proc.dc3build.drivers.dc3_driver import DC3Driver
from extensions.aproc.proc.dc3build.model.dc3build_input import InputDC3BuildProcess
from extensions.aproc.proc.ingest.drivers.impl.utils import get_file_size


class Driver(DC3Driver):

    def __init__(self):
        super().__init__()

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        DC3Driver.init(configuration)

    # Implements drivers method
    def supports(self, item: Item) -> bool:
        return item.properties.item_format and item.properties.item_format.lower() == ItemFormat.safe.value.lower()

    def __flat_items__(items: dict[str, dict[str, Item]]) -> list[Item]:
        its = list(map(lambda v: list(v.values()), items.values()))
        return [x for xs in its for x in xs]

    # Implements drivers method
    def create_cube(self, dc3_request: InputDC3BuildProcess, items: dict[str, dict[str, Item]], target_directory: str) -> Item:
        CUBE_ASSET_NAME = "cube"
        first_item: Item = items.get(dc3_request.composition[0].dc3__references[0].dc3__collection).get(dc3_request.composition[0].dc3__references[0].dc3__id)
        # item.collection, item.catalog and item.id are managed by the process, no need to set it!
        item = Item()
        item.properties = Properties()
        item.properties.start_datetime = min(list(map(lambda group: group.dc3__datetime, dc3_request.composition)))
        item.properties.end_datetime = max(list(map(lambda group: group.dc3__datetime, dc3_request.composition)))
        item.properties.datetime = item.properties.start_datetime
        item.properties.keywords = dc3_request.keywords
        item.properties.gsd = dc3_request.target_resolution
        item.properties.item_type = ResourceType.cube.name
        item.properties.item_format = ItemFormat.adc3.name
        item.properties.main_asset_format = AssetFormat.zarr.name
        item.properties.main_asset_name = CUBE_ASSET_NAME
        item.properties.observation_type = first_item.properties.observation_type
        if dc3_request.keywords is None:
            dc3_request.keywords = []
        if first_item.properties.programme:
            item.properties.keywords.append(first_item.properties.programme)
        if first_item.properties.constellation:
            item.properties.keywords.append(first_item.properties.constellation)
        if first_item.properties.satellite:
            item.properties.keywords.append(first_item.properties.satellite)
        if first_item.properties.platform:
            item.properties.keywords.append(first_item.properties.platform)
        if first_item.properties.instrument:
            item.properties.keywords.append(first_item.properties.instrument)
        if first_item.properties.sensor:
            item.properties.keywords.append(first_item.properties.sensor)
        item.properties.annotations = " ".join(dc3_request.keywords)
        item.properties.locations = []
        for it in Driver.__flat_items__(items):
            if it.properties.locations:
                item.properties.locations = item.properties.locations + it.properties.locations
        item.properties.eo__bands = dc3_request.bands  # The cube bands should be the same as the requested bands, asset tracability is added.
        item.properties.cube__variables = {}
        for band in dc3_request.bands:
            item.properties.cube__variables[band.name] = VariableType.data
        item.properties.proj__epsg = dc3_request.target_projection

        # SECTION TO IMPLEMENT
        item.bbox = [1, 1, 3, 3]
        item.geometry = json.loads(dc3_request.roi)  # TODO
        item.centroid = [0, 0]  # TODO
        i = 1
        for band in item.properties.eo__bands:
            band.index = i
            i = 1 + 1
            band.asset = CUBE_ASSET_NAME
            band.dc3__quality_indicators = Indicators(
                dc3__time_compacity=0,  # TODO
                dc3__group_lightness=0,  # TODO
                dc3__spatial_coverage=0,  # TODO
                dc3__time_regularity=0)  # TODO
        item.properties.dc3__quality_indicators = Indicators(
            dc3__time_compacity=0,  # TODO
            dc3__group_lightness=0,  # TODO
            dc3__spatial_coverage=0,  # TODO
            dc3__time_regularity=0)  # TODO
        item.properties.dc3__composition = dc3_request.composition  # TODO set the dc3__quality_indicators of the groups
        item.properties.dc3__number_of_chunks = 0   # TODO compute the number of chunks
        item.properties.dc3__chunk_weight = 0   # TODO compute the chunk weight
        item.properties.dc3__fill_ratio = 0   # TODO compute the fill ratio
        item.properties.cube__dimensions = {}   # TODO set the dimensiosn
        item.properties.cube__variables = {}   # TODO set the variables

        cube_file = os.path.join(target_directory, "cube.zarr")
        with open(cube_file, "wb") as out:
            out.truncate(1024 * 1024 * 10)
        item.assets = {
            CUBE_ASSET_NAME: Asset(
                name=CUBE_ASSET_NAME,
                size=get_file_size(cube_file),
                type=MimeType.ZARR.name,
                href=cube_file,
                asset_type=ResourceType.cube.name,
                asset_format=AssetFormat.zarr.name,
                airs__managed=True,
                title=dc3_request.description,
                description=dc3_request.description,
                roles=[Role.datacube, Role.data, Role.zarr]
            )
        }
        Driver.LOGGER.debug("Cube STAC Item: {}".format(mapper.to_json(item)))
        return item
