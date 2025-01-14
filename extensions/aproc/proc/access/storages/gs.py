import enum
import json
import os
import tempfile
from typing import Literal
from urllib.parse import urlparse

from google.cloud.storage import Client
from google.oauth2 import service_account
from pydantic import BaseModel, Field, computed_field

from aproc.core.logger import Logger
from extensions.aproc.proc.access.storages.abstract import AbstractStorage

LOGGER = Logger.logger


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


class GoogleStorage(AbstractStorage):
    type: Literal["gs"] = "gs"
    bucket: str
    api_key: GoogleStorageApiKey | None = Field(default=None)

    @computed_field
    @property
    def is_anon_client(self) -> bool:
        return self.api_key is None

    @computed_field
    @property
    def credentials_file(self) -> str:
        if not self.is_anon_client:
            with tempfile.NamedTemporaryFile("w+", delete=False) as f:
                json.dump(self.api_key.model_dump(), f)
                f.close()
            credentials = f.name
        else:
            credentials = None
        return credentials

    def get_storage_parameters(self):
        if self.is_anon_client:
            LOGGER.warning("No api_key is configured for this Google Storage. Using anonymous credentials")
            client = Client.create_anonymous_client()
        else:
            credentials = service_account.Credentials.from_service_account_info(self.api_key)
            client = Client("APROC", credentials=credentials)

        return {"client": client}

    def supports(self, href: str):
        scheme = urlparse(href).scheme
        netloc = urlparse(href).netloc

        return scheme == "gs" and netloc == self.bucket

    def __get_bucket(self):
        client = self.get_storage_parameters()["client"]

        if self.is_anon_client:
            return client.bucket(self.bucket)
        else:
            # Try to retrieve a bucket (this makes an API request)
            return client.get_bucket(self.bucket)

    def exists(self, href: str):
        bucket = self.__get_bucket()
        return bucket.blob(href).exists()

    def get_rasterio_session(self):
        import rasterio.session

        params = {
            "session": rasterio.session.GSSession(self.credentials_file),
        }

        if self.api_key is None:
            LOGGER.warning("No api_key is configured for this Google Storage bucket. Using anonymous credentials")
            params["GS_NO_SIGN_REQUEST"] = "YES"
        else:
            params["GS_NO_SIGN_REQUEST"] = "NO"

        return params

    def pull(self, href: str, dst: str, is_dst_dir: bool):
        super().pull(href, dst, is_dst_dir)

        bucket = self.__get_bucket()
        blob = bucket.blob(urlparse(href).path[1:])

        if is_dst_dir:
            # If it is a directory, then add filename at the end of the path to match shutil.copy behaviour
            dst = os.path.join(dst, os.path.basename(href))
        blob.download_to_filename(dst)

    def is_file(self, href: str):
        return self.exists(href)

    def is_dir(self, href: str):
        # Does not handle empty folders
        blobs = list(self.__get_bucket().list_blobs(prefix=href.removesuffix("/") + "/"))
        return len(blobs) > 1
