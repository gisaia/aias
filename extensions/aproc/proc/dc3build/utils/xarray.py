import enum
import math

from extensions.aproc.proc.dc3build.drivers.dc3_driver import DC3Driver
import numpy as np
import xarray as xr
from pydantic import BaseModel
from shapely import Point, Polygon

from airs.core.models.model import ChunkingStrategy

POTATO_CHUNK = {"x": 256, "y": 256, "t": 32}
CARROT_CHUNK = {"x": 32, "y": 32, "t": 1024}
SPINACH_CHUNK = {"x": 1024, "y": 1024, "t": 1}


class IntersectionType(enum.Enum):
    LEFT = "left"
    BOTTOM = "bottom"
    RIGHT = "right"
    TOP = "top"
    SAME = "same"


class MinMax(BaseModel):
    min: float
    max: float


def get_chunk_shape(dims: dict[str, int],
                    chunking_strat: ChunkingStrategy = ChunkingStrategy.POTATO) -> dict[str, int]:
    """
    Generates chunks of pre-determined size based on a desired strategy.
    For 'uint32' and 'int32' data types, they result in ~8Mb chunks.
    """

    def resize_time_depth(chunk_shape: dict[str, int], dims: dict[str, int]):
        while dims["t"] <= chunk_shape["t"] / 4:
            chunk_shape["x"] *= 2
            chunk_shape["y"] *= 2
            chunk_shape["t"] = int(chunk_shape["t"]/4)
        return chunk_shape

    if chunking_strat == ChunkingStrategy.POTATO:
        chunk_shape = resize_time_depth(POTATO_CHUNK, dims)
    elif chunking_strat == ChunkingStrategy.CARROT:
        chunk_shape = resize_time_depth(CARROT_CHUNK, dims)
    elif chunking_strat == ChunkingStrategy.SPINACH:
        chunk_shape = SPINACH_CHUNK
    else:
        raise ValueError(f"Chunking strategy '{chunking_strat}' not defined")

    chunk_shape["x"] = min(chunk_shape["x"], dims["x"])
    chunk_shape["y"] = min(chunk_shape["y"], dims["y"])
    chunk_shape["t"] = min(chunk_shape["t"], dims["t"])
    return chunk_shape


def coarse_bands(datacube: xr.Dataset, bands: list[str],
                 x_factor: int, y_factor: int) -> xr.Dataset:
    """
    Mean coarse the bands of a datacube

    :param band: A xarray data array
    :param x_factor: A coarsing factor along the x dimension
    :param y_factor: A coarsing factor along the y dimension
    """
    return datacube.get(bands) \
        .coarsen({"x": x_factor, "y": y_factor}, boundary="pad").mean()


def get_approximate_quantile(band: xr.DataArray,
                             quantile: float = 0.02) -> MinMax:
    """
    Coarse a band along all dimensions to find its
    approximate quantile.

    :param band A xarray data array
    :param x_factor A coarsing factor along the x dimension
    :param y_factor A coarsing factor along the y dimension
    :param quantile The quantile to compute. Needs to be between 0 and 1
    """
    if quantile < 0 or quantile > 1:
        raise ValueError("quantile needs to be between 0 and 1" +
                         f"(value given: {quantile})")

    dims = list(band.sizes.keys())

    min, max = band.chunk({dim: -1 for dim in dims}) \
                   .quantile([quantile, 1-quantile], dim=dims).values

    return MinMax(min=min, max=max)


def get_bounds(ds: xr.Dataset):
    return (float(ds.get("x").min()),
            float(ds.get("y").min()),
            float(ds.get("x").max()),
            float(ds.get("y").max()))


def complete_grid(lon: xr.DataArray | np.ndarray,
                  lat: xr.DataArray | np.ndarray,
                  lon_step: float, lat_step: float, bounds: tuple):
    """
    Completes the coordinates arrays to represent the full extent of 'bounds'
    (lonmin, latmin, lonmax, latmax), according to the input steps.
    """
    lon_before = np.arange(
        lon[0] - lon_step, bounds[0], -lon_step)[::-1]
    lon_after = np.arange(
        lon[-1] + lon_step, bounds[2], lon_step)

    lat_before = np.arange(
        lat[0] - lat_step, bounds[1], -lat_step)[::-1]
    lat_after = np.arange(
        lat[-1] + lon_step, bounds[3], lat_step)

    grid_lon = np.concatenate(
        (lon_before, lon, lon_after))
    grid_lat = np.concatenate(
        (lat_before, lat, lat_after))

    # If missing an element, add the furthest from the bounds
    if len(grid_lon) < math.ceil((bounds[2] - bounds[0]) / lon_step):
        if abs(grid_lon[-1] - bounds[2]) < abs(grid_lon[0] - bounds[0]):
            grid_lon = np.concatenate(
                ([grid_lon[0] - lon_step], grid_lon))
        else:
            grid_lon = np.concatenate(
                (grid_lon, [grid_lon[-1] + lon_step]))
    # If one extra element, remove the furthest from the bounds
    elif len(grid_lon) > math.ceil((bounds[2] - bounds[0]) / lon_step):
        if abs(grid_lon[-1] - bounds[2]) < abs(grid_lon[0] - bounds[0]):
            grid_lon = grid_lon[1:]
        else:
            grid_lon = grid_lon[:-1]

    # If missing an element, add the furthest from the bounds
    if len(grid_lat) < math.ceil((bounds[3] - bounds[1]) / lat_step):
        if abs(grid_lat[-1] - bounds[3]) < abs(grid_lat[0] - bounds[1]):
            grid_lat = np.concatenate(
                ([grid_lat[0] - lat_step], grid_lat))
        else:
            grid_lat = np.concatenate(
                (grid_lat, [grid_lat[-1] + lat_step]))
    # If one extra element, remove the furthest from the bounds
    elif len(grid_lat) > math.ceil((bounds[3] - bounds[1]) / lat_step):
        if abs(grid_lat[-1] - bounds[2]) < abs(grid_lat[0] - bounds[0]):
            grid_lat = grid_lat[1:]
        else:
            grid_lat = grid_lat[:-1]

    return grid_lon, grid_lat


