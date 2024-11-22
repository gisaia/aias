import io
import os
import re
import shutil
import tarfile
import tempfile
import zipfile

import requests
from pydantic import Field

from airs.core.models.model import AssetFormat, Item, ItemFormat
from extensions.aproc.proc.download.drivers.driver import \
    Driver as DownloadDriver
from extensions.aproc.proc.download.drivers.exceptions import DriverException
from extensions.aproc.proc.download.drivers.impl.utils import extract
from extensions.aproc.proc.s3_configuration import S3Configuration


class ZarrConfiguration(S3Configuration):
    chunk_size: int = Field(1000)


class Driver(DownloadDriver):
    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        Driver.configuration = ZarrConfiguration.model_validate(configuration)

    # Implements drivers method
    def supports(item: Item) -> bool:
        href = Driver.get_asset_href(item)
        return item.properties.item_format \
            and item.properties.item_format.lower() == ItemFormat.safe.value.lower() \
            and href is not None

    # Implements drivers method
    def fetch_and_transform(self, item: Item, target_directory: str, crop_wkt: str, target_projection: str, target_format: str, raw_archive: bool):
        if raw_archive is True:
            raise DriverException("Raw archive can't be returned for a zarr download.")
        if target_format != AssetFormat.zarr.value:
            raise DriverException(f"Target format must be {AssetFormat.zarr.value}")
        if target_projection == 'native':
            target_projection = item.properties.proj__epsg

        import numpy as np
        import rasterio
        import rasterio.enums
        import rasterio.warp
        import rioxarray
        import smart_open
        import xarray as xr

        asset_href = Driver.get_asset_href(item)
        tmp_asset = None

        if self.configuration.is_download_required(asset_href):
            from urllib.parse import urlparse

            Driver.LOGGER.info("Downloading archive for Zarr creation.")

            requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
            r = requests.get(asset_href, headers=self.configuration.get_storage_parameters(asset_href, Driver.LOGGER)["headers"],
                             stream=True, verify=False)

            tmp_asset = os.path.join(tempfile.gettempdir(), urlparse(asset_href).path.strip("/").split("/")[-1])
            if (os.path.splitext(tmp_asset)[1] != ".zip"):
                tmp_asset = os.path.splitext(tmp_asset)[0] + ".zip"

            Driver.LOGGER.warning(tmp_asset)
            with open(tmp_asset, "wb") as out_file:
                shutil.copyfileobj(r.raw, out_file)

            raster_files = self.__find_raster_files(tmp_asset)
            asset_href = f"file://{tmp_asset}"
        else:
            Driver.LOGGER.info("Streaming archive for Zarr creation.")
            with smart_open.open(asset_href, "rb", transport_params=self.configuration.get_storage_parameters(asset_href, Driver.LOGGER)) as fb:
                raster_files = self.__find_raster_files(fb)

        zarr_res = self.__get_zarr_resolution()

        session = self.configuration.get_rasterio_session(asset_href, Driver.LOGGER)
        with rasterio.Env(session):
            tmp_files = [tempfile.NamedTemporaryFile("w+", suffix=".jp2", delete=False).name for _ in raster_files]

            for ri, rf in enumerate(raster_files):
                with rasterio.open("zip+" + asset_href + "!" + rf) as src:
                    repeats = src.res[0] / zarr_res

                    if repeats != 1:
                        align_transform, width, height = rasterio.warp.aligned_target(
                            src.transform, src.height, src.width, (zarr_res, zarr_res))

                        if int(repeats) == repeats:
                            repeats = int(repeats)
                            data = np.zeros((src.count, src.height * repeats, src.width * repeats), dtype=src.dtypes[0])
                            for i in range(src.count):
                                data[i] = np.repeat(np.repeat(src.read()[i], repeats, axis=1), repeats, axis=0)
                            transform = align_transform
                        else:
                            # This method will create some differences with the original image
                            data, transform = rasterio.warp.reproject(
                                source=src.read(),
                                destination=np.zeros((src.count, height, width)),
                                src_transform=src.transform,
                                dst_transform=align_transform,
                                src_crs=src.crs,
                                dst_crs=src.crs,
                                dst_nodata=src.nodata,
                                resampling=rasterio.enums.Resampling.nearest)
                    else:
                        transform, _, _ = src.transform, src.width, src.height
                        data = src.read()

                    profile = src.profile
                    profile.update(transform=transform, driver="JP2OpenJPEG",
                                   height=data.shape[1], width=data.shape[2])

                    temporary_raster = tempfile.NamedTemporaryFile("w+", suffix=".jp2", delete=False)
                    with rasterio.open(temporary_raster.name, "w", **profile, quality=100, reversible=True) as dst:
                        dst.write(data)

                    extract([], crop_wkt, temporary_raster.name, "JP2OpenJPEG",
                            target_projection, "/".join(tmp_files[ri].split("/")[:-1]),
                            tmp_files[ri].split("/")[-1])
                os.remove(temporary_raster.name)

        zarr_name = os.path.splitext(os.path.basename(asset_href))[0] + "." + target_format
        band_names = map(lambda x: x.split("/")[-1][-7:-4], raster_files)

        chunk_size = self.configuration.chunk_size
        zarr_path = target_directory + "/" + zarr_name
        bands: xr.Dataset = None
        for b, r in zip(band_names, tmp_files):
            da = rioxarray.open_rasterio(r, default_name=b, chunks=(1, chunk_size, chunk_size), driver="JP2OpenJPEg")
            if bands is None:
                bands = da
            else:
                bands = xr.merge([bands, da])
        bands \
            .squeeze("band").drop_vars("band") \
            .chunk(chunk_size) \
            .to_zarr(zarr_path, mode="w", consolidated=True) \
            .close()

        for f in tmp_files:
            os.remove(f)
        if tmp_asset:
            os.remove(tmp_asset)

        archive_path = zarr_path + ".tar"
        with tarfile.open(archive_path, "w") as tar:
            tar.add(zarr_path, arcname=os.path.basename(zarr_path))

    def __find_raster_files(self, fb: str | io.TextIOWrapper):
        with zipfile.ZipFile(fb) as raster_zip:
            file_names = raster_zip.namelist()
            raster_files = list(filter(
                lambda f: re.match(r".*/IMG_DATA/.*" + r"\.jp2", f) and not re.match(r".*TCI.jp2", f), file_names))

        return raster_files

    def __get_zarr_resolution(self):
        # TODO: with band selection, it will depend on the highest resolution SELECTED band
        return 10
