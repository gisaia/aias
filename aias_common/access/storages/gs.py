import json
import os
import tempfile
from urllib.parse import urlparse, urlunparse

from google.cloud.storage import Client
from google.oauth2 import service_account

from aias_common.access.configuration import GoogleStorageConfiguration
from aias_common.access.file import File
from aias_common.access.storages.abstract import AbstractStorage


class GoogleStorage(AbstractStorage):

    def get_configuration(self) -> GoogleStorageConfiguration:
        assert isinstance(self.storage_configuration, GoogleStorageConfiguration)
        return self.storage_configuration

    def get_storage_parameters(self):
        if self.get_configuration().is_anon_client:
            client = Client.create_anonymous_client()
        else:
            credentials = service_account.Credentials.from_service_account_info(self.get_configuration().api_key)
            client = Client("APROC", credentials=credentials)

        return {"client": client}

    def supports(self, href: str):
        scheme = urlparse(href).scheme
        netloc = urlparse(href).netloc

        return scheme == "gs" and netloc == self.get_configuration().bucket

    def __get_bucket(self):
        client = self.get_storage_parameters()["client"]

        if self.get_configuration().is_anon_client:
            return client.bucket(self.get_configuration().bucket)
        else:
            # Try to retrieve a bucket (this makes an API request)
            return client.get_bucket(self.get_configuration().bucket)

    def __get_blob(self, href: str):
        bucket = self.__get_bucket()
        return bucket.get_blob(urlparse(href).path[1:] or "/")

    def exists(self, href: str):
        return self.is_file(href) or self.is_dir(href)

    def get_rasterio_session(self):
        import rasterio.session

        params = {
            "session": rasterio.session.GSSession(self.get_configuration().credentials_file),
        }

        if self.get_configuration().api_key is None:
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

    def __list_blobs(self, source: str) -> list[File]:
        """
        Return a list of files contained in the specified folder, as well as subfolders
        """
        url = urlparse(source)
        blobs = self.__get_bucket().list_blobs(prefix=url.path.removeprefix("/"), delimiter="/")
        files = list(map(lambda b: File(name=os.path.basename(b.name), path=self.__update_url__(source=source, path=b.name), is_dir=False, last_modification_date=b.updated, creattion_date=b.time_created), blobs))
        dirs = list(map(lambda b: File(name=os.path.basename(b.removesuffix("/")), path=self.__update_url__(source=source, path=b).removesuffix("/") + "/", is_dir=True), blobs.prefixes))
        return files + dirs

    def __update_url__(self, source: str, path: str):
        url = urlparse(source)
        components = list(url[:])
        if len(components) == 5:
            components.append('')
        components[2] = path
        return urlunparse(tuple(components))

    def is_file(self, href: str):
        files = self.__list_blobs(href)
        return len(list(filter(lambda f: f.path == href and not f.is_dir, files))) == 1

    def is_dir(self, href: str):
        files = self.__list_blobs(href)
        return len(list(filter(lambda f: os.path.dirname(f.path).removesuffix("/") == href.removesuffix("/") and (f.is_dir or os.path.basename(f.path)), files))) > 0

    def get_file_size(self, href: str):
        return self.__get_blob(href).size

    def listdir(self, href: str) -> list[File]:
        return self.__list_blobs(href.removesuffix("/") + "/")

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
            raise PermissionError("Creating a folder on a remote storage is not permitted")

    def clean(self, href: str):
        raise PermissionError("Deleting files on a remote storage is not permitted")
