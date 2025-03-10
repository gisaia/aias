import math
import re
from datetime import datetime, timezone

import xarray as xr
from shapely.geometry import Polygon

from airs.core.models.model import (AssetFormat, DimensionType,
                                    HorizontalSpatialDimension, Indicators,
                                    Item, ItemFormat, ItemGroup, Properties,
                                    ResourceType, Role, TemporalDimension,
                                    Variable)
from extensions.aproc.proc.dc3build.drivers.dc3_driver import DC3Driver
from extensions.aproc.proc.dc3build.model.dc3build_input import \
    InputDC3BuildProcess
from extensions.aproc.proc.dc3build.utils.geo import bbox2polygon, roi2geometry
from extensions.aproc.proc.dc3build.utils.raster import get_all_aliases
from extensions.aproc.proc.drivers.exceptions import DriverException


def create_datacube_metadata(request: InputDC3BuildProcess, items: dict[str, dict[str, Item]],
                             datacube: xr.Dataset, x_step: float | int | None,
                             y_step: float | int | None) -> Properties:
    properties = Properties()

    # Get some properties directly from the request
    properties.start_datetime = min(list(map(lambda group: group.dc3__datetime, request.composition)))
    properties.end_datetime = max(list(map(lambda group: group.dc3__datetime, request.composition)))
    properties.datetime = properties.start_datetime
    properties.gsd = request.target_resolution
    properties.item_type = ResourceType.cube.name
    properties.item_format = ItemFormat.adc3.name
    properties.main_asset_format = AssetFormat.zarr.name
    properties.proj__epsg = request.target_projection
    properties.main_asset_name = Role.datacube.value

    # Use first item for certain properties
    first_reference = request.composition[0].dc3__references[0]
    properties.observation_type = items[first_reference.dc3__collection][first_reference.dc3__id].properties.observation_type

    # Get keywords from composition's items
    properties.keywords = request.keywords or []
    properties.locations = []
    for it in DC3Driver.__flat_items__(items):
        if it.properties.locations:
            properties.locations = properties.locations + it.properties.locations
        if it.properties.programme:
            properties.keywords.append(it.properties.programme)
        if it.properties.constellation:
            properties.keywords.append(it.properties.constellation)
        if it.properties.satellite:
            properties.keywords.append(it.properties.satellite)
        if it.properties.platform:
            properties.keywords.append(it.properties.platform)
        if it.properties.instrument:
            properties.keywords.append(it.properties.instrument)
        if it.properties.sensor:
            properties.keywords.append(it.properties.sensor)
    properties.keywords = list(set(properties.keywords))

    properties.annotations = " ".join(properties.keywords)

    properties.cube__variables = {}
    properties.eo__bands = request.bands  # The cube bands should be the same as the requested bands, asset tracability is added.
    for band in request.bands:
        properties.cube__variables[band.name] = Variable(
            dimensions=["x", "y", "t"],
            type="data", description=band.description,
            extent=[datacube.get(band.name).min().values.tolist(),
                    datacube.get(band.name).max().values.tolist()],
            unit=band.dc3__unit, expression=band.dc3__expression
        )

    properties.cube__dimensions = {}
    properties.cube__dimensions["x"] = HorizontalSpatialDimension(
        type=DimensionType.spatial.value, axis="x", description="",
        extent=[float(datacube.get("x").values[0]),
                float(datacube.get("x").values[-1])],
        step=x_step, reference_system=request.target_projection
    )

    properties.cube__dimensions["y"] = HorizontalSpatialDimension(
        type=DimensionType.spatial.value, axis="y", description="",
        extent=[float(datacube.get("y").values[0]),
                float(datacube.get("y").values[-1])],
        step=y_step, reference_system=request.target_projection
    )

    t_step = None
    if len(datacube.get("t")) != 1:
        t_step = str(datacube.get("t").diff("t").sum().values
                     / (len(datacube.get("t")) - 1))
    properties.cube__dimensions["t"] = TemporalDimension(
        type=DimensionType.temporal.value, axis="t", description="",
        extent=[datetime.fromtimestamp(
                    datacube.get("t").values[0], timezone.utc).isoformat() + 'Z',
                datetime.fromtimestamp(
                    datacube.get("t").values[-1], timezone.utc).isoformat() + 'Z'],
        step=t_step
    )

    properties.dc3__overview = {}
    for band in request.bands:
        band.dc3__min = datacube.get(band.name).min().values.tolist()
        band.dc3__max = datacube.get(band.name).max().values.tolist()
        if band.dc3__cmap:
            properties.dc3__overview = {band.dc3__cmap: band.name}
        if band.dc3__rgb:
            properties.dc3__overview[band.dc3__rgb.value] = band.name

    if len(properties.dc3__overview) == 0:
        properties.dc3__overview = {"rainbow": list(datacube.data_vars.keys())[0]}

    properties.dc3__number_of_chunks = 1
    for chunks in datacube.chunks.values():
        properties.dc3__number_of_chunks *= len(chunks)

    data_weight = list(datacube.variables.values())[0].data.dtype.itemsize
    properties.dc3__chunk_weight = datacube.chunks['x'][0] * datacube.chunks['y'][0] \
        * datacube.chunks['t'][0] * data_weight

    composition_start = math.inf
    composition_end = -math.inf

    composition_by_alias: list[dict[str, list[Item]]] = []
    for group in request.composition:
        group_composition: dict[str, list[Item]] = {}
        for ref in group.dc3__references:
            item = items[ref.dc3__collection][ref.dc3__id]
            if item:
                # Split the rasters by timestamp and product type
                if ref.dc3__alias in group_composition:
                    group_composition[ref.dc3__alias].append(item)
                else:
                    group_composition[ref.dc3__alias] = [item]

                # Find the first and last timestamp
                timestamp = item.properties.datetime.timestamp()
                if timestamp < composition_start:
                    composition_start = timestamp
                if timestamp > composition_end:
                    composition_end = timestamp
            else:
                raise DriverException(
                    f'Raster "{ref.dc3__id}" was not found in collection {ref.dc3__collection}')
        composition_by_alias.append(group_composition)

    timespan = composition_start - composition_end
    indicators_per_group_per_alias: list[dict[str, Indicators]] = []
    roi_polygon = roi2geometry(request.roi)

    for group in composition_by_alias:
        group_indicators_per_alias = {}

        # Split rasters of the group by type
        for alias, group_items in group.items():
            group_indicators_per_alias[alias] = Indicators(
                dc3__time_compacity=compute_time_compacity(group_items, timespan),
                dc3__spatial_coverage=compute_spatial_coverage(group_items, roi_polygon),
                dc3__group_lightness=compute_group_lightness(group_items, roi_polygon)
            )
        indicators_per_group_per_alias.append(group_indicators_per_alias)

    # For the group, the indicator is the product of those of each type
    for idx, group in enumerate(indicators_per_group_per_alias):
        request.composition[idx].dc3__quality_indicators = Indicators(
            dc3__time_compacity=math.prod(
                    map(lambda t: t.dc3__time_compacity, group.values())),
            dc3__spatial_coverage=math.prod(
                    map(lambda t: t.dc3__spatial_coverage, group.values())),
            dc3__group_lightness=math.prod(
                    map(lambda t: t.dc3__group_lightness, group.values()))
        )
    properties.dc3__composition = request.composition

    # For each alias, the indicator is the product of those of each group
    # of the desired alias
    alias_indicators: dict[str, Indicators] = {}
    aliases = get_all_aliases(request)
    for alias in aliases:
        alias_indicators[alias] = Indicators(
            dc3__time_compacity=math.prod(
                map(lambda g, alias=alias: g[alias].dc3__time_compacity if alias in g
                    else 1, indicators_per_group_per_alias)),
            dc3__spatial_coverage=math.prod(
                map(lambda g, alias=alias: g[alias].dc3__spatial_coverage if alias in g
                    else 1, indicators_per_group_per_alias)),
            dc3__group_lightness=math.prod(
                map(lambda g, alias=alias: g[alias].dc3__group_lightness if alias in g
                    else 1, indicators_per_group_per_alias))
        )

    for idx, band in enumerate(request.bands):
        # Find which product types constitute the band
        aliases_in_band = re.findall(rf'({"|".join(aliases)})\.[a-zA-Z0-9]*',
                                     band.dc3__expression)

        # Compute the indicator as a product of the those of the products
        # used to compute the band
        band.dc3__quality_indicators = Indicators(
            dc3__time_compacity=math.prod(
                map(lambda t: alias_indicators[t].dc3__time_compacity,
                    aliases_in_band)),
            dc3__spatial_coverage=math.prod(
                map(lambda t: alias_indicators[t].dc3__spatial_coverage,
                    aliases_in_band)),
            dc3__group_lightness=math.prod(
                map(lambda t: alias_indicators[t].dc3__group_lightness,
                    aliases_in_band))
        )
        band.index = idx + 1
        band.asset = Role.datacube.value

    properties.eo__bands = request.bands

    # For the cube, the indicator is the product of those of each group
    properties.dc3__quality_indicators = Indicators(
        dc3__time_compacity=math.prod(
            map(lambda g: g.dc3__quality_indicators.dc3__time_compacity, request.composition)),
        dc3__spatial_coverage=math.prod(
            map(lambda g: g.dc3__quality_indicators.dc3__spatial_coverage, request.composition)),
        dc3__group_lightness=math.prod(
            map(lambda g: g.dc3__quality_indicators.dc3__group_lightness, request.composition)),
        dc3__time_regularity=compute_time_regularity(request.composition)
    )

    # Fill ratio is the average of how much each band is filled
    fill_ratio = 0
    cube_size = len(datacube.x) * len(datacube.y) * len(datacube.t)
    for band in datacube.data_vars.values():
        fill_ratio += 1 - band.isnull().sum().compute().values / cube_size
    properties.dc3__fill_ratio = fill_ratio / len(datacube.data_vars)

    return properties


