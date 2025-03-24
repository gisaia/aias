import json
import re
import sys
import zipfile

import requests
import typer
from prettytable import PrettyTable

from airs.core.models.mapper import item_from_dict, to_json
from airs.core.models.model import AssetFormat, Band, Item, ItemFormat, Role

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
app = typer.Typer(add_completion=False, no_args_is_help=True)


def to_item(feature, extra_params={}, find_bands=False) -> Item:
    feature["centroid"] = [
        feature.get("centroid").get("lon"),
        feature.get("centroid").get("lat"),
    ]
    # CLEANING
    feature.pop("stac_version")
    feature.pop("stac_extensions")
    feature.pop("links")

    fields_to_keep = {}
    # TO ITEM
    item = item_from_dict(feature)
    item.collection = extra_params.get("collection")
    item.catalog = extra_params.get("catalog")
    item.properties.programme = feature.get("properties").get("programme", "")
    item.properties.constellation = feature.get("properties").get("constellation", "")
    item.properties.processing__level = feature.get("properties").get("spaceborne:productLevel")
    item.properties.sensor_mode = feature.get("properties").get("spaceborne:sensorMode")
    item.properties.data_type = feature.get("properties").get("dataType")
    item.properties.item_type = feature.get("properties").get("spaceborne:productType")
    item.properties.eo__cloud_cover = feature.get("properties").get("spaceborne:cloudCover")
    item.properties.platform = feature.get("properties").get("spaceborne:satellitePlatform")
    item.properties.sensor = feature.get("properties").get("spaceborne:satelliteSensor")
    item.properties.acq__acquisition_orbit = feature.get("properties").get("spaceborne:orbitID")
    item.properties.acq__acquisition_orbit_direction = feature.get("properties").get("spaceborne:orbitDirection")
    item.properties.item_format = ItemFormat.safe
    fields_to_keep["accessService:endpointURL"] = feature.get("properties").get("accessService:endpointURL")

    for name, asset in item.assets.items():
        asset.airs__managed = False

    # ASSETS
    assets = {}
    md_count = 1
    for name, asset in item.assets.items():
        name = None
        if asset.roles and len(asset.roles) > 0:
            name = "-".join(asset.roles)
        if name == Role.data.value:
            if asset.type == "application/xml":
                name = Role.metadata.value + "-" + str(md_count)
                md_count = md_count + 1
                asset.asset_format = AssetFormat.xml
                asset.roles = [Role.metadata]
            if asset.type == "application/zip":
                name = Role.data.value
                asset.asset_format = AssetFormat.zip
                asset.roles = [Role.data]

                # If not online, skip the band assets registration
                # This takes between 30s and 1min per item
                if find_bands and asset.description.split("\n")[4].split(": ")[1] == 'true':
                    from extensions.aproc.proc.access.manager import \
                        AccessManager

                    print(f"Referencing bands for {item.id}")
                    with AccessManager.stream(asset.href) as fb:
                        with zipfile.ZipFile(fb) as z:
                            files = z.namelist()
                            paths = list(filter(lambda f: re.match(r".*(B\d{1,2}|TCI)\.(tif|jp2)", f), files))
                            bands = list(map(lambda f: re.findall(r"((?:FRE_|SRE_)?(?:B\d{1,2}|TCI))\.(?:tif|jp2)$", f)[0], paths))

                            asset.eo__bands = []
                            for b, p in zip(bands, paths):
                                asset.eo__bands.append(Band(
                                    asset=name, path_within_asset=p, name=b))
        if name:
            asset.name = name
            assets[name] = asset
    item.assets = assets

    # LOCATIONS
    item.properties.locations = []
    for continent in item.properties.model_extra.get("spaceborne__political", {}).get("continents", []):
        item.properties.locations.append(continent.get("name"))
        for country in continent.get("countries", []):
            item.properties.locations.append(country.get("name"))
            for region in country.get("regions", []):
                item.properties.locations.append(region.get("name"))
    item.properties.model_extra.clear()
    item.properties.model_extra.update(fields_to_keep)
    return item


def search(stac_url: str, start_date: int, end_date: int, data_type: list[str], product_level: list[str], bbox: list[float], max_hits: int, just_count: bool = False, process_function=None, extra_params={}, find_bands=False):
    data = {
        "sortBy": [{"direction": "desc", "field": "temporal:startDate"}],
        "limit": 50,
        "page": 1,
        "query": {
        }
    }
    if data_type:
        data["query"]["dataType"] = {"in": data_type}
    if product_level:
        data["query"]["spaceborne:productLevel"] = {"in": product_level}
    if start_date:
        data["query"]["temporal:endDate"] = {"gte": start_date}
    if end_date:
        data["query"]["temporal:startDate"] = {"lte": end_date}
    if bbox:
        data["bbox"] = bbox
    headers = {"content-type": "application/json"}
    page = 1
    count = 0
    while page:
        data["page"] = page
        r = requests.post(url="/".join([stac_url, "items"]), headers=headers, data=json.dumps(data), verify=False)
        if r.ok:
            doc = r.json()
            to_do = min(doc.get("context", {}).get("matched", 0), max_hits)
            if just_count:
                print("{} items found.".format(doc.get("context", {}).get("matched", 0)))
                return
            for feature in doc.get("features", []):
                item = to_item(feature, extra_params, find_bands)
                if process_function:
                    process_function(item)
                count = count + 1
                if count >= max_hits:
                    return
            pages = list(filter(lambda link: link.get("rel") == "next", doc.get("links", [])))
            if len(pages) > 0:
                page = page + 1
            else:
                page = None
            print("{} on {}".format(count, to_do))
        else:
            page = None
            print("Failed to fetch items from {}: {} ({})".format(stac_url, r.status_code, r.content), file=sys.stderr)


