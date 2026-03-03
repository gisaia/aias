"""
Standalone local test for the Satellogic ingest driver.

Extracts the synthetic test product ZIP, runs the driver pipeline,
and validates all metadata fields without requiring external infrastructure.

Run with:
    cd aias && python -m pytest test/test_satellogic_driver.py -v
"""
import os
import shutil
import tempfile
import unittest
import zipfile
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import Band, Role
from aproc.core.settings import Configuration as AprocConfiguration
from extensions.aproc.proc.drivers.driver_manager import DriverManager
from extensions.aproc.proc.ingest.drivers.impl.satellogic import Driver
from extensions.aproc.proc.ingest.ingest_process import summary
from extensions.aproc.proc.ingest.settings import Configuration as IngestConfiguration


_TEST_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to the synthetic product ZIP (inside aias/test/inputs/images/)
SYNTHETIC_ZIP = os.path.join(
    _TEST_DIR, "inputs", "images",
    "SYNTHETIC_20260101_120000_000_SN01_L1D_SR_MS_999999.zip",
)

# Golden reference files produced by the current driver pipeline
EXPECTED_OVERVIEW = os.path.join(
    _TEST_DIR, "inputs", "images", "expected_satellogic_overview.png",
)
EXPECTED_THUMBNAIL = os.path.join(
    _TEST_DIR, "inputs", "images", "expected_satellogic_thumbnail.png",
)


