import enum
import json
import re
import tempfile
import zipfile
from typing import Annotated, Literal, Union
from urllib.parse import urlparse

from pydantic import BaseModel, Field, computed_field

from airs.core.models.model import AssetFormat, Item, Role
from extensions.aproc.proc.download.drivers.driver import \
    Driver as DownloadDriver
from extensions.aproc.proc.download.drivers.exceptions import DriverException
from extensions.aproc.proc.download.drivers.impl.utils import (extract,
                                                               get_file_name)


class GoogleStorageConstants(str, enum.Enum):
    AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
    TOKEN_URI = "https://oauth2.googleapis.com/token"
    AUTH_PROVIDER_CERT_URL = "https://www.googleapis.com/oauth2/v1/certs"


class GoogleStorageApiKey(BaseModel):
    type: Literal["service_account"] = "service_account"
    project_id: str
    private_key_id: str
    private_key: str
    client_id: str | None = Field(None)
    auth_uri: Literal[GoogleStorageConstants.AUTH_URI] = GoogleStorageConstants.AUTH_URI.value
    token_uri: Literal[GoogleStorageConstants.TOKEN_URI] = GoogleStorageConstants.TOKEN_URI.value
    auth_provider_x509_cert_url: Literal[GoogleStorageConstants.AUTH_PROVIDER_CERT_URL] = GoogleStorageConstants.AUTH_PROVIDER_CERT_URL.value
    universe_domain: Literal["googleapis.com"] = "googleapis.com"

    @computed_field
    @property
    def client_x509_cert_url(self) -> str:
        return f"https://www.googleapis.com/robot/v1/metadata/x509/{self.project_id}%40appspot.gserviceaccount.com"

    @computed_field
    @property
    def client_email(self) -> str:
        return f"{self.project_id}@appspot.gserviceaccount.com"


class GoogleStorage(BaseModel):
    type: Literal["gs"] = "gs"
    bucket: str
    api_key: GoogleStorageApiKey


Storage = Annotated[Union[GoogleStorage], Field(discriminator="type")]


class Configuration(BaseModel):
    input: Storage


class Driver(DownloadDriver):
    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        Driver.configuration = Configuration.model_validate(configuration)

    # Implements drivers method
    def supports(item: Item) -> bool:
        data = item.assets.get(Role.data.value)
        return item.properties.constellation == "Sentinel-2" \
            and item.properties.processing__level == "L1C" \
            and data is not None and data.href is not None and (
                data.href.startswith("s3://")
                or data.href.startswith("gs://")
                or data.href.startswith("file://")
                or data.href.startswith("http://")
                or data.href.startswith("https://"))

    # Implements drivers method
    def fetch_and_transform(self, item: Item, target_directory: str, crop_wkt: str, target_projection: str, target_format: str, raw_archive: bool):
        if raw_archive is False:
            raise DriverException("Raw archive can't be returned for a zarr download.")
        if target_format != AssetFormat.zarr.value:
            raise DriverException(f"Target format must be {Role.zarr.value}")

        import rasterio
        import rioxarray
        import smart_open
        import xarray as xr

        asset_href = item.assets.get(Role.data.value).href

        with smart_open.open(asset_href, "rb", transport_params=self.__get_storage_parameters(asset_href, self.configuration)) as fb:
            with zipfile.ZipFile(fb) as raster_zip:
                file_names = raster_zip.namelist()
                raster_files = list(filter(lambda f: re.match(r".*/IMG_DATA/.*" + r"\.jp2", f) and not re.match(r".*TCI.jp2", f), file_names))

        session = self.__get_rasterio_session(asset_href)

        with rasterio.Env(session):
            # Get dimensions of the highest resolution band
            zarr_res = 10
            # TODO: with band selection, it will depend on the highest resolution SELECTED band

            tmp_files = [tempfile.NamedTemporaryFile("w+", suffix=".jp2", delete=False).name for _ in raster_files]
            for i, rf in enumerate(raster_files):
                with rasterio.open("zip+" + asset_href + "!" + rf) as src:
                    repeats = src.res[0] / zarr_res

                    if repeats != 1:
                        import numpy as np
                        import rasterio.warp

                        align_transform, width, height = rasterio.warp.aligned_target(
                            src.transform, src.height, src.width, (zarr_res, zarr_res))
                        if int(repeats) == repeats:
                            repeats = int(repeats)
                            data = np.zeros((1, src.height * repeats, src.width * repeats))
                            data[0] = np.repeat(np.repeat(src.read()[0], repeats, axis=1), repeats, axis=0)
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
                        transform, width, height = src.transform, src.width, src.height
                        data = src.read()

                    profile = src.profile
                    profile.update(transform=transform, driver="JP2OpenJPEG",
                                   height=data.shape[1], width=data.shape[2])

                    temporary_raster = tempfile.NamedTemporaryFile("w+", suffix=".jp2", delete=False)
                    with rasterio.open(temporary_raster.name, "w", **profile, quality=100, reversible=True) as dst:
                        dst.write(data)

                extract([], crop_wkt, temporary_raster.name, "JP2OpenJPEG",
                        target_projection, "/".join(tmp_files[i].split("/")[:-1]),
                        tmp_files[i].split("/")[-1])
                temporary_raster.delete = True
                temporary_raster.close()

        zarr_name = get_file_name(item, target_format)
        band_names = map(lambda x: x.split("/")[-1][-7:-4], raster_files)
        bands: xr.Dataset = None

        for b, r in zip(band_names, tmp_files):
            da = rioxarray.open_rasterio(r, default_name=b)
            if bands is None:
                bands = da
            else:
                bands = xr.merge([bands, da])
        bands.to_zarr(target_directory + "/" + zarr_name, mode="w").close()

    def __get_rasterio_session(self, href: str):
        storage_type = urlparse(href).scheme

        if not storage_type or storage_type == "file":
            return None
        if storage_type == "gs":
            import rasterio.session

            if self.configuration.input.type != "gs":
                raise
            api_key = self.configuration.input.api_key

            with tempfile.NamedTemporaryFile("w+", delete=False) as f:
                json.dump(api_key.model_dump(), f)
                f.close()
            return rasterio.session.GSSession(f.name)
        else:
            raise NotImplementedError(f"Storage '{storage_type}' not compatible")

    def __get_storage_parameters(self, href: str) -> dict:
        storage_type = urlparse(href).scheme

        if not storage_type or storage_type == "file":
            return {}
        if storage_type == "gs":
            from google.cloud.storage import Client
            from google.oauth2 import service_account

            if self.configuration.input.type != "gs":
                raise
            api_key = self.configuration.input.api_key

            credentials = service_account.Credentials.from_service_account_info(api_key)
            client = Client("APROC", credentials=credentials)
            return {"client": client}
        else:
            raise NotImplementedError(f"Storage '{storage_type}' not compatible")
