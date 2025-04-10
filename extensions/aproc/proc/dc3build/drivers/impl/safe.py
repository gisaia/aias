import functools
import json
import os
import re

from airs.core.models import mapper
from airs.core.models.model import (Asset, AssetFormat, ChunkingStrategy, Item,
                                    ItemFormat, MimeType, ResourceType, Role)
from aias_common.access.manager import AccessManager
from extensions.aproc.proc.dc3build.drivers.dc3_driver import DC3Driver
from extensions.aproc.proc.dc3build.model.dc3build_input import \
    InputDC3BuildProcess


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

    # Implements drivers method
    def create_cube(self, dc3_request: InputDC3BuildProcess, items: dict[str, dict[str, Item]], target_directory: str) -> Item:
        import numpy as np
        import rasterio
        import xarray as xr
        import zarr
        from shapely import to_geojson

        from extensions.aproc.proc.dc3build.utils.geo import roi2geometry
        from extensions.aproc.proc.dc3build.utils.gif import create_gif
        from extensions.aproc.proc.dc3build.utils.metadata import \
            create_datacube_metadata
        from extensions.aproc.proc.dc3build.utils.raster import (
            find_raster_files, get_all_aliases, get_eval_formula)
        from extensions.aproc.proc.dc3build.utils.raster_to_zarr import \
            RasterToZarr
        from extensions.aproc.proc.dc3build.utils.xarray import (
            create_common_grid, get_chunk_shape, mosaick_list)

        """ ATP: Composition of href """
        # What are the bands that are needed by alias?
        bands_per_alias: dict[str, list[str]] = {}
        aliases = get_all_aliases(dc3_request)

        for alias in aliases:
            for b in dc3_request.bands:
                bands_per_alias[alias] = re.findall(rf"{alias}\.([a-zA-Z0-9]*)", b.dc3__expression)

        # Sort composition groups by datetime
        dc3_request.composition.sort(key=lambda g: g.dc3__datetime)

        roi_polygon = roi2geometry(dc3_request.roi)
        # Access all assets (only desired bands)
        composition: dict[int, list[str]] = {}
        for group in dc3_request.composition:
            timestamp = int(group.dc3__datetime.timestamp())
            composition[timestamp] = []

            for e in group.dc3__references:
                # Href of the zip containing all bands
                a: Asset = items[e.dc3__collection][e.dc3__id].assets[Role.data.value]
                # TODO: SRE or FRE ? => Products for GEODES
                # band_regex = re.compile(rf".*/.*SRE_({'|'.join(bands_per_alias[e.dc3__alias])})\.tif")
                band_regex = re.compile(rf".*/IMG_DATA/.*({'|'.join(bands_per_alias[e.dc3__alias])})\.jp2")

                # TODO: should I use path_within_asset instead of regex ?
                with AccessManager.stream(a.href) as ab:
                    bands = find_raster_files(ab, band_regex, e.dc3__alias)

                # Find the lowest resolution product among those required
                min_res = np.Inf
                try:
                    with rasterio.Env(**AccessManager.get_rasterio_session(a.href)):
                        for p in bands.values():
                            with rasterio.open("zip+" + a.href + "!" + p) as src:
                                if src.res[0] < min_res:
                                    min_res = src.res[0]

                        zarrs: list[zarr.DirectoryStore] = []

                        # For each object, create a zarr
                        for band, path in bands.items():
                            with rasterio.open("zip+" + a.href + "!" + path, "r+") as src:
                                # Create Raster object
                                raster = RasterToZarr(band, src, dc3_request.target_projection,
                                                      min_res, roi_polygon)

                                # Create zarr store
                                # TODO: add method to create a temporary file ? -> have a process id that is used
                                zarr_tmp_root_path = os.path.join(AccessManager.tmp_dir, f"{e.dc3__collection}_{e.dc3__id}.zarr")
                                zarr_dir = raster.create_zarr_dir(
                                    zarr_tmp_root_path, int(items[e.dc3__collection][e.dc3__id].properties.datetime.timestamp()), timestamp)

                                zarrs.append(zarr_dir)
                except Exception:
                    # Can raise a CPLE_AppDefinedError error
                    ...

                if len(zarrs) != len(bands):
                    raise RuntimeError(f"Error while generating the zarr for the bands of {e.dc3__id}")

                # Retrieve the zarr stores as xarray objects that are on a same grid
                merged_bands: xr.Dataset = None
                for zarr_dir in zarrs:
                    with xr.open_zarr(zarr_dir) as xr_zarr:
                        if merged_bands is None:
                            merged_bands = xr_zarr
                        else:
                            merged_bands = xr.merge((merged_bands, xr_zarr))

                # Merge all bands
                chunk_shape = get_chunk_shape(merged_bands.sizes, ChunkingStrategy.SPINACH)
                # There could be the same product in multiple slices, so we need to use the timestamp to discriminate them
                merged_zarr_path = os.path.join(AccessManager.tmp_dir, f"{os.path.basename(a.href)}_{timestamp}.zarr")
                composition[timestamp].append(merged_zarr_path)

                merged_bands.chunk(chunk_shape) \
                            .to_zarr(merged_zarr_path, mode="w") \
                            .close()

                # Clean up the temporary files created
                for zarr_dir in zarrs:
                    if AccessManager.exists(zarr_dir.path):
                        AccessManager.clean(zarr_dir.path)  # !DELETE!
                del zarrs
                del merged_bands

        """ ATP: Composition of xr.Dataset """

        lon, lat, lon_step, lat_step = create_common_grid(composition, roi_polygon)

        # Mosaicking of each of the group on the common grid
        def merge_mosaicked(mosaick_a: xr.Dataset, mosaick_b: xr.Dataset) -> xr.Dataset:
            return xr.combine_by_coords((mosaick_a, mosaick_b), combine_attrs="override")

        datacube = functools.reduce(
            merge_mosaicked, map(lambda datasets: mosaick_list(datasets, lon, lat, lon_step, lat_step),
                                 composition.values()))

        """ ATP: Datacube (single xr.Dataset) """

        # Compute the bands given by the formulas
        for band in dc3_request.bands:
            datacube[band.name] = eval(get_eval_formula(band.dc3__expression, aliases))
            if (band.dc3__min is not None) or (band.dc3__max is not None):
                datacube[band.name] = datacube[band.name].clip(band.dc3__min, band.dc3__max)

        # Keep requested bands
        requested_bands = [band.name for band in dc3_request.bands]
        datacube = datacube[requested_bands]

        # Generate and add metadata to the datacube
        properties = create_datacube_metadata(dc3_request, items, datacube, lon_step, lat_step)
        datacube.attrs = properties.model_dump(exclude_none=True, exclude_unset=True, mode="json")
        datacube.attrs.update({
            "title": dc3_request.title,
            "description": dc3_request.description
        })

        # Chunk the datacube
        cube_file = os.path.join(target_directory, "cube.zarr")
        zipped_cube_file = cube_file + ".zip"
        datacube.chunk(get_chunk_shape(
                    datacube.dims, dc3_request.chunking_strategy)) \
                .to_zarr(cube_file, mode="w") \
                .close()

        AccessManager.zip(cube_file, zipped_cube_file)
        # The zipping of the file adds ane extra ".zip" at the end
        os.rename(zipped_cube_file + ".zip", zipped_cube_file)

        # item.collection, item.catalog and item.id are managed by the process, no need to set it!
        item = Item(
            properties=properties,
            bbox=roi_polygon.bounds,
            geometry=json.loads(to_geojson(roi_polygon)),
            centroid=roi_polygon.centroid.coords[0]
        )

        item.assets = {
            Role.datacube.value: Asset(
                name=Role.datacube.value,
                size=AccessManager.get_size(cube_file),
                type=MimeType.ZARR.value,
                href=zipped_cube_file,  # Could be cube_file but won't work for upload with airs__managed
                asset_type=ResourceType.cube.value,
                asset_format=AssetFormat.zarr.value,
                airs__managed=True,
                title=dc3_request.title,
                description=dc3_request.description,
                roles=[Role.datacube, Role.data, Role.zarr]
            )
        }

        # Create the overview
        if dc3_request.overview:
            overview_file = os.path.join(target_directory, "overview.gif")

            with xr.open_zarr(cube_file) as datacube:
                create_gif(datacube, item, overview_file)

            item.assets[Role.overview.value] = Asset(
                name=Role.overview.value,
                size=AccessManager.get_size(overview_file),
                type=MimeType.GIF.value,
                href=overview_file,
                asset_type=ResourceType.other.value,
                asset_format=AssetFormat.gif.value,
                airs__managed=True,
                title="",
                description="",
                roles=[Role.overview]
            )

        Driver.LOGGER.debug("Cube STAC Item: {}".format(mapper.to_json(item)))
        return item