def compute_time_compacity(items: list[Item],
                           timespan: int) -> float:
    """
    Computes how compact time-wise the list of rasters is in regards to
    the global timespan of the datacube.

    The time compacity corresponds to 1 - (t_max - t_min) / timespan
    """
    if timespan == 0:
        return 1
    raster_times = list(map(lambda r: r.properties.datetime.timestamp(), items))

    return 1 - (max(raster_times) - min(raster_times)) / timespan


def __get_items_geometry_union(items: list[Item], roi: Polygon) -> tuple[list[Polygon], Polygon]:
    """
    Get the geometry of a list of Items based on their coordinates or bbox otherwise. Compute their union restricted to the input ROI
    """
    def project_item_geometry(item: Item):
        geo: Polygon = None
        if (
            item.geometry["type"].lower() == "polygon"
            and item.geometry["coordinates"][0]
        ):
            geo = Polygon(item.geometry["coordinates"][0])
        if (
            item.geometry["type"].lower() == "multipolygon"
            and item.geometry["coordinates"][0]
            and item.geometry["coordinates"][0][0]
        ):
            geo = Polygon(item.geometry["coordinates"][0][0])
        if geo is None:
            # Could it be an issue in 3D ?
            geo = bbox2polygon(item.bbox[0], item.bbox[1], item.bbox[2], item.bbox[3])
        return geo

    item_geometries = list(map(project_item_geometry, items))

    polygon_union = item_geometries[0]
    for polygon in item_geometries[1:]:
        polygon_union = polygon_union.union(polygon)
    polygon_union = polygon_union.intersection(roi)

    return item_geometries, polygon_union


