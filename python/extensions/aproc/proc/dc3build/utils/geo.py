import json
import re

from shapely.geometry import Point, Polygon, shape
from shapely.wkt import loads


def project_polygon(polygon: Polygon, src_crs: str, dst_crs: str) -> Polygon:
    """
    Project a polygon in the desired projection
    """
    from rasterio.warp import transform_geom

    x, y = polygon.exterior.coords.xy

    return Polygon(transform_geom(
        src_crs, dst_crs,
        {
            'type': polygon.geom_type,
            'coordinates': [list(zip(x, y))]
        })["coordinates"][0])


def bbox2polygon(left: float, bottom: float,
                 right: float, top: float) -> Polygon:
    """
    Convert the corners of a bbox into a shapely polygon
    """
    lb = Point(float(left), float(bottom))
    lt = Point(float(left), float(top))
    rb = Point(float(right), float(bottom))
    rt = Point(float(right), float(top))

    return Polygon([lb, rb, rt, lt, lb])


def roi2geometry(roi: str) -> Polygon:
    """
    Convert a ROI into a shapely geometry
    """
    # If contains'(' is a WKT
    if re.match(r".*\(.*", roi):
        try:
            polygon = Polygon(loads(roi).coords)
        except Exception:
            raise ValueError("The ROI is not formatted correctly")
        if polygon.geom_type != "Polygon":
            raise TypeError("Only POLYGON geometry is supported for the ROI")
        return polygon
    # Else if is a BBOX
    if len(roi.split(",")) == 4:
        try:
            corners = roi.split(",")

            return bbox2polygon(float(corners[0]), float(corners[1]),
                                float(corners[2]), float(corners[3]))
        except Exception:
            raise TypeError("Only POLYGON geometry is supported for the ROI," +
                            "in WKT or BBOX format")
    # Else it is a geojson
    try:
        geom = shape(json.loads(roi))
        if geom.geom_type != "Polygon":
            raise TypeError("Only POLYGON geometry is supported for the ROI")
        return geom
    except Exception:
        raise TypeError("Only POLYGON geometry is supported for the ROI," +
                        "in WKT, geojson or BBOX format")
