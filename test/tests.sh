export PYTHONPATH=`pwd`

# UNIT TESTS
python3 test/tests.py

# Add asset
#curl -X POST \
#    http://127.0.0.1:8000/digitalearth.africa/esa_worldcover_2021/077cb463-1f68-5532-aa8b-8df0b510231a/classification?content_type=image/tiff \
#    -F file=@test/ESA_WorldCover_10m_2021_v200_N15E000_Map.tif

# Add item
#curl -X POST \
#    -H "Content-Type: application/json" \
#    http://127.0.0.1:8000/digitalearth.africa/esa_worldcover_2021/077cb463-1f68-5532-aa8b-8df0b510231a \
#    -d @test/077cb463-1f68-5532-aa8b-8df0b510231a.json 


#curl -X POST \
#    -H "Content-Type: application/json" \
#    http://localhost:8000/dominox/theia-snow/SENTINEL2A_20230411-112240-616_L2B-SNOW_T29RPQ_D \
#    -d '{"collection": null, "catalog": null, "id": "SENTINEL2A_20230411-112240-616_L2B-SNOW_T29RPQ_D", "geometry": {"type": "Polygon", "crs": {"type": "name", "properties": {"name": "EPSG:4326"}}, "coordinates": [[[-7.94552469, 31.63119316], [-6.78825378, 31.61638832], [-6.81110668, 30.62639046], [-7.95642853, 30.64063072], [-7.94552469, 31.63119316]]]}, "bbox": [-7.95642853, 30.62639046, -6.78825378, 31.63119316], "centroid": [-7.3753539, 31.12950817], "assets": {"thumbnail": {"name": "thumbnail", "href": "https://theia.cnes.fr/data//Snow/2023/04/11/SENTINEL2A_20230411-112240-616_L2B-SNOW_T29RPQ_D_V1-9/SENTINEL2A_20230411-112240-616_L2B-SNOW_T29RPQ_D_V1-9_THB_ALL.png", "relative_href": null, "object_store": null, "title": "thumbnail", "description": "thumbnail", "type": "image/png", "roles": ["thumbnail"], "extra_fields": null, "gsd": null, "eo": null, "sar": null, "proj": null}, "overview": {"name": "overview", "href": "https://theia.cnes.fr/data//Snow/2023/04/11/SENTINEL2A_20230411-112240-616_L2B-SNOW_T29RPQ_D_V1-9/SENTINEL2A_20230411-112240-616_L2B-SNOW_T29RPQ_D_V1-9_QKL_ALL.png", "relative_href": null, "object_store": null, "title": "overview", "description": "overview", "type": "image/png", "roles": ["overview"], "extra_fields": null, "gsd": null, "eo": null, "sar": null, "proj": null}, "data": {"name": "data", "href": "https://theia.cnes.fr/atdistrib/resto2/collections/Snow/27ede16d-45a1-505b-b28d-008b1880fbfd/download?issuerId=theia", "relative_href": null, "object_store": null, "title": "data", "description": "data", "type": "application/zip", "roles": ["data"], "extra_fields": null, "gsd": null, "eo": {"bands": []}, "sar": null, "proj": null}}, "properties": {"datetime": "2023-04-11T11:22:40+00:00", "start_datetime": null, "end_datetime": "2023-04-11T11:22:40+00:00", "view": null, "storage": null, "eo": null, "programme": null, "constellation": "Snow", "instrument": null, "sensor": null, "sensor_type": "OPTICAL", "gsd": 20.0, "data_type": null, "data_coverage": null, "water_coverage": 0.0, "locations": null, "create_datetime": 1681212160, "update_datetime": 1681815707, "processing": null, "cube": null, "sar": null, "proj": null, "generated": null, "snow_coverage": 0.76178247583784, "cloud_coverage": 0.020922292892193, "begin_datetime": 1681212160, "level": "LEVEL 2B"}}'
