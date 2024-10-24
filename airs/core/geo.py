from typing import Tuple


class lonlat:
    lon: float
    lat: float

    def __init__(self, coords: list[float]):
        if len(coords) == 2:
            self.lon = coords[0]
            self.lat = coords[1]
        else:
            raise ValueError("The length of the coordinate array must be 2 but is {}".format(len(coords)))


class BOX:
    no: lonlat
    ne: lonlat
    so: lonlat
    se: lonlat

    def __init__(self, no: lonlat, ne: lonlat, so: lonlat, se: lonlat):
        self.no = no
        self.ne = ne
        self.so = so
        self.se = se

    def tltrbrbl(self):
        return [[self.no.lon, self.no.lat],
                [self.ne.lon, self.ne.lat],
                [self.se.lon, self.se.lat],
                [self.so.lon, self.so.lat]]


def getCorners(polygon: list[Tuple[float, float]]) -> BOX:
    centroid = [0, 0]
    for p in polygon:
        centroid[0] = centroid[0] + p[0]
        centroid[1] = centroid[1] + p[1]
    centroid[0] = centroid[0] / len(polygon)
    centroid[1] = centroid[1] / len(polygon)

    ne = no = se = so = centroid
    for p in polygon:
        lon, lat = p
        if lon <= no[0] and lat >= no[1]:
            no = p
        if lon >= ne[0] and lat >= ne[1]:
            ne = p
        if lon <= so[0] and lat <= so[1]:
            so = p
        if lon >= se[0] and lat <= se[1]:
            se = p
    return BOX(no=lonlat(no), ne=lonlat(ne), so=lonlat(so), se=lonlat(se))


def valid_bbox(bbox: list[float]):
    if bbox is None:
        return False
    if not len(bbox) == 4:
        return False
    if bbox[0] is None or bbox[1] is None or bbox[2] is None or bbox[3] is None:
        return False
    if bbox[0] > 180 or bbox[0] < -180:
        return False
    if bbox[1] > 90 or bbox[1] < -90:
        return False
    if bbox[2] > 180 or bbox[2] < -180:
        return False
    if bbox[3] > 90 or bbox[3] < -90:
        return False
    return True
