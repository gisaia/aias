import numpy as np
import rasterio.warp
from rasterio.io import DatasetReader


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
