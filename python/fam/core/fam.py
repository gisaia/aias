import datetime
import os

from aias_common.access.manager import AccessManager
from extensions.aproc.proc.drivers.driver_manager import DriverManager
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver
from fam.core.model import Archive
from fam.core.logger import Logger

LOGGER = Logger.logger


class Fam():

    @staticmethod
    def list_archives(path: str, max_size: int = 10, timeout_in_seconds: int = 60) -> list[Archive]:
        return Fam.__list_archives(path, size=0, max_size=max_size, timeout_in_seconds=timeout_in_seconds, start_timestamp=datetime.datetime.now().timestamp())

    @staticmethod
    def __list_archives(path: str, size: int = 0, max_size: int = 10, start_timestamp: float = 0.0, timeout_in_seconds: int = 60) -> list[Archive]:
        if size >= max_size or os.path.basename(path).startswith("."):
            return []
        driver: IngestDriver = DriverManager.solve("ingest", path)
        if driver is not None:
            lm: float | None = AccessManager.get_last_modification_time(path)
            cd: float | None = AccessManager.get_creation_time(path)
            if lm:
                lm = datetime.datetime.fromtimestamp(lm)
            if cd:
                cd = datetime.datetime.fromtimestamp(cd)
            archive = Archive(id=driver.get_item_id(path),
                              name=os.path.basename(path.removesuffix("/")),
                              driver_name=driver.name,
                              path=path,
                              is_dir=AccessManager.is_dir(path),
                              last_modification_date=lm,
                              creation_date=cd)
            return [archive]
        else:
            if AccessManager.is_dir(path):
                if start_timestamp > 0 and start_timestamp + timeout_in_seconds < datetime.datetime.now().timestamp():
                    # taking too long : no more directory exploration
                    LOGGER.info("timeout on list_archives {}".format(path))
                    return []
                archives: list[Archive] = []
                for file in AccessManager.listdir(path):
                    sub_archives = Fam.__list_archives(file.path, size=size, max_size=max_size, start_timestamp=start_timestamp, timeout_in_seconds=timeout_in_seconds)
                    size = size + len(sub_archives)
                    archives = archives + sub_archives
                return archives
            else:
                # it is a file but no driver supports it, so it is not an archive.
                return []