def create_common_grid(composition: dict[str, list[str]], roi_polygon: Polygon):
    """
    From a composition of paths of xarray Datasets, create a grid that can be shared by all assets
    """
    xmin, ymin, xmax, ymax = np.inf, np.inf, -np.inf, -np.inf
    roi_centroid: Point = roi_polygon.centroid
    min_distance = np.inf
    center_granule_idx = {}
    for timestamp, ds_list in composition.items():
        for idx, ds_adress in enumerate(ds_list):
            # Find the centermost granule based on ROI and max bounds
            with xr.open_zarr(ds_adress) as dataset:
                ds_bounds = get_bounds(dataset)
                granule_center = Point((ds_bounds[0] + ds_bounds[2]) / 2,
                                       (ds_bounds[1] + ds_bounds[3]) / 2)
                if roi_centroid.distance(granule_center) < min_distance:
                    min_distance = roi_centroid.distance(granule_center)
                    center_granule_idx["group"] = timestamp
                    center_granule_idx["item"] = idx

                # Update the extent of the datacube
                xmin = min(xmin, ds_bounds[0])
                ymin = min(ymin, ds_bounds[1])
                xmax = max(xmax, ds_bounds[2])
                ymax = max(ymax, ds_bounds[3])

    # Extend its grid to match full extent
    with xr.open_zarr(composition[center_granule_idx["group"]][center_granule_idx["item"]]) as center_granule_ds:
        lon_step = float(center_granule_ds.get("x").diff("x").mean()
                         .values.tolist())
        lat_step = float(center_granule_ds.get("y").diff("y").mean()
                         .values.tolist())

        lon, lat = complete_grid([roi_centroid.x], [roi_centroid.y],
                                 lon_step, lat_step,
                                 (xmin, ymin, xmax, ymax))

    return lon, lat, lon_step, lat_step


def mosaick_list(datasets: list[xr.Dataset], lon: np.ndarray,
                 lat: np.ndarray, lon_step: float, lat_step: float) -> xr.Dataset:

    merged_dataset: xr.Dataset = None
    for ds in datasets:
        # Interpolate the granule with new grid on its extent
        with xr.open_zarr(ds) as dataset:
            bounds = get_bounds(dataset)
            granule_grid = {}
            granule_grid["x"] = lon[(lon[:] >= bounds[0])
                                    & (lon[:] <= bounds[2])]
            granule_grid["y"] = lat[(lat[:] >= bounds[1])
                                    & (lat[:] <= bounds[3])]
            granule_grid["x"], granule_grid["y"] = complete_grid(
                granule_grid["x"], granule_grid["y"],
                lon_step, lat_step, bounds)
            dims = {"x": len(granule_grid["x"]),
                    "y": len(granule_grid["y"]), "t": 1}

            merged_dataset = merge_datasets(
                merged_dataset,
                dataset.interp_like(
                    xr.Dataset(granule_grid), method="nearest")
                .chunk(get_chunk_shape(dims, ChunkingStrategy.SPINACH)))

    return merged_dataset


def merge_datasets(first_dataset: xr.Dataset,
                   second_dataset: xr.Dataset) -> xr.Dataset:
    """
    Merge two datasets based on their geographical bounds as well as
    their bands. Performs a mosaicking for the bands in common, while just
    appending the other bands to the resulting dataset.
    """

    if first_dataset is None:
        return second_dataset
    if second_dataset is None:
        return first_dataset

    # It is only possible to concatenate datasets that contain the same bands
    common_bands = []
    for band in first_dataset.data_vars.keys():
        if band in second_dataset.data_vars.keys():
            common_bands.append(band)

    # If they intersect in any way but don't hold the same data,
    # then no mosaickin is needed
    if len(common_bands) == 0:
        return xr.merge(
            (first_dataset, second_dataset), combine_attrs="override")

    rest_first_ds = first_dataset[
        list(set(first_dataset.data_vars.keys()).difference(common_bands))]
    common_first_ds = first_dataset[common_bands]

    rest_second_ds = second_dataset[
        list(set(second_dataset.data_vars.keys()).difference(common_bands))]
    commonSecondDS = second_dataset[common_bands]

    return xr.merge(
        (mosaick_pair(common_first_ds, commonSecondDS),
         rest_first_ds, rest_second_ds), combine_attrs="override")


