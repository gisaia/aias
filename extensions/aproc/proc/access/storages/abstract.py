from abc import ABC, abstractmethod
import os
import tempfile
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel


class AbstractStorage(BaseModel, ABC):
    type: Any

    @abstractmethod
    def get_storage_parameters(self) -> dict:
        """Based on the type of storage and its characteristics, gives storage-specific parameters to use to access data

        Args:
            href (str): Href of the file to consult
        """
        ...

    @abstractmethod
    def supports(self, href: str) -> bool:
        """Return whether the provided href can be handled by the storage.

        Args:
            href (str): Href of the file to consult

        Returns:
            bool: True if the storage can handle href, False otherwise
        """
        ...

    @abstractmethod
    def exists(self, href: str) -> bool:
        """Return whether the file given exists in the storage

        Args:
            href (str): Href of the file to consult

        Returns:
            bool: True if the file exists, False otherwise
        """
        ...

    @abstractmethod
    def get_rasterio_session(self) -> dict:
        """Return a rasterio Session and potential variables to access data remotely

        Args:
            href (str): Href od the file to stream

        Returns:
            dict
        """
        ...

    @abstractmethod
    def pull(self, href: str, dst: str):
        """Copy/Download the desired file from the file system to write it locally

        Args:
            href (str): File to fetch
            dst (str): Destination of the file
        """
        # Check that dst is local
        scheme = urlparse(dst).scheme
        if scheme != "" and scheme != "file":
            raise ValueError("Destination must be on the local filesystem")

    def prepare_for_local_process(self, href: str) -> str:
        """Prepare the desired file, to then be able to process it locally

        Args:
            href(str): File to prepare

        Returns:
            str: The local path at which the file can be found
        """
        dst = os.path.join(tempfile.gettempdir(), os.path.basename(href))

        self.pull(href, dst)
        return dst

    @abstractmethod
    def is_file(self, href: str) -> bool:
        """Returns whether the specified href is a file

        Args:
            href(str): The href to test

        Returns:
            bool: Whether the input is a file
        """
        ...

    @abstractmethod
    def is_dir(self, href: str) -> bool:
        """Returns whether the specified href is a directory

        Args:
            href(str): The href to test

        Returns:
            bool: Whether the input is a directory
        """
        ...
