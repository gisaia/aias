import os
from airs.core.models.model import Item, Role
from aproc.core.settings import Configuration
from extensions.aproc.proc.download.drivers.driver import Driver as DownloadDriver
from datetime import datetime
class Driver(DownloadDriver):

    # Implements drivers method
    @staticmethod
    def init(configuration: Configuration):
        ...

    # Implements drivers method
    @staticmethod
    def supports(item: Item) -> bool:
        if item.assets.get(Role.metadata.value) is not None:
            asset = item.assets.get(Role.metadata.value)
            file_name = os.path.basename(asset.href)
            return file_name.startswith("DIM") and file_name.endswith(".XML")
        else:
            return False
    
    # Implements drivers method
    def fetch_and_transform(self, item: Item, target_directory: str, file_name: str, crop_wkt: str, target_projection: str, target_format: str):
        from extensions.aproc.proc.download.drivers.impl.utils import extract
        import pyproj
        asset = item.assets.get(Role.metadata.value)
        dimap_file = asset.href
        dimap_file_name = os.path.basename(dimap_file)
        epsg_target = pyproj.Proj(target_projection)
        # Default driver is GTiff
        driver_target = "GTiff"
        if target_format == "Geotiff":
            driver_target = "GTiff"
            target_file_name = os.path.splitext(dimap_file_name)[0]  + datetime.now().strftime("%d-%m-%Y-%H-%M-%S")+'.tif'
        elif target_format == "Jpeg2000":
            driver_target = "JP2OpenJPEG"
            target_file_name = os.path.splitext(dimap_file_name)[0]  + datetime.now().strftime("%d-%m-%Y-%H-%M-%S")+'.JP2'
        extract(crop_wkt, dimap_file, driver_target, epsg_target, target_directory, target_file_name,
                      target_projection)



