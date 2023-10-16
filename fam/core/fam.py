import datetime
import os
from extensions.aproc.proc.ingest.drivers.drivers import Drivers
from fam.core.model import Archive

class Fam():

    def list_archives(prefix: str, path: str, size: int = 0, max_size: int = 10) -> list[Archive]:
        full_path=os.path.join(prefix, path)
        if size >= max_size or os.path.basename(path).startswith("."):
            return []
        driver = Drivers.solve(full_path)
        if driver is not None:
            archive = Archive(id=driver.get_item_id(full_path),
                              name=os.path.basename(path),
                              driver_name=driver.name,
                              path=path,
                              is_dir=os.path.isdir(full_path),
                              last_modification_date=datetime.datetime.fromtimestamp(os.path.getmtime(full_path)),
                              creation_date=datetime.datetime.fromtimestamp(os.path.getctime(full_path)))
            return [archive]
        else:
            if os.path.isdir(full_path):
                archives: list[Archive] = []
                for file in os.listdir(full_path):
                    sub_archives = Fam.list_archives(prefix, os.path.join(path, file), size=size, max_size=max_size)
                    size = size + len(sub_archives)
                    archives = archives + sub_archives
                return archives
            else:
                # it is a file but no driver supports it, so it is not an archive.
                return []
