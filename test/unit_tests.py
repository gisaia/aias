import unittest
from datetime import datetime
import dateutil.parser as parser
import json

import airs.core.models.mapper as mapper
from airs.core.models.model import Item

class Tests(unittest.TestCase):

    def test_load_item(self):
        # we check that the values loaded from the json file are correct
        with open("test/inputs/077cb463-1f68-5532-aa8b-8df0b510231a.json", 'r') as jsonfile:
            item:Item=Item(**json.load(jsonfile))
            self.assertEqual(item.id,"077cb463-1f68-5532-aa8b-8df0b510231a")
            self.assertEqual(item.properties.proj__epsg,4326)
            self.assertEqual(item.properties.end_datetime,parser.parse("2021-12-31T00:00:00Z"))
            self.assertEqual(item.properties.start_datetime,parser.parse("2021-01-01T00:00:00Z"))
            self.assertEqual(item.properties.datetime,parser.parse("2021-12-31T00:00:00Z"))
            self.assertTrue(item.assets.get("classification", False))
            self.assertEqual(item.assets["classification"].eo__bands[0].name,"classification")
            self.assertEqual(item.assets["classification"].proj__epsg,4326)
            self.assertTrue("data" in item.assets["classification"].roles)
            self.assertEqual(item.bbox[0],0.0)
            self.assertEqual(item.bbox[1],15.0)
            self.assertEqual(item.bbox[2],3.0)
            self.assertEqual(item.bbox[3],18.0)
            self.assertEqual(item.collection,"esa_worldcover_2021")

    def test_export_item(self):
        # we check that load(export(load(json)))=load(json)
        self.maxDiff=None
        with open("test/inputs/077cb463-1f68-5532-aa8b-8df0b510231a.json", 'r') as jsonfile:
            expected=mapper.item_from_json_file(jsonfile)
            result=mapper.item_from_json(mapper.to_json(expected))
            print(result)
            self.assertEqual(
                result, 
                expected
                )
            result=mapper.item_from_json(mapper.to_arlaseo_json(expected))
            print(expected.assets["classification"].eo__bands)
            print(result.assets["classification"].eo__bands)
            self.assertEqual(
                result, 
                expected
                )

if __name__ == '__main__':
    unittest.main()
