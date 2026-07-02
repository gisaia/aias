import json
from datetime import datetime
from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType, Band)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver
from extensions.aproc.proc.drivers.exceptions import DriverException


class Driver(IngestDriver):

    def __init__(self):
        super().__init__()
        self.md_path = None
        self.tif_path = None
        self.quicklook_path = None
        self.thumbnail_path = None
        self.data_mask_path = None
        self.quality_mask_path = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        # Add the archive asset
        ImageDriverHelper.add_archive(assets, url)
        # Load metadata JSON
        with AccessManager.stream(self.md_path) as fb:
            md = json.load(fb)

        def make_bands(bands_raw, include_solar=True):
            """
            Create Band objects from a list of dictionaries.

            Args:
                bands_raw (list): List of band dictionaries from metadata
                include_solar (bool): Whether to include solar_illumination attribute

            Returns:
                list[Band]: List of Band objects
            """
            bands = []
            for b in bands_raw:
                name = b.get('name', None)
                common_name = b.get('common_name', None)
                if not (name or common_name):
                    continue
                kwargs = dict(
                    name=name,
                    eo__common_name=common_name,
                    eo__center_wavelength=b.get('center_wavelength', None),
                    eo__full_width_half_max=b.get('full_width_half_max', None)
                )
                if include_solar:
                    kwargs['eo__solar_illumination'] = b.get('solar_illumination', None)
                bands.append(Band(**kwargs))
            return bands

        # Extract bands for each asset type
        cog_eo_bands = make_bands(md.get('assets', {}).get('Cloud optimized GeoTiff', {}).get('eo:bands', []), include_solar=True)
        ov_eo_bands = make_bands(md.get('assets', {}).get('Overview image', {}).get('eo:bands', []), include_solar=False)
        th_eo_bands = make_bands(md.get('assets', {}).get('Thumbnail image', {}).get('eo:bands', []), include_solar=False)

        # Add cog, overview and thumbnail assets
        ImageDriverHelper.add_asset(assets, href=self.tif_path, role=Role.data, type=MimeType.COG, asset_format=AssetFormat.cog, asset_type=ResourceType.gridded, eo_bands=cog_eo_bands, airs__managed=False)
        # Add metadata JSON asset
        ImageDriverHelper.add_asset(assets, href=self.md_path, role=Role.metadata, type=MimeType.JSON, asset_format=AssetFormat.json, asset_type=ResourceType.other)

        if self.quicklook_path:
            ImageDriverHelper.add_asset(assets, href=self.quicklook_path, role=Role.overview, type=MimeType.PNG, asset_format=AssetFormat.png, asset_type=ResourceType.gridded, eo_bands=ov_eo_bands, airs__managed=True)
        if self.thumbnail_path:
            ImageDriverHelper.add_asset(assets, href=self.thumbnail_path, role=Role.thumbnail, type=MimeType.PNG, asset_format=AssetFormat.png, asset_type=ResourceType.gridded, eo_bands=th_eo_bands, airs__managed=True)

        if self.quality_mask_path:
            ImageDriverHelper.add_asset(assets, href=self.quality_mask_path, role=Role.quality_mask, type=MimeType.TIFF, asset_format=AssetFormat.geotiff, asset_type=ResourceType.gridded)
        if self.data_mask_path:
            ImageDriverHelper.add_asset(assets, href=self.data_mask_path, role=Role.data_mask, type=MimeType.TIFF, asset_format=AssetFormat.geotiff, asset_type=ResourceType.gridded)

        return assets


    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    def load_metadata(self, url: str) -> object:
        with AccessManager.stream(self.md_path) as fb:
            md = json.load(fb)
        return md

    def build_core_item(self, url: str, assets: list[Asset], metadata: dict) -> Item:
        id = metadata.get("id", None)
        geometry = metadata.get("geometry", None)
        bbox = metadata.get("bbox", None)
        if bbox and len(bbox) >= 4:
            centroid_lon = (bbox[0] + bbox[2]) / 2
            centroid_lat = (bbox[1] + bbox[3]) / 2
            centroid = [centroid_lon, centroid_lat]
        else:
            centroid = None

        properties = metadata.get("properties", {})
        start_datetime_str = properties.get("start_datetime", None)
        start_datetime = (
            datetime.strptime(start_datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            if start_datetime_str
            else None
        )
        end_datetime_str = properties.get("end_datetime", None)
        end_datetime = (
            datetime.strptime(end_datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            if end_datetime_str
            else None
        )
        constellation = properties.get("constellation", None)
        date_time_str = properties.get("datetime", None)
        date_time = (
            datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            if date_time_str
            else None
        )
        item = Item(
            id=self.get_item_id(url),
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                constellation=constellation,
                sensor_type=SensorType.OPTIC.value,
                secondary_id=id,
                item_format=ItemFormat.wyvern,
                item_type=ResourceType.gridded.value,
                main_asset_format=AssetFormat.geotiff,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.optic
            ),
            assets={asset.name: asset for asset in assets}
        )

        return item

    def add_major_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        properties = metadata.get("properties", {})

        processing__level = properties.get("processing:level", None)
        gsd = properties.get("gsd", None)
        proj__epsg = properties.get("proj:epsg", None)
        satellite = properties.get("platform", None)
        item.properties.gsd=gsd
        item.properties.processing__level=processing__level
        item.properties.proj__epsg=proj__epsg
        item.properties.satellite=satellite
        item.properties.secondary_id = metadata.get("id", None)
        return item

    def add_minor_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        properties = metadata.get("properties", {})

        processing__facility = properties.get("processing:facility", None)
        processing__version = properties.get("processing:version", None)
        license = properties.get("license", None)
        instruments = properties.get("instruments", [])
        instrument = instruments[0] if instruments else None
        platform = properties.get("platform", None)
        created_str = properties.get("created", None)
        created = (
            int(datetime.strptime(created_str, "%Y-%m-%dT%H:%M:%SZ").timestamp())
            if created_str
            else None
        )
        updated_str = properties.get("updated", None)
        updated = (
            int(datetime.strptime(updated_str, "%Y-%m-%dT%H:%M:%SZ").timestamp())
            if updated_str
            else None
        )
        view__off_nadir = properties.get("view:off_nadir", None)
        view__incidence_angle = properties.get("view:incidence_angle", None)
        view__azimuth = properties.get("view:azimuth", None)
        view__sun_azimuth = properties.get("view:sun_azimuth", None)
        view__sun_elevation = properties.get("view:sun_elevation", None)
        proj__shape = properties.get("proj:shape", None)
        eo__cloud_cover = properties.get("eo:cloud_cover", None)
        sensor_mode = properties.get("sensor_mode", None)
        product_type = properties.get("product_type", None)

        item.properties.processing__facility = processing__facility
        item.properties.processing__version = processing__version
        item.properties.license = license
        item.properties.instrument = instrument
        item.properties.platform= platform
        item.properties.created =  created
        item.properties.updated =  updated
        item.properties.view__off_nadir = view__off_nadir
        item.properties.view__incidence_angle = view__incidence_angle
        item.properties.view__azimuth = view__azimuth
        item.properties.view__sun_azimuth = view__sun_azimuth
        item.properties.view__sun_elevation = view__sun_elevation
        item.properties.proj__shape = proj__shape
        item.properties.eo__cloud_cover = eo__cloud_cover
        item.properties.sensor_mode= sensor_mode
        item.properties.sensor = platform
        item.properties.product_type = product_type
        return item

    def __check_path__(self, path: str):
        self.__init__()
        if AccessManager.is_dir(path):
            for file in AccessManager.listdir(path):
                if file.name.startswith("wyvern"):
                    if file.name.endswith("_data_mask.tiff"):
                        self.data_mask_path = file.path
                    elif file.name.endswith("_preview.png"):
                        self.quicklook_path = file.path
                    elif file.name.endswith("_thumbnail.png"):
                        self.thumbnail_path = file.path
                    elif file.name.endswith("_pixel_quality_mask.tiff"):
                        self.quality_mask_path = file.path
                    elif file.name.endswith("_mask.tiff"):
                        Driver.LOGGER.warning(f"Found mask file {file.path} but not registered as asset")
                    elif file.name.endswith((".tif", ".tiff")):
                        self.tif_path = file.path
                    elif file.name.endswith(".json"):
                        self.md_path = file.path
            return self.tif_path is not None \
                and self.md_path is not None 
        return False