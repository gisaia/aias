import enum
import json
import logging
import os
import re
import tarfile
import tempfile
import zipfile
from typing import Annotated, Literal, Union
from urllib.parse import urlparse

from pydantic import BaseModel, Field, computed_field

from airs.core.models.model import AssetFormat, Item, ItemFormat, Role
from extensions.aproc.proc.download.drivers.driver import \
    Driver as DownloadDriver
from extensions.aproc.proc.download.drivers.exceptions import DriverException
from extensions.aproc.proc.download.drivers.impl.utils import extract


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


class HttpsStorage(BaseModel):
    type: Literal["https"] = "https"
    headers: dict[str, str]
    domain: str


class NoStorage(BaseModel):
    type: Literal[None] = None


Storage = Annotated[Union[GoogleStorage, HttpsStorage, NoStorage], Field(discriminator="type")]

import requests
import contextlib
import warnings
from urllib3.exceptions import InsecureRequestWarning

old_merge_environment_settings = requests.Session.merge_environment_settings


@contextlib.contextmanager
def no_ssl_verification():
    opened_adapters = set()

    def merge_environment_settings(self, url, proxies, stream, verify, cert):
        # Verification happens only once per connection so we need to close
        # all the opened adapters once we're done. Otherwise, the effects of
        # verify=False persist beyond the end of this context manager.
        opened_adapters.add(self.get_adapter(url))

        settings = old_merge_environment_settings(self, url, proxies, stream, verify, cert)
        settings['verify'] = False

        return settings

    requests.Session.merge_environment_settings = merge_environment_settings

    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', InsecureRequestWarning)
            yield
    finally:
        requests.Session.merge_environment_settings = old_merge_environment_settings

        for adapter in opened_adapters:
            try:
                adapter.close()
            except Exception:
                pass


class S3Configuration(BaseModel):
    input: Storage | None = Field(None)

    def get_storage_parameters(self, href: str, LOGGER: logging.Logger) -> dict:
        storage_type = urlparse(href).scheme
        netloc = urlparse(href).netloc

        if not storage_type or storage_type == "file" or storage_type == "http":
            return {}

        if storage_type == "https":
            if self.input.type != "https" or netloc != self.input.domain:
                LOGGER.warning("No headers is configured for this domain. Using no headers")
                return {}
            return {"headers": self.input.headers, "verify": False}

        if storage_type == "gs":
            from google.cloud.storage import Client
            from google.oauth2 import service_account

            if self.input.type != "gs" or netloc != self.input.bucket:
                LOGGER.warning("No api_key is configured for this Google Storage. Using anonymous credentials")
                client = Client.create_anonymous_client()
            else:
                api_key = self.input.api_key
                credentials = service_account.Credentials.from_service_account_info(api_key)
                client = Client("APROC", credentials=credentials)

            return {"client": client}

        raise NotImplementedError(f"Storage '{storage_type}' not compatible")

    def get_rasterio_session(self, href: str, LOGGER: logging.Logger):
        storage_type = urlparse(href).scheme

        if not storage_type or storage_type == "file" or storage_type == "http":
            return None

        if storage_type == "https":
            # TODO: might need some dev here
            return None

        if storage_type == "gs":
            import rasterio.session

            bucket = urlparse(href).netloc

            if self.input.type != "gs" or bucket != self.input.bucket:
                LOGGER.warning("No api_key is configured for this Google Storage bucket. Using anonymous credentials")
                credentials = None
                os.environ["GS_NO_SIGN_REQUEST"] = "YES"
            else:
                os.environ["GS_NO_SIGN_REQUEST"] = "NO"
                with tempfile.NamedTemporaryFile("w+", delete=False) as f:
                    json.dump(self.input.api_key.model_dump(), f)
                    f.close()
                credentials = f.name

            return rasterio.session.GSSession(credentials)

        raise NotImplementedError(f"Storage '{storage_type}' not compatible")


class Configuration(S3Configuration):
    chunk_size: int = Field(1000)


class Driver(DownloadDriver):
    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        Driver.configuration = Configuration.model_validate(configuration)

    # Implements drivers method
    def supports(item: Item) -> bool:
        data = item.assets.get(Role.data.value)
        return item.properties.item_format \
            and item.properties.item_format.lower() == ItemFormat.safe.value.lower() \
            and data is not None and data.href is not None

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

        # asset_href = item.assets.get(Role.data.value).href
        asset_href = "https://geodes-portal.cnes.fr/api/download/URN:FEATURE:DATA:gdh:cf9cceb1-54a5-35ba-9a02-fa0f792445ce:V1/files/17fedb3a7d3098b97bf83649fde0f99a"

        with smart_open.open(asset_href, "rb", transport_params=self.configuration.get_storage_parameters(asset_href, Driver.LOGGER)) as fb:
            print("Opened")
            with open("test.txt", "wb") as f:
                f.write(fb.read(10000))
            with zipfile.ZipFile(fb) as raster_zip:
                file_names = raster_zip.namelist()
                raster_files = list(filter(
                    lambda f: re.match(r".*/IMG_DATA/.*" + r"\.jp2", f) and not re.match(r".*TCI.jp2", f), file_names))

        # Get dimensions of the highest resolution band
        zarr_res = 10
        # TODO: with band selection, it will depend on the highest resolution SELECTED band

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

        archive_path = zarr_path + ".tar"
        with tarfile.open(archive_path, "w") as tar:
            tar.add(zarr_path, arcname=os.path.basename(zarr_path))


