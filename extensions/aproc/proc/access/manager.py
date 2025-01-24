from contextlib import contextmanager
import os
import shutil
import tempfile
from typing import Annotated, Union

from pydantic import Field

from aproc.core.logger import Logger
from aproc.core.settings import Configuration
from extensions.aproc.proc.access.storages.file import AccessType, FileStorage
from extensions.aproc.proc.access.storages.gs import GoogleStorage
from extensions.aproc.proc.access.storages.http import HttpStorage
from extensions.aproc.proc.access.storages.https import HttpsStorage

AnyStorage = Annotated[Union[FileStorage, GoogleStorage, HttpStorage, HttpsStorage], Field(discriminator="type")]

LOGGER = Logger.logger


class AccessManager:
    storages: list[AnyStorage]
    tmp_dir = tempfile.gettempdir()

    @staticmethod
    def init():
        LOGGER.info("Initializing APROC storages")
        AccessManager.storages = []

        for s in Configuration.settings.storages:
            match s.type:
                case "file":
                    AccessManager.storages.append(FileStorage(**s.model_dump()))
                case "gs":
                    AccessManager.storages.append(GoogleStorage(**s.model_dump()))
                case "http":
                    AccessManager.storages.append(HttpStorage(**s.model_dump()))
                case "https":
                    AccessManager.storages.append(HttpsStorage(**s.model_dump()))
                case _:
                    raise NotImplementedError(f"Specified storage {s.type} is not implemented")

    @staticmethod
    def resolve_storage(href: str) -> AnyStorage:
        """
        Based on the defined storages, returns the one matching the input href
        """

        for s in AccessManager.storages:
            try:
                if s.supports(href):
                    return s
            except Exception:
                ...
        raise NotImplementedError(f"Storage for {href} is not configured")

    @staticmethod
    def get_storage_parameters(href: str):
        storage = AccessManager.resolve_storage(href)

        return storage.get_storage_parameters()

    @staticmethod
    def pull(href: str, dst: str):
        """
        Pulls a file from a storage to write it in the local storage.
        If the input storage is local, then it is a copy. Otherwise it is a download.
        """
        storage = AccessManager.resolve_storage(href)

        # Check that the destination is an authorized path for at least one of the file storages
        is_dst_authorized = any(map(lambda s: s.is_path_authorized(dst, AccessType.WRITE), filter(lambda s: s.type == "file", AccessManager.storages)))
        if not is_dst_authorized:
            raise ValueError("Destination path is not authorized")

        storage.pull(href, dst)

    # Will return a yield
    @staticmethod
    @contextmanager
    def stream(href: str):
        """
        Reads the content of a file in a storage without downloading it.
        """
        import smart_open

        with smart_open.open(href, "rb", transport_params=AccessManager.get_storage_parameters(href)) as f:
            yield f

    @staticmethod
    def get_rasterio_session(href: str):
        storage = AccessManager.resolve_storage(href)

        return storage.get_rasterio_session()

    @staticmethod
    def exists(href: str) -> bool:
        """
        Whether the file exists
        """
        storage = AccessManager.resolve_storage(href)

        return storage.exists(href)

    @staticmethod
    def is_download_required(href: str):
        storage = AccessManager.resolve_storage(href)

        return storage.type in ["http", "https"] \
            and storage.force_download

    @staticmethod
    def prepare(href: str, dst: str | None = None):
        """Prepare the file to be processed locally

        Args:
            href (str): Href (local or not) of the file

        Returns:
            str: The local path at which the file can be found
        """
        storage = AccessManager.resolve_storage(href)

        # If the storage is not local, pull it
        if storage.type != "file":
            if dst is None:
                dst = os.path.join(AccessManager.tmp_dir, os.path.basename(href))

            AccessManager.pull(href, dst)
            return dst

        return href

    @staticmethod
    def zip(href: str, zip_path: str):
        # For all storages but FileStorage, files need to be pulled before being processed
        href = AccessManager.prepare(href)

        # Get direct parent folder of href_file to zip
        dir_name = os.path.dirname(href)
        shutil.make_archive(zip_path, 'zip', dir_name)

    @staticmethod
    def is_file(href: str):
        storage = AccessManager.resolve_storage(href)

        return storage.is_file(href)

    @staticmethod
    def is_dir(href: str):
        storage = AccessManager.resolve_storage(href)

        return storage.is_dir(href)

    @staticmethod
    def get_file_size(href: str):
        try:
            storage = AccessManager.resolve_storage(href)
            if href and AccessManager.exists(href) and AccessManager.is_file(href):
                return storage.get_file_size(href)
        except Exception:
            ...
        return None

    @staticmethod
    def listdir(href: str):
        storage = AccessManager.resolve_storage(href)

        if not storage.is_dir(href):
            raise ValueError("Given href does not point to a directory")

        return storage.listdir(href)

    @staticmethod
    def get_last_modification_time(href: str):
        storage = AccessManager.resolve_storage(href)
        return storage.get_last_modification_time(href)

    @staticmethod
    def get_creation_time(href: str):
        storage = AccessManager.resolve_storage(href)
        return storage.get_creation_time(href)

    @staticmethod
    def makedir(href: str, strict=False):
        """
        Create if needed (and possible) the specified dir
        """
        storage = AccessManager.resolve_storage(href)
        return storage.makedir(href, strict=strict)

    @staticmethod
    def dirname(href: str):
        """
        Wraps os.path.dirname to allow for absolute path to be determined if needed
        """
        storage = AccessManager.resolve_storage(href)
        return storage.dirname(href)


LOGGER.info("Loading configuration {}".format(os.environ.get("APROC_CONFIGURATION_FILE")))
Configuration.init(os.environ.get("APROC_CONFIGURATION_FILE"))
AccessManager.init()
