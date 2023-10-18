
def setup_gdal():
    from osgeo import gdal
    gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN', 'YES')
    gdal.UseExceptions()
    gdal.PushErrorHandler('CPLQuietErrorHandler')
    gdal.VSICurlClearCache()

def get_id(url):
    id = str(url.replace("/", "-").replace(" ","_"))
    if id[0] == "-":
        return id[1:]
    return id

def get_geom_bbox_centroid(ul_lon,ul_lat,ur_lon,ur_lat,lr_lon,lr_lat,ll_lon,ll_lat):
    import json
    from osgeo import ogr
    coordinates = [[ul_lon, ul_lat],
                   [ur_lon, ur_lat],
                   [lr_lon, lr_lat],
                   [ll_lon, ll_lat]]
    bbox = [min(map(lambda xy: xy[0], coordinates)),
            min(map(lambda xy: xy[1], coordinates)),
            max(map(lambda xy: xy[0], coordinates)),
            max(map(lambda xy: xy[1], coordinates))]
    coordinates.append(coordinates[0])
    # Define geometry
    geometry = {
        "type": "Polygon",
        "coordinates": [coordinates]
    }
    geom = ogr.CreateGeometryFromJson(json.dumps(geometry))
    centroid_geom = geom.Centroid()
    centroid_geom_list = str(centroid_geom).replace("(", "").replace(")", "").split(" ")
    # Define centroid
    centroid = [float(centroid_geom_list[1]), float(centroid_geom_list[2])]
    return geometry, bbox, centroid
