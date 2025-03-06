import io
import re
import zipfile
from typing import Pattern

import numpy as np
import rasterio.enums
import rasterio.warp
from rasterio.io import DatasetReader

from extensions.aproc.proc.dc3build.model.dc3build_input import \
    InputDC3BuildProcess


def resample_raster(src: DatasetReader, input_data: np.ndarray, target_resolution: int | float):
    repeats = src.res[0] / target_resolution

    if repeats != 1:
        align_transform, width, height = rasterio.warp.aligned_target(
            src.transform, src.height, src.width, (target_resolution, target_resolution))

        if int(repeats) == repeats:
            repeats = int(repeats)
            height = input_data.shape[len(input_data.shape) - 2]
            width = input_data.shape[len(input_data.shape) - 1]
            data = np.zeros((src.count, height * repeats, width * repeats), dtype=src.dtypes[0])
            for i in range(src.count):
                data[i] = np.repeat(np.repeat(input_data[i], repeats, axis=1), repeats, axis=0)
            transform = align_transform
        else:
            # This method will create some differences with the original image
            data, transform = rasterio.warp.reproject(
                source=input_data,
                destination=np.zeros((src.count, height, width)),
                src_transform=src.transform,
                dst_transform=align_transform,
                src_crs=src.crs,
                dst_crs=src.crs,
                dst_nodata=src.nodata,
                resampling=rasterio.enums.Resampling.nearest)
    else:
        transform = src.transform
        data = input_data

    return data, transform


def find_raster_files(fb: str | io.TextIOWrapper, regex: Pattern[str], alias=None) -> dict[str, str]:
    """
    From a zip archive, extract a dictionary of band -> path matching the input regex.
    The regex must have exactly one capturing group
    """
    bands: dict[str, str] = {}
    with zipfile.ZipFile(fb) as zip:
        file_names = zip.namelist()
        for f_name in file_names:
            matches = re.findall(regex, f_name)
            if len(matches) > 0:
                key = matches[0]
                if alias is not None:
                    key = alias + '.' + key
                bands[key] = f_name

    return bands


def get_eval_formula(band_expression: str,
                     aliases: set[str]) -> str:
    """
    Transform the requested expression of the band in a xarray operation
    """
    def repl(match: re.Match[str]) -> str:
        for m in match.groups():
            return f"datacube.get('{m}')"

    result = band_expression
    for alias in aliases:
        result = re.sub(rf"({alias}\.[a-zA-Z0-9]*)", repl, result)

    return result


def get_all_aliases(request: InputDC3BuildProcess) -> set[str]:
    """
    Get all unique aliases nested in the request's composition
    """
    aliases: set[str] = set()
    for g in request.composition:
        for r in g.dc3__references:
            aliases.add(r.dc3__alias)
    return aliases
