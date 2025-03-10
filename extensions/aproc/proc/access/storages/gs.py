import enum
import json
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
    is_local: Literal[False] = False
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
                json.dump(self.api_key.model_dump(exclude_none=True, exclude_unset=True), f)
                f.close()
            credentials = f.name
        else:
            credentials = None
        return credentials

    def get_storage_parameters(self):
        if self.is_anon_client:
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

    def __get_blob(self, href: str):
        bucket = self.__get_bucket()
        return bucket.get_blob(urlparse(href).path[1:] or "/")

    def exists(self, href: str):
        return self.is_file(href) or self.is_dir(href)

    def get_rasterio_session(self):
        import rasterio.session

        params = {
            "session": rasterio.session.GSSession(self.credentials_file),
        }

        if self.api_key is None:
            params["GS_NO_SIGN_REQUEST"] = "YES"
        else:
            params["GS_NO_SIGN_REQUEST"] = "NO"

        return params

    def pull(self, href: str, dst: str):
        super().pull(href, dst)

        blob = self.__get_blob(href)
        if blob is None:
            raise LookupError(f"Can't find {href}")

        blob.download_to_filename(dst)

    def is_file(self, href: str):
        prefix = urlparse(href).path.removeprefix("/")
        files, dirs = self.__list_blobs(prefix=prefix)

        return len(files) > 0 and files[0] == prefix and len(dirs) == 0

    def __list_blobs(self, prefix: str) -> tuple[list[str], list[str]]:
        """
        Return a list of files contained in the specified folder, as well as subfolders
        """
        # If requesting the root folder, prefix needs to be empty
        if prefix == "/":
            prefix = ""
        blobs = self.__get_bucket().list_blobs(prefix=prefix, delimiter="/")
        return list(map(lambda b: b.name, blobs)), list(blobs.prefixes)

    def is_dir(self, href: str):
        prefix = urlparse(href).path.removeprefix("/").removesuffix("/") + "/"
        files, dirs = self.__list_blobs(prefix)

        return len(files) > 0 or len(dirs) > 0

    def get_file_size(self, href: str):
        return self.__get_blob(href).size

    def listdir(self, href: str):
        prefix = urlparse(href).path.removeprefix("/").removesuffix("/") + "/"
        files, dirs = self.__list_blobs(prefix)

        return list(map(lambda b: b.split(prefix)[1], files)) + \
            list(map(lambda b: b.split(prefix)[1].strip("/"), dirs))

    def get_last_modification_time(self, href: str):
        blob = self.__get_blob(href)
        if blob:
            mod_time = blob.updated
            return mod_time.timestamp() if mod_time is not None else 0
        return 0

    def get_creation_time(self, href: str):
        blob = self.__get_blob(href)
        if blob:
            creation_time = blob.time_created
            return creation_time.timestamp() if creation_time is not None else 0
        return 0

    def makedir(self, href: str, strict=False):
        if strict:
            raise NotImplementedError("It is not possible to create the folder on Google Storage")

    def clean(self, href: str):
        raise NotImplementedError("It is not possible to delete a file on Google Storage")