def intersect(first_dataset: xr.Dataset,
              second_dataset: xr.Dataset) -> list[IntersectionType]:
    first_bounds = get_bounds(first_dataset)
    second_bounds = get_bounds(second_dataset)

    if first_bounds == second_bounds:
        return [IntersectionType.SAME]

    intersections = []
    if first_bounds[0] < second_bounds[2] < first_bounds[2]:
        intersections.append(IntersectionType.LEFT)
    if first_bounds[1] < second_bounds[3] < first_bounds[3]:
        intersections.append(IntersectionType.BOTTOM)
    if first_bounds[0] < second_bounds[0] < first_bounds[2]:
        intersections.append(IntersectionType.RIGHT)
    if first_bounds[1] < second_bounds[1] < first_bounds[3]:
        intersections.append(IntersectionType.TOP)

    return np.array(intersections)


def mosaick_pair(first_dataset: xr.Dataset,
                 second_dataset: xr.Dataset) -> xr.Dataset:

    intersection_types = intersect(first_dataset, second_dataset)

    # If no intersections, auto-magically combine
    if len(intersection_types) == 0:
        return xr.combine_by_coords(
            (first_dataset, second_dataset), combine_attrs="override")

    # If they represent the same extent of data, merge based on criterion
    if IntersectionType.SAME in intersection_types:
        if first_dataset.attrs["product_timestamp"] \
                >= second_dataset.attrs["product_timestamp"]:
            ds = first_dataset.combine_first(second_dataset) \
                    .assign_attrs({"product_timestamp":
                                   first_dataset.attrs["product_timestamp"]})
            return ds
        else:
            ds = second_dataset.combine_first(first_dataset) \
                    .assign_attrs({"product_timestamp":
                                   second_dataset.attrs["product_timestamp"]})
            return ds

    first_bounds = get_bounds(first_dataset)
    second_bounds = get_bounds(second_dataset)

    # Resolve overlapping counter-clockwise
    if IntersectionType.LEFT in intersection_types:
        left = second_dataset.where(
            second_dataset.x < first_bounds[0], drop=True)
        first_ds_intersection = first_dataset.where(
            first_dataset.x <= second_bounds[2], drop=True)
        second_ds_intersection = second_dataset.where(
            second_dataset.x >= first_bounds[0], drop=True)
        intersection = mosaick_pair(first_ds_intersection,
                                    second_ds_intersection)
        right = first_dataset.where(
            first_dataset.x > second_bounds[2], drop=True)
        if len(left.x) == 0:
            return xr.concat([intersection, right], dim="x")
        return xr.concat([left, intersection, right], dim="x")

    if IntersectionType.BOTTOM in intersection_types:
        bottom = second_dataset.where(
            second_dataset.y < first_bounds[1], drop=True)
        first_ds_intersection = first_dataset.where(
            first_dataset.y <= second_bounds[3], drop=True)
        second_ds_intersection = second_dataset.where(
            second_dataset.y >= first_bounds[1], drop=True)
        intersection = mosaick_pair(first_ds_intersection,
                                    second_ds_intersection)
        top = first_dataset.where(
            first_dataset.y > second_bounds[3], drop=True)
        if len(bottom.y) == 0:
            return xr.concat([intersection, top], dim="y")
        return xr.concat([bottom, intersection, top], dim="y")

    if IntersectionType.RIGHT in intersection_types:
        left = first_dataset.where(
            first_dataset.x < second_bounds[0], drop=True)
        first_ds_intersection = first_dataset.where(
            first_dataset.x >= second_bounds[0], drop=True)
        second_ds_intersection = second_dataset.where(
            second_dataset.x <= first_bounds[2], drop=True)
        intersection = mosaick_pair(first_ds_intersection,
                                    second_ds_intersection)
        right = second_dataset.where(
            second_dataset.x > first_bounds[2], drop=True)
        if len(right.x) == 0:
            return xr.concat([left, intersection], dim="x")
        return xr.concat([left, intersection, right], dim="x")

    if IntersectionType.TOP in intersection_types:
        bottom = first_dataset.where(
            first_dataset.y < second_bounds[1], drop=True)
        first_ds_intersection = first_dataset.where(
            first_dataset.y >= second_bounds[1], drop=True)
        second_ds_intersection = second_dataset.where(
            second_dataset.y <= first_bounds[3], drop=True)
        intersection = mosaick_pair(first_ds_intersection,
                                    second_ds_intersection)
        top = second_dataset.where(
            second_dataset.y > first_bounds[3], drop=True)
        if len(top.y) == 0:
            return xr.concat([bottom, intersection], dim="y")
        return xr.concat([bottom, intersection, top], dim="y")