def add_to_airs(airs_url: str, collection: str, item: Item):
    requests.post("/".join([airs_url, "collections", collection, "items"]), )
    r = requests.post(url="/".join([airs_url, "collections", collection, "items"]), data=to_json(item), headers={"Content-Type": "application/json"}, verify=False)
    if r.status_code >= 200 and r.status_code < 300:
        print("{} added".format(item.id))
    else:
        print("ERROR: Failled to add {}: {} ({})".format(item.id, r.status_code, r.content), file=sys.stderr)


def __print_table(field_names: list[str], rows, sortby: str = None):
    tab = PrettyTable(field_names, sortby=sortby, align="l")
    tab.add_rows(rows)
    print(tab)


def list_collections(stac_url: str):
    data = '{"page":1, "limit":500}'
    headers = {"content-type": "application/json"}
    r = requests.post(url="/".join([stac_url, "collections"]), headers=headers, data=data, verify=False)
    collections = r.json().get("collections", [])
    table = [["id", "dataType", "processingLevel", "start/end", "count"]]
    for collection in collections:
        count = collection.get("summaries", {}).get("total_items", "")
        if count > 0:
            table.append([
                collection.get("id"),
                collection.get("summaries", {}).get("dataType"),
                ",".join(collection.get("summaries", {}).get("dcs:processingLevel", [])),
                collection.get("extent", {}).get("temporal", {}).get("interval", []),
                count
            ])
    return table


STAC_URL_HELP = "STAC URL (e.g. https://geodes-portal.cnes.fr/api/stac/)"
PRODUCT_LEVEL_HELP = "Product levels"
START_DATE_HELP = "Start date for the STAC search"
END_DATE_HELP = "End date for the STAC search"
BBOX_HELP = "BBOX (lon_min lat_min lon max lat_max)"
MAX_HELP = "Max number of feature to process"
FIND_BANDS_HELP = "Whether to explore the zipped archive to find all the bands contained. This increases the processing time significantly and requires to specify a configuration file for the storages through the APROC_CONFIGURATION_FILE environment variable."


@app.command(help="Add STAC features to ARLAS AIRS")
def add(
    stac_url: str = typer.Argument(help=STAC_URL_HELP),
    airs_url: str = typer.Argument(help="AIRS URL (e.g. https://localhost/airs/)"),
    collection: str = typer.Argument(help="Name of the ARLAS Collection)"),
    catalog: str = typer.Argument(help="Name of the catalog within the collection)"),
    data_type: list[str] = typer.Option(help="Data type ()", default=None),
    product_level: list[str] = typer.Option(help=PRODUCT_LEVEL_HELP, default=None),
    start_date: str = typer.Option(help=START_DATE_HELP, default=None),
    end_date: str = typer.Option(help=END_DATE_HELP, default=None),
    bbox: list[float] = typer.Option(help=BBOX_HELP, default=None),
    max: int = typer.Option(help=MAX_HELP, default=1000),
    find_bands: bool = typer.Option(help=FIND_BANDS_HELP)
):
    try:
        stac_url = stac_url.removesuffix("/items")
        search(stac_url, start_date, end_date, data_type, product_level, bbox, max, process_function=lambda i: add_to_airs(airs_url=airs_url, collection=collection, item=i), extra_params={"collection": collection, "catalog": catalog}, find_bands=find_bands)
    except Exception as e:
        print("ERROR: Failled to add items: {}".format(e), file=sys.stderr)


@app.command(help="Show STAC features")
def show(
    stac_url: str = typer.Argument(help=STAC_URL_HELP),
    data_type: list[str] = typer.Option(help="Data type ()", default=None),
    product_level: list[str] = typer.Option(help=PRODUCT_LEVEL_HELP, default=None),
    start_date: str = typer.Option(help=START_DATE_HELP, default=None),
    end_date: str = typer.Option(help=END_DATE_HELP, default=None),
    bbox: list[float] = typer.Option(help=BBOX_HELP, default=None),
    max: int = typer.Option(help=MAX_HELP, default=1000),
    find_bands: bool = typer.Option(help=FIND_BANDS_HELP)
):
    stac_url = stac_url.removesuffix("/items")
    search(stac_url, start_date, end_date, data_type, product_level, bbox, max, process_function=lambda i: print(to_json(i)), find_bands=find_bands)


@app.command(help="List collections")
def collections(
    stac_url: str = typer.Argument(help=STAC_URL_HELP),
):
    stac_url = stac_url.removesuffix("/items")
    t = list_collections(stac_url)
    __print_table(t[0], t[1:], sortby=t[0][0])


@app.command(help="Count STAC features")
def count(
    stac_url: str = typer.Argument(help=STAC_URL_HELP),
    data_type: list[str] = typer.Option(help="Data type (PEPS_S1_L1, PEPS_S1_L2, PEPS_S2_L1C, MUSCATE_SENTINEL2_SENTINEL2_L2A, MUSCATE_Snow_SENTINEL2_L2B-SNOW, MUSCATE_WaterQual_SENTINEL2_L2B-WATER, MUSCATE_SENTINEL2_SENTINEL2_L3A)", default=None),
    product_level: list[str] = typer.Option(help=PRODUCT_LEVEL_HELP, default=None),
    start_date: str = typer.Option(help=START_DATE_HELP, default=None),
    end_date: str = typer.Option(help=END_DATE_HELP, default=None),
    bbox: list[float] = typer.Option(help=BBOX_HELP, default=None),
    max: int = typer.Option(help=MAX_HELP, default=1000)
):
    stac_url = stac_url.removesuffix("/items")
    search(stac_url, start_date, end_date, data_type, product_level, bbox, max, just_count=True)


def main():
    app()


if __name__ == "__main__":
    main()
