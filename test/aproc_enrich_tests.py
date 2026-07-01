import json
import os
from time import sleep
import unittest
from airs.core.models import mapper
from airs.core.models.model import AssetFormat, Item
from aproc.core.models.ogc.enums import StatusCode
from aproc.core.models.ogc.job import StatusInfo
from test.aproc_ingest_tests import (AST, CAPELLA1, CAPELLA2, CAPELLA3, CSK, CSK2, SPOT6, GEOSAT, ICEYE, IKONOS, JP2000, PNEOMS, PNEOPAN,
                                     RADARSAT2, RAPID_EYE, SATELLOGIC, SENTINEL1_GRDH, SUPERVIEW, SUPERVIEW3_4, WYVERN, LANDSAT9,
                                     SENTINEL1_SLC, SENTINEL2, SKYSAT, SPOT5,
                                     TERRASARX, TERRASARX_PAZ, TIF, WORLDVIEW, UMBRA_STAC, IngestTests)
from test.aproc_tests import AprocTests
from test.utils import (AIRS_URL, APROC_ENDPOINT, CATALOG, COLLECTION, SENTINEL_2_ID, SENTINEL_2_ITEM, SENTINEL_2_ZIP_ID, MAX_ITERATIONS,
                        SENTINEL_2_ZIP_ITEM, add_item)
import requests

from aproc.core.models.ogc import Execute
from extensions.aproc.proc.enrich.enrich_process import InputEnrichProcess
from test.aproc_ingest_tests_gs import ROOT, Tests as IngestionTests