class TestSatellogicDriver(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize AccessManager from config (same as utils.py)
        AprocConfiguration.init(configuration_file='conf/aproc.yaml')
        AccessManager.init(AprocConfiguration.settings.access_manager)
        IngestConfiguration.init(configuration_file='./conf/drivers.yaml')
        DriverManager.init(summary.id, IngestConfiguration.settings.drivers)

        # Extract synthetic product to a temp directory under /tmp/
        cls.tmp_dir = tempfile.mkdtemp(prefix="test-satellogic-", dir="/tmp")
        cls.extract_dir = os.path.join(cls.tmp_dir, "product")
        os.makedirs(cls.extract_dir)
        with zipfile.ZipFile(SYNTHETIC_ZIP, "r") as zf:
            zf.extractall(cls.extract_dir)

        # Set up the driver
        cls.driver = Driver()
        cls.driver.assets_dir = os.path.join(cls.tmp_dir, "assets")
        os.makedirs(cls.driver.assets_dir, exist_ok=True)
        cls.driver.name = "satellogic"

        # Run the full pipeline once for to_item tests
        if not cls.driver.supports(cls.extract_dir):
            raise unittest.SkipTest(
                f"Driver does not support extracted product at {cls.extract_dir}"
            )
        cls.assets = cls.driver.identify_assets(cls.extract_dir)
        cls.assets = cls.driver.fetch_assets(cls.extract_dir, cls.assets)
        cls.assets = cls.driver.transform_assets(cls.extract_dir, cls.assets)
        cls.item = cls.driver.to_item(cls.extract_dir, cls.assets)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_dir, ignore_errors=True)

    # ── supports() tests ──

    def test_supports_valid_product(self):
        driver = Driver()
        self.assertTrue(driver.supports(self.extract_dir))

    def test_supports_empty_directory(self):
        empty_dir = os.path.join(self.tmp_dir, "empty")
        os.makedirs(empty_dir, exist_ok=True)
        driver = Driver()
        self.assertFalse(driver.supports(empty_dir))

    def test_supports_missing_toa(self):
        """Directory with metadata but no rasters/*_TOA_0.tif."""
        no_toa_dir = os.path.join(self.tmp_dir, "no_toa")
        os.makedirs(no_toa_dir, exist_ok=True)
        # Copy only the metadata file
        for f in os.listdir(self.extract_dir):
            if f.endswith("_metadata_stac.geojson"):
                shutil.copy2(
                    os.path.join(self.extract_dir, f),
                    os.path.join(no_toa_dir, f),
                )
        driver = Driver()
        self.assertFalse(driver.supports(no_toa_dir))

    def test_supports_missing_metadata(self):
        """Directory with rasters/*_TOA_0.tif but no geojson."""
        no_md_dir = os.path.join(self.tmp_dir, "no_metadata")
        rasters_dir = os.path.join(no_md_dir, "rasters")
        os.makedirs(rasters_dir, exist_ok=True)
        # Copy only the TOA raster
        src_rasters = os.path.join(self.extract_dir, "rasters")
        for f in os.listdir(src_rasters):
            if f.endswith("_TOA_0.tif"):
                shutil.copy2(
                    os.path.join(src_rasters, f),
                    os.path.join(rasters_dir, f),
                )
        driver = Driver()
        self.assertFalse(driver.supports(no_md_dir))

    # ── identify_assets() tests ──

    def test_identify_assets(self):
        driver = Driver()
        driver.supports(self.extract_dir)
        assets = driver.identify_assets(self.extract_dir)
        asset_names = [a.name for a in assets]
        expected = [
            Role.archive.value,
            Role.data.value,
            Role.visual.value,
            Role.cloud.value,
            Role.metadata.value,
            Role.thumbnail.value,
            Role.overview.value,
        ]
        for name in expected:
            self.assertIn(name, asset_names, f"Missing asset: {name}")
        self.assertEqual(len(assets), 7)
        for asset in assets:
            self.assertIsNotNone(asset.roles)
            self.assertGreaterEqual(len(asset.roles), 1)
            self.assertIsNotNone(asset.href)

    def test_identify_assets_data_has_bands(self):
        driver = Driver()
        driver.supports(self.extract_dir)
        assets = driver.identify_assets(self.extract_dir)
        data_asset = next(a for a in assets if a.name == Role.data.value)
        self.assertIsNotNone(data_asset.eo__bands)
        self.assertEqual(len(data_asset.eo__bands), 4)
        band_names = [b.name for b in data_asset.eo__bands]
        self.assertEqual(band_names, ["blue_test", "green_test", "red_test", "nir_test"])
        for band in data_asset.eo__bands:
            self.assertIsInstance(band, Band)

    # ── to_item() tests ──

    def test_to_item_no_exception(self):
        # The pipeline was already run in setUpClass; verify no exception was raised
        self.assertIsNotNone(self.item)

    def test_to_item_geometry(self):
        self.assertIsNotNone(self.item.geometry)
        self.assertEqual(self.item.geometry["type"], "Polygon")
        self.assertIsNotNone(self.item.bbox)
        self.assertEqual(len(self.item.bbox), 4)
        self.assertAlmostEqual(self.item.bbox[0], -110.924, places=3)
        self.assertAlmostEqual(self.item.bbox[1], 32.127, places=3)
        self.assertAlmostEqual(self.item.bbox[2], -110.821, places=3)
        self.assertAlmostEqual(self.item.bbox[3], 32.217, places=3)
        self.assertIsNotNone(self.item.centroid)
        self.assertEqual(len(self.item.centroid), 2)

    def test_to_item_core_properties(self):
        props = self.item.properties
        self.assertEqual(props.constellation, "Satellogic")
        self.assertEqual(props.item_format, "SATELLOGIC")
        self.assertEqual(props.sensor_type, "OPTIC")
        self.assertEqual(props.observation_type, "OPTIC")
        self.assertEqual(props.main_asset_format, "GEOTIFF")
        self.assertEqual(props.main_asset_name, "data")

    def test_to_item_major_metadata(self):
        props = self.item.properties
        self.assertAlmostEqual(props.gsd, 0.75, places=5)
        self.assertEqual(props.satellite, "newsat01")
        self.assertEqual(props.proj__epsg, 32612)
        self.assertEqual(props.processing__level, "L1D_SR")
        self.assertEqual(
            props.secondary_id,
            "20260101_120000_000_SN01_L1D_SR_MS_999999",
        )

    def test_to_item_minor_metadata(self):
        props = self.item.properties
        self.assertAlmostEqual(props.eo__cloud_cover, 12.34, places=5)
        self.assertAlmostEqual(props.view__sun_azimuth, 222.222, places=5)
        self.assertAlmostEqual(props.view__sun_elevation, 33.333, places=5)
        self.assertAlmostEqual(props.view__azimuth, 44.444, places=5)
        self.assertAlmostEqual(props.view__off_nadir, 11.111, places=5)
        self.assertAlmostEqual(props.view__incidence_angle, 55.555, places=5)
        self.assertEqual(props.instrument, "multispectral")
        self.assertEqual(props.sensor, "newsat01")

    def test_to_item_datetime(self):
        props = self.item.properties
        self.assertIsNotNone(props.datetime)
        expected_dt = datetime.strptime("2026-01-01T12:34:56.000000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
        self.assertEqual(props.datetime, expected_dt)

    def test_to_item_assets_complete(self):
        expected_keys = [
            "archive", "data", "visual", "cloud",
            "metadata", "thumbnail", "overview",
        ]
        for key in expected_keys:
            self.assertIn(key, self.item.assets, f"Missing asset key: {key}")

    # ── transform_assets() output comparison tests ──

    def test_transform_overview_matches_golden(self):
        """Overview produced by _crop_black_borders must match the golden reference."""
        overview_asset = next(a for a in self.assets if a.name == "overview")
        with open(overview_asset.href, "rb") as f:
            produced = f.read()
        with open(EXPECTED_OVERVIEW, "rb") as f:
            expected = f.read()
        self.assertEqual(
            produced, expected,
            f"Overview mismatch: produced {len(produced)} bytes vs expected {len(expected)} bytes",
        )

    def test_transform_thumbnail_matches_golden(self):
        """Thumbnail (copied from product, not reprocessed) must match the golden reference."""
        thumbnail_asset = next(a for a in self.assets if a.name == "thumbnail")
        with open(thumbnail_asset.href, "rb") as f:
            produced = f.read()
        with open(EXPECTED_THUMBNAIL, "rb") as f:
            expected = f.read()
        self.assertEqual(
            produced, expected,
            f"Thumbnail mismatch: produced {len(produced)} bytes vs expected {len(expected)} bytes",
        )


if __name__ == "__main__":
    unittest.main()