if __name__ == "__main__":
    gs = {
        "type": "service_account",
        "project_id": "arlas-184007",
        "private_key_id": "1e4b70b80f73ed52c7a612b17a22af9ab83b7fea",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCXCi46nVGNcvBI\niRuV3DK3iIu0vjkoX5h9VaJAiC+yYWCx+4atyvW8n3dZItzPLE0ijvnnKHYl8Qdm\n2OevldtBlMUDf2tLUNHYsAIydh9aphfya6OsALYJo6d2j7Y9gqKUh6w5X1RnkA+9\nCQmiORPNb1WW2BmL8CWDy0fBieVunsRTqvjQX8IyGQvdi6pEOrr4uaBef42UIE+o\nHtTZrnQNNHXra633txU23rserVj9citjmmKkzQJYZ5HdfRb+Fncs89lsZQ0bfnsx\nOxf7np9CK4qIyF2/aNdo8uIudyTze07X+1zOzX0v7iLVVoDGSEfeq08RUg0jE97T\nt2kglUXjAgMBAAECggEAJun7kSR5H31uhPG2Rr0N4BVxESc1aL6AdkI65G9yAn5u\nQEzynRI+j9NyF2gRBdt/IBlAL5tQHWRlKM1Xm/h7HgFrZQROK4BuIGrwlfmzCFLk\ntpOe/rDMNd2RRs2uAVkH9EakS7/Q6kHGnEiYz8/u1y4JGi0hH9nGgJc+LJIPp5kg\nknQKL+5hYHhDjwMFC2dmgc9kT5S2rF9eLhZtFxi1Se76X7KlebX+5+n7VFSdy6cP\nNHBv4EE7VCOZM/nhzv5obQLGGVtGdE5sWdy6mp2zl9U9q8s+d/8h637+NSoJ927n\ngdNEsy0+EB8hQS0IUf3RxABybYxII82b/9d3iUCZAQKBgQC2HkIh6XoBKrpplodV\nUTPbNlSFwzi+UbUSsL+cuTccgidvAToxzMvdIZJxSAuTpuRjGNBA4qhfMX8WaTvr\nbssgsvUuzIElkKt7z5Kup8qG6jlftLMxdzAYIWxtntic/oIyf32T7UwzeMAInREY\nle+wkAI8ubyM9OT720L28/BeYwKBgQDUUEvqv6a1U5OEMWsYSD4EclwJHFhY9C9+\ncQCnrSbYJcDtZzLY0D8gxC+wu+c5Jt+cTSkBzYcWJT3SDBg1FT3p4mSgCjn+YbVY\n3BHWLlRq+usQarJ7yOcDb3oOy5/RXHd3dFyDPOYTxAyXDdR+HKJW9w4Cd93yUGQb\nJttXMP5SgQKBgQC0VvhD3pBbEXWw00fGO3fvTjiakLvi8sQs8ut7hYlGaLgl2wBG\nijciDXmXRbF5D92/J7YpWolCYqAnkCOuunLZOX1DT21fxoeZPe5Rl4Qc31nbJPQB\nOrZcXtShJJf5tqk02jx/PI+ltJ/sp6RjRS4qGCCvA3nr1yHdKL2CEANpYwKBgQCD\nH3Azc9empw41Fzw4C+3ZWzOCIPJjRbPLWEj6RZL27SIgvJqHkt1aBDAb64CbKGnz\noyfPSDrEr41lmzicGBlbyAkzWf2FIJ0aWxfc+lICnCLuyaafkm0yDvgICTQT3hKe\nQMwd9U93J55K8CyrEk4kfYI2fgch7wpURoQybjyzgQKBgQCNNWTUISjOQoWjU/vS\nEL1LRJ/YgilJd7+aobHzm9qtosZOLuHKOVAyq/H6ur/F+ct1WJXf6GbYC7CLxelF\nfIpyIBqpilWx8Jo//bwCfZGsOes9jUm61i1/C7fogASmmSzwbmQtZ5v/rzdB9o97\nPQg0yS5UIFGmmIzyeoTj+Xpn0Q==\n-----END PRIVATE KEY-----\n",
        "client_email": "arlas-184007@appspot.gserviceaccount.com",
        "client_id": "",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/arlas-184007%40appspot.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }

    conf = {
        "tmp_folder": "/tmp/",
        "input": {
            "type": "gs",
            "bucket": "gisaia-public",
            "api_key": gs
        }
    }

    token = ""

    conf = {
        "input": {
            "type": "https",
            "headers": {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json, text/plain, /",
                "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8,en-US;q=0.7",
                "Referer": "https://geodes-portal.cnes.fr/search?dataType=Sentinel-2&satellitePlatform=S2A&startDate=2024-11-06T11:49&box=-20037508.342789244,-8988179.198035019,20037508.342789244,8988179.198035019",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin"
            },
            "domain": "geodes-portal.cnes.fr"
        }
    }

    Driver.init(conf)
    driver = Driver()

    # crop_wkt = "POLYGON ((0.087547 42.794645, 0.087547 42.832926, 0.176811 42.832926, 0.176811 42.794645, 0.087547 42.794645))"
    import logging

    logging.basicConfig(level=logging.DEBUG)
    asset_href = "https://geodes-portal.cnes.fr/api/download/URN:FEATURE:DATA:gdh:cf9cceb1-54a5-35ba-9a02-fa0f792445ce:V1/files/17fedb3a7d3098b97bf83649fde0f99a"

    import time

    start_time = time.time()
    print(f"Starting: {start_time}")
    with no_ssl_verification():
        r = requests.get(asset_href, headers=conf["input"]["headers"])
        print(r.content)
        # driver.fetch_and_transform({}, "outbox", "", "EPSG:4326", "ZARR", False)
    print(f"Duration: {time.time() - start_time}")