class Tests(AprocTests):

    def enrich_with(self, id: str, enrichments: list[str]) -> Item:
        inputs: InputEnrichProcess = InputEnrichProcess(requests=[{"collection": COLLECTION, "item_id": id}], enrichments=enrichments)
        execute = Execute(inputs=inputs.model_dump(exclude_none=True, exclude_unset=True))
        r = requests.post("/".join([APROC_ENDPOINT, "processes/enrich/execution"]), data=json.dumps(execute.model_dump(exclude_none=True, exclude_unset=True)), headers={"Content-Type": "application/json"})
        self.assertTrue(r.ok)
        status: StatusInfo = StatusInfo(**json.loads(r.content))
        i: int = 0
        while status.status not in [StatusCode.failed, StatusCode.dismissed, StatusCode.successful] and i < MAX_ITERATIONS:
            sleep(1)
            i = i + 1
            status = StatusInfo(**json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID])).content))
        self.assertEqual(status.status, StatusCode.successful, status.model_dump_json())

        # check that the item has the new asset
        item: Item = mapper.item_from_dict(requests.get("/".join([AIRS_URL, "collections", COLLECTION, "items", id])).json()) 
        return item

    def check_cog(self, item: Item, asset_type: str, max_size: int):
        self.assertIsNotNone(item.assets.get(asset_type), f"{asset_type} asset exists")
        self.assertGreater(item.assets.get(asset_type).size, 0, f"{asset_type} size greater than 0")
        self.assertEqual(item.assets.get(asset_type).asset_format, AssetFormat.cog.value, f"format is cog")
        self.assertEqual(item.assets.get(asset_type).proj__epsg, 3857, f"projection is 3857")
        from osgeo import gdal
        with gdal.Open(item.assets.get(asset_type).href) as ds:
            src_width = ds.RasterXSize
            src_height = ds.RasterYSize
            self.assertLessEqual(src_width, max_size, f"{asset_type} width less than {max_size}")
            self.assertLessEqual(src_height, max_size, f"{asset_type} height less than {max_size}")
        info = gdal.Info(item.assets.get(asset_type).href, options=gdal.InfoOptions(format="json"))
        self.assertEqual(info.get("metadata").get("IMAGE_STRUCTURE", {}).get("LAYOUT", None), "COG", "layout is COG")


    def test_enrich_s2_cog_from_zip(self):
        add_item(self, SENTINEL_2_ZIP_ITEM, SENTINEL_2_ZIP_ID)
        i = self.enrich_with(SENTINEL_2_ZIP_ID, [AssetFormat.overview_cog.value, AssetFormat.cog.value])
        self.check_cog(i, AssetFormat.cog.value.lower(), 500)
        self.check_cog(i, AssetFormat.overview_cog.value.lower(), 200)

    def test_enrich_s2_cog_from_folder(self):
        add_item(self, SENTINEL_2_ITEM, SENTINEL_2_ID)
        i: Item = self.enrich_with(SENTINEL_2_ID, [AssetFormat.overview_cog.value, AssetFormat.cog.value, AssetFormat.all_bands_cog.value])
        self.check_cog(i, AssetFormat.cog.value.lower(), 500)
        self.check_cog(i, AssetFormat.overview_cog.value.lower(), 200)
        self.check_cog(i, AssetFormat.all_bands_cog.value.lower(), 300)

    def enrich_archive_cog(self, url, enrichments: list[str] = [AssetFormat.cog.value, AssetFormat.overview_cog.value]):
        r = IngestionTests().ingest_no_wait(url, COLLECTION, CATALOG)
        status = StatusInfo(**json.loads(r.content))
        status = IngestionTests().wait_for(status)
        result = json.loads(requests.get("/".join([APROC_ENDPOINT, "jobs", status.jobID, "results"])).content)
        i = mapper.item_from_json(requests.get(result["item_location"]).content)
        i = self.enrich_with(i.id, enrichments)
        self.check_cog(i, AssetFormat.cog.value.lower(), 500)
        self.check_cog(i, AssetFormat.overview_cog.value.lower(), 200)
        return i

    def test_enrich_landsat9_cog(self):
        url = os.path.join(ROOT, LANDSAT9)
        i = self.enrich_archive_cog(url, enrichments=[AssetFormat.cog.value, AssetFormat.overview_cog.value, AssetFormat.all_bands_cog.value])
        self.check_cog(i, AssetFormat.all_bands_cog.value.lower(), 300)

    def test_enrich_ast_cog(self):
        url = os.path.join(ROOT, AST)
        self.enrich_archive_cog(url)

    # def test_enrich_axelspace_cog(self):
        # url = os.path.join(ROOT, AXELSPACE)
        # self.enrich_archive_cog(url)  TODO : get synthetic data

    # def test_enrich_bsg_cog(self):
        # url = os.path.join(ROOT, BSG)
        # self.enrich_archive_cog(url)  TODO : get synthetic data

    def test_enrich_capella1_cog(self):
        url = os.path.join(ROOT, CAPELLA1)
        self.enrich_archive_cog(url)

    def test_enrich_capella2_cog(self):
        url = os.path.join(ROOT, CAPELLA2)
        self.enrich_archive_cog(url)

    def test_enrich_capella3_cog(self):
        url = os.path.join(ROOT, CAPELLA3)
        self.enrich_archive_cog(url)

    # def test_enrich_csk_cog(self):  No driver for CSK H5 for now
    #     url = os.path.join(ROOT, CSK)
    #     self.enrich_archive_cog(url)

    def test_enrich_csk2_cog(self):
        url = os.path.join(ROOT, CSK2)
        self.enrich_archive_cog(url)

    def test_enrich_digitalglobe_cog(self):
        url = os.path.join(ROOT, WORLDVIEW)
        self.enrich_archive_cog(url)

    def test_enrich_spot5_cog(self):
        url = os.path.join(ROOT, SPOT5)
        self.enrich_archive_cog(url)

    def test_enrich_spot6_cog(self):
        url = os.path.join(ROOT, SPOT6)
        self.enrich_archive_cog(url)

    # def test_enrich_pneoms_cog(self):   TODO: DOES NOT WORK WITH JPEG2000 source. See issue https://github.com/gisaia/aias/issues/507
    #     url = os.path.join(ROOT, PNEOMS)
    #     self.enrich_archive_cog(url)

    # def test_enrich_pneopan_cog(self):  TODO: DOES NOT WORK WITH JPEG2000 source. See issue https://github.com/gisaia/aias/issues/507
    #     url = os.path.join(ROOT, PNEOPAN)
    #     self.enrich_archive_cog(url)

    def test_enrich_geoeye_cog(self):   
        url = os.path.join(ROOT, IKONOS)
        self.enrich_archive_cog(url)

    def test_enrich_geosat_cog(self):   
        url = os.path.join(ROOT, GEOSAT)
        self.enrich_archive_cog(url)

    def test_enrich_iceye_cog(self):
        url = os.path.join(ROOT, ICEYE)
        self.enrich_archive_cog(url)

    # def test_enrich_opencosmos_cog(self): TODO: waiting for a synthetic dataset to be generated for opencosmos, see issue https://github.com/gisaia/aias/issues/507
        url = os.path.join(ROOT, "opencosmos/HAMMER_L1C_000003173_20251230113811_20251230113815_9ABD70F6_assets")
        self.enrich_archive_cog(url)

    # def test_enrich_radarsat2_cog(self):  # y a pas de data par defaut, donc pas de visu

    def test_enrich_rapideye_cog(self):
        url = os.path.join(ROOT, RAPID_EYE)
        self.enrich_archive_cog(url)

    def test_enrich_satellogic_cog(self):
        url = os.path.join(ROOT, SATELLOGIC)
        self.enrich_archive_cog(url)

    def test_enrich_skysat_cog(self):
        url = os.path.join(ROOT, SKYSAT)
        self.enrich_archive_cog(url)

    def test_enrich_superview_cog(self):
        url = os.path.join(ROOT, SUPERVIEW)
        self.enrich_archive_cog(url)

    def test_enrich_superview3_4_cog(self):
        url = os.path.join(ROOT, SUPERVIEW3_4 + "_MUX")
        self.enrich_archive_cog(url)

    def test_enrich_terrasarx_cog(self):   
        url = os.path.join(ROOT, TERRASARX)
        self.enrich_archive_cog(url)

    def test_enrich_terrasarx_paz_cog(self): 
        url = os.path.join(ROOT, TERRASARX_PAZ)
        self.enrich_archive_cog(url)

    def test_enrich_umbra_cog(self):    
        url = os.path.join(ROOT, UMBRA_STAC)
        self.enrich_archive_cog(url)

    def test_enrich_wyvern_cog(self): 
        url = os.path.join(ROOT, WYVERN)
        self.enrich_archive_cog(url)

    def test_enrich_tiff_cog(self):
        url = os.path.join(ROOT, TIF)
        self.enrich_archive_cog(url)

    # def test_enrich_jpg2000_cog(self): TODO: DOES NOT WORK WITH JPEG2000 source. See issue https://github.com/gisaia/aias/issues/507
    #     url = os.path.join(ROOT, JP2000)
    #     self.enrich_archive_cog(url)

if __name__ == '__main__':
    unittest.main()
