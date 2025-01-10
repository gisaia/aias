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
    def pull(href: str, dst: str, is_dst_dir: bool):
        """
        Pulls a file from a storage to write it in the local storage.
        If the input storage is local, then it is a copy. Otherwise it is a download.
        """
        storage = AccessManager.resolve_storage(href)
        storage.pull(href, dst, is_dst_dir)

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
            and storage.force_download

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

    @staticmethod
    def is_file(href: str):
        storage = AccessManager.resolve_storage(href)

        return storage.is_file(href)

    @staticmethod
    def is_dir(href: str):
        storage = AccessManager.resolve_storage(href)

        return storage.is_dir(href)
