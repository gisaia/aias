from contextlib import contextmanager
from datetime import datetime
import os
import shutil
import tempfile
from typing import Annotated, Union

from pydantic import Field

from aproc.core.logger import Logger
from aproc.core.settings import Configuration
from extensions.aproc.proc.access.storages.file import FileStorage
from extensions.aproc.proc.access.storages.gs import GoogleStorage
from extensions.aproc.proc.access.storages.http import HttpStorage
from extensions.aproc.proc.access.storages.https import HttpsStorage

AnyStorage = Annotated[Union[FileStorage, GoogleStorage, HttpStorage, HttpsStorage], Field(discriminator="type")]

LOGGER = Logger.logger


class AccessManager:
    storage: AnyStorage | None = Field(None)
    tmp_dir = tempfile.gettempdir()

    @staticmethod
    def init():
        LOGGER.info("Initializing APROC storages")
        storage_settings = Configuration.settings.storage.model_dump()

        match Configuration.settings.storage.type:
            case "file":
                AccessManager.storage = FileStorage(**storage_settings)
            case "gs":
                AccessManager.storage = GoogleStorage(**storage_settings)
            case "http":
                AccessManager.storage = HttpStorage(**storage_settings)
            case "https":
                AccessManager.storage = HttpsStorage(**storage_settings)
            case _:
                raise NotImplementedError(f"Specified storage {Configuration.settings.storage.type} is not implemented")

    @staticmethod
    def resolve_storage(href: str) -> AnyStorage:
        """
        Based on the defined storages (TODO), returns the one matching the input href
        """

        if AccessManager.storage.supports(href):
            return AccessManager.storage

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
        storage.pull(href, dst)

    # Will return a yield
    @staticmethod
    def stream():
        """
        Reads the content of a file in a storage without downloading it.
        """
        ...

    @contextmanager
    @staticmethod
    def get_rasterio_session(href: str):
        import rasterio

        storage = AccessManager.resolve_storage(href)

        yield rasterio.Env(storage.get_rasterio_session())

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
            and AccessManager.storage.force_download

    @staticmethod
    def prepare(href: str):
        """Prepare the file to be processed locally

        Args:
            href (str): Href (local or not) of the file

        Returns:
            str: The local path at which the file can be found
        """
        storage = AccessManager.resolve_storage(href)

        href = storage.prepare_for_local_process(href)
        return href

    @staticmethod
    def zip(href: str, target_directory: str):
        # For all storages but FileStorage, files need to be pulled before being processed
        href = AccessManager.prepare(href)

        file_name = os.path.basename(href)
        # Get direct parent folder of href_file to zip
        dir_name = os.path.dirname(href)
        target_file_name = os.path.splitext(file_name)[0] + datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
        shutil.make_archive(target_directory + "/" + target_file_name, 'zip', dir_name)
