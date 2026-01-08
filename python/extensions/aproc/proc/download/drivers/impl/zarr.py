import io
import os
import re
import tarfile
import tempfile
from typing import Any

from pydantic import BaseModel, Field

from airs.core.models.model import AssetFormat, Item, ItemFormat, MimeType, Role
from aias_common.access.manager import AccessManager
from extensions.aproc.proc.download.drivers.download_driver import \
    DownloadDriver
from extensions.aproc.proc.download.drivers.impl.utils import extract
from extensions.aproc.proc.drivers.exceptions import DriverException


class ZarrConfiguration(BaseModel):
    chunk_size: int = Field(default=1000)


class Driver(DownloadDriver):
    configuration: ZarrConfiguration

    def __init__(self):
        super().__init__()

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        DownloadDriver.init(configuration)
        Driver.configuration = ZarrConfiguration.model_validate(configuration)

    # Implements drivers method
    def supports(self, resource: Item, extra_params: dict[str, Any] = {}) -> bool:
        # Supports only zarr target format for s2 items
        if extra_params.get("target_format", "").lower() == AssetFormat.zarr.value.lower():                
            href = self.get_asset_href(resource)
            return resource.properties is not None and resource.properties.item_format is not None \
                and resource.properties.item_format.lower() == ItemFormat.safe.value.lower() \
                and href is not None
        return False

    # Implements drivers method
    def fetch_and_transform(self, item: Item, target_directory: str, crop_wkt: str, target_projection: str, target_format: str, raw_archive: bool):
        if raw_archive is True:
            raise DriverException("Raw archive can't be returned for a zarr download.")
        if target_format.lower() != AssetFormat.zarr.value.lower():
            raise DriverException(f"Target format must be {AssetFormat.zarr.value}")
        if target_projection == 'native' and item.properties:
            if item.properties.proj__epsg:
                target_projection = str(item.properties.proj__epsg)
            else:
                raise DriverException("Item has no EPSG code defined for native projection.")

        import rasterio
        import rioxarray
        import xarray as xr

        asset_href = self.get_asset_href(item)
        tmp_asset = None
        is_asset_zip = item.assets.get(Role.data.value).type == MimeType.ZIP.value

        # Downloading all bands one by one is heavily discouraged
        if is_asset_zip and AccessManager.is_download_required(asset_href):
            self.LOGGER.info("Downloading archive for Zarr creation.")

            # Create tmp file where data will be downloaded
            tmp_asset = os.path.join(AccessManager.tmp_dir, os.path.basename(asset_href))
            if (os.path.splitext(tmp_asset)[1] != ".zip"):
                tmp_asset = os.path.splitext(tmp_asset)[0] + ".zip"

            # Download archive then extract it
            AccessManager.pull(asset_href, tmp_asset)
            raster_files = self.__find_raster_files_in_zip(tmp_asset)

            asset_href = f"file://{tmp_asset}"
        else:
            if is_asset_zip:
                self.LOGGER.info("Streaming archive for Zarr creation.")
                with AccessManager.stream(asset_href) as fb:
                    raster_files = self.__find_raster_files_in_zip(fb)
            else:
                raster_files = self.__find_all_bands_but_main(item)

        with rasterio.Env(**AccessManager.get_rasterio_session(asset_href)):
            tmp_files = [tempfile.NamedTemporaryFile("w+", suffix=".jp2", delete=False).name for _ in raster_files]

            for ri, rf in enumerate(raster_files):
                if is_asset_zip:
                    href = "zip+" + asset_href + "!" + rf
                else:
                    href = rf
                self.__transform_band(href, crop_wkt, target_projection, tmp_files[ri])

        zarr_name = os.path.splitext(os.path.basename(asset_href))[0] + "." + target_format
        band_names = map(lambda x: x.split("/")[-1][-7:-4], raster_files)

        chunk_size = Driver.configuration.chunk_size
        zarr_path = target_directory + "/" + zarr_name
        bands: xr.Dataset = None
        for b, r in zip(band_names, tmp_files):
            with rioxarray.open_rasterio(r, default_name=b, chunks=(1, chunk_size, chunk_size), driver="JP2OpenJPEg") as da:
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
            os.remove(f)  # !DELETE!
        if tmp_asset:
            os.remove(tmp_asset)  # !DELETE!

        archive_path = zarr_path + ".tar"
        with tarfile.open(archive_path, "w") as tar:
            tar.add(zarr_path, arcname=os.path.basename(zarr_path))

    def __transform_band(self, input_band: str, crop_wkt: str, target_projection: str, target_path: str):
        import rasterio

        from extensions.aproc.proc.dc3build.utils.raster import resample_raster

        target_directory = os.path.dirname(target_path)
        target_file = os.path.basename(target_path)

        with rasterio.open(input_band) as src:
            # In case no projection is defined, get the one of any of the band
            if target_projection is None:
                target_projection = src.crs

            data, transform = resample_raster(src, src.read(), self.__get_zarr_resolution())

            profile = src.profile
            profile.update(transform=transform, driver="JP2OpenJPEG",
                           height=data.shape[1], width=data.shape[2])

            temporary_raster = tempfile.NamedTemporaryFile("w+", suffix=".jp2", delete=False)
            with rasterio.open(temporary_raster.name, "w", **profile, quality=100, reversible=True) as dst:
                dst.write(data)

            extract([], crop_wkt, temporary_raster.name, "JP2OpenJPEG",
                    target_projection, target_directory, target_file)
        os.remove(temporary_raster.name)  # !DELETE!

    def __find_raster_files_in_zip(self, fb: str | io.TextIOWrapper):
        from extensions.aproc.proc.dc3build.utils.raster import \
            find_raster_files

        return list(find_raster_files(fb, re.compile(r"IMG_DATA/.*(B\d{2})\.jp2")).values())

    def __get_zarr_resolution(self):
        # TODO: with band selection, it will depend on the highest resolution SELECTED band
        return 10

    def __find_all_bands_but_main(self, item: Item):
        raster_files = []
        # Get all the assets that are not the main one
        for a in item.assets.values():
            try:
                if a.roles.index(Role.data.value) >= 0 and a.name != Role.data.value:
                    raster_files.append(a.href)
            except Exception:
                ...

        return raster_files
