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
    output_folder: str | None = None  # todo: this should use self.get_asset_filepath instead

    def __init__(self):
        super().__init__()
        self.md_path = None
        self.tif_path = None
        self.quicklook_path = None
        self.thumbnail_path = None
        self.data_mask_path = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)
        Driver.output_folder = configuration['tmp_directory']

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
                kwargs = dict(
                    name=b['name'],
                    eo__common_name=b['common_name'],
                    eo__center_wavelength=b['center_wavelength'],
                    eo__full_width_half_max=b['full_width_half_max'],
                )
                if include_solar:
                    kwargs['eo__solar_illumination'] = b['solar_illumination']
                bands.append(Band(**kwargs))
            return bands

        def get_bands(asset_name, include_solar=True):
            """
            Extract bands from metadata for a given asset name.
            Raises DriverException if a key is missing.
            """
            try:
                return make_bands(md['assets'][asset_name]['eo:bands'], include_solar)
            except KeyError as ke:
                raise DriverException(f"Invalid metadata file {self.md_path}: missing key {ke.args[0]}")

        # Extract bands for each asset type
        cog_eo_bands = get_bands('Cloud optimized GeoTiff', include_solar=True)
        ov_eo_bands = get_bands('Overview image', include_solar=False)
        th_eo_bands = get_bands('Thumbnail image', include_solar=False)

        def add_asset(path, role, mime, fmt, resource_type, bands, managed):
            """
            Add an Asset object to the assets list.
            """
            assets.append(Asset(
                href=path,
                size=AccessManager.get_size(path),
                roles=[role.value],
                name=role.value,
                type=mime.value,
                description=role.value,
                airs__managed=managed,
                asset_format=fmt.value,
                asset_type=resource_type.value,
                eo__bands=bands
            ))

        # Add cog, overview and thumbnail assets
        add_asset(self.tif_path, Role.data, MimeType.COG, AssetFormat.cog, ResourceType.gridded, cog_eo_bands, managed=False)
        add_asset(self.quicklook_path, Role.overview, MimeType.PNG, AssetFormat.png, ResourceType.gridded, ov_eo_bands, managed=True)
        add_asset(self.thumbnail_path, Role.thumbnail, MimeType.PNG, AssetFormat.png, ResourceType.gridded, th_eo_bands, managed=True)

        # Add metadata JSON asset
        ImageDriverHelper.add_asset(
            assets, self.md_path, Role.metadata, MimeType.JSON, AssetFormat.json, ResourceType.other
        )

        return assets


    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        with AccessManager.stream(self.md_path) as fb:
            md = json.load(fb)
        try:
            geometry = md["geometry"]
            bbox = md["bbox"]
            centroid_lon = (bbox[0] + bbox[2]) / 2
            centroid_lat = (bbox[1] + bbox[3]) / 2
            properties =  md["properties"]
            processing__level = properties["processing:level"]
            processing__facility = properties["processing:facility"]
            processing__version = properties["processing:version"]
            license = properties["license"]
            start_datetime = datetime.strptime(properties["start_datetime"], "%Y-%m-%dT%H:%M:%S.%fZ")
            end_datetime = datetime.strptime(properties["end_datetime"], "%Y-%m-%dT%H:%M:%S.%fZ")
            instrument = properties["instruments"][0]
            platform= properties["platform"]
            created =  int(datetime.strptime(properties["created"], "%Y-%m-%dT%H:%M:%SZ").timestamp())
            updated =  int(datetime.strptime(properties["updated"],"%Y-%m-%dT%H:%M:%SZ").timestamp())
            constellation = properties["constellation"]
            view__off_nadir = properties["view:off_nadir"]
            view__incidence_angle = properties["view:incidence_angle"]
            view__azimuth = properties["view:azimuth"]
            view__sun_azimuth = properties["view:sun_azimuth"]
            view__sun_elevation = properties["view:sun_elevation"]
            gsd = properties["gsd"]
            proj__epsg = properties["proj:epsg"]
            proj__shape = properties["proj:shape"]
            eo__cloud_cover = properties["eo:cloud_cover"]
            sensor_mode= properties["sensor_mode"]
            product_type = properties["product_type"]
            date_time = datetime.strptime(properties["datetime"], "%Y-%m-%dT%H:%M:%S.%fZ")
        except KeyError as ke:
            raise DriverException(f"Invalid metadata file {self.md_path}: a key is missing: {ke.args[0]}")

        item = Item(
            id=self.get_item_id(url),
            license=license,
            geometry=geometry,
            bbox=bbox,
            centroid=[centroid_lon,centroid_lat],
            properties=Properties(
                datetime=date_time,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                created=created,
                updated=updated,
                constellation=constellation,
                platform=platform,
                satellite=platform,
                instrument=instrument,
                sensor=platform,
                sensor_type=SensorType.OPTIC,
                sensor_mode=sensor_mode,
                item_format=ItemFormat.wyvern,
                item_type=ResourceType.gridded.value,
                main_asset_format=AssetFormat.geotiff,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.optic,
                processing__level=processing__level,
                processing__facility = processing__facility,
                processing__version = processing__version,
                gsd=gsd,
                proj__epsg=proj__epsg,
                proj__shape=proj__shape,
                view__off_nadir = view__off_nadir,
                view__incidence_angle = view__incidence_angle,
                view__azimuth = view__azimuth,
                view__sun_azimuth = view__sun_azimuth,
                view__sun_elevation = view__sun_elevation,
                product_type=product_type,
                eo__cloud_cover=eo__cloud_cover
            ),
            assets={asset.name: asset for asset in assets}
        )

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
                    elif file.name.endswith(".tiff"):
                        self.tif_path = file.path
                    elif file.name.endswith(".json"):
                        self.md_path = file.path
            return self.tif_path is not None \
                and self.md_path is not None \
                and self.quicklook_path is not None \
                and self.thumbnail_path is not None \
                and self.data_mask_path is not None
        return False