def compute_spatial_coverage(items: list[Item], roi: Polygon) -> float:
    """
    Computes how well the list of rasters cover the desired ROI.

    The spatial coverage corresponds to area(U(polygon)) / area(ROI).
    """
    _, polygon_union = __get_items_geometry_union(items, roi)

    return polygon_union.area / roi.area


def compute_group_lightness(items: list[Item], roi: Polygon) -> float:
    """
    Computes how little redundant geographic information is carried
    in the input list of rasters.

    The group lightness corresponds to area(U(polygon)) / S(area(polygon)).
    """
    items_polygon, polygon_union = __get_items_geometry_union(items, roi)

    sum_areas = sum(map(lambda p: p.intersection(roi).area, items_polygon))

    return polygon_union.area / sum_areas


def compute_time_regularity(composition: list[ItemGroup]) -> float:
    """
    Computes an indicator of how regularly spaced
    the time slices of a datacube is.

    The time regularity corresponds to 1 - std(timeDeltas)/avg(timeDeltas).
    """
    if len(composition) == 1:
        return 1

    delta_times = []

    for i in range(len(composition) - 1):
        delta_times.append(
            (composition[i + 1].dc3__datetime - composition[i].dc3__datetime).total_seconds())
    avg_delta_time = sum(delta_times) / len(delta_times)

    return 1 - math.sqrt(sum(
        map(lambda t: math.pow(t - avg_delta_time, 2), delta_times)
            ) / len(delta_times)) / avg_delta_time
