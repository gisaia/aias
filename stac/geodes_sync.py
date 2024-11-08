import json
import sys

import requests
import typer

from airs.core.models.mapper import item_from_dict, to_json
from airs.core.models.model import Asset, AssetFormat, Item, Role

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
app = typer.Typer(add_completion=False, no_args_is_help=True)


def to_item(feature, extra_params={}) -> Item:
    feature["centroid"] = [
        feature.get("centroid").get("lon"),
        feature.get("centroid").get("lat"),
    ]
    # CLEANING
    feature.pop("stac_version")
    feature.pop("stac_extensions")
    feature.pop("links")

    # TO ITEM
    item = item_from_dict(feature)
    item.collection = extra_params.get("collection")
    item.catalog = extra_params.get("catalog")
    item.properties.programme = "Copernicus"
    item.properties.constellation = "Sentinel-2"
    item.properties.processing__level = feature.get("properties").get("spaceborne:productLevel")
    item.properties.sensor = feature.get("properties").get("spaceborne:sensorMode")
    item.properties.data_type = feature.get("properties").get("dataType")
    item.properties.item_type = feature.get("properties").get("spaceborne:productType")
    item.properties.eo__cloud_cover = feature.get("properties").get("spaceborne:cloudCover")
    item.properties.platform = feature.get("properties").get("spaceborne:satellitePlatform")
    item.properties.sensor = feature.get("properties").get("spaceborne:satelliteSensor")
    item.properties.acq__acquisition_orbit = feature.get("properties").get("spaceborne:orbitID")
    item.properties.acq__acquisition_orbit_direction = feature.get("properties").get("spaceborne:orbitDirection")

    for name, asset in item.assets.items():
        asset: Asset = asset
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
                asset.asset_format = AssetFormat.xml.value
                asset.roles = [Role.metadata.value]
            if asset.type == "application/zip":
                name = Role.data.value
                asset.asset_format = AssetFormat.zip.value
                asset.roles = [Role.data.value]
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
                item.properties.locations.append(country.get("name"))
    if item.properties.model_extra.get("spaceborne__political"):
        item.properties.model_extra.pop("spaceborne__political")
    if item.properties.model_extra.get("spaceborne__references"):
        item.properties.model_extra.pop("spaceborne__references")
    item.properties.model_extra.clear()
    return item


def search(stac_url: str, start_date: int, end_date: int, data_type: list[str], product_level: list[str], bbox: list[float], max_hits: int, just_count: bool = False, process_function=None, extra_params={}):
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
    to_do = max_hits
    while page:
        data["page"] = page
        r = requests.post(url=stac_url, headers=headers, data=json.dumps(data), verify=False)
        if r.ok:
            doc = r.json()
            to_do = min(doc.get("context", {}).get("matched", 0), max_hits)
            if just_count:
                print("{} items found.".format(doc.get("context", {}).get("matched", 0)))
                return
            for feature in doc.get("features", []):
                item = to_item(feature, extra_params)
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


@app.command(help="Add STAC features to ARLAS AIRS")
def add(
    stac_url: str = typer.Argument(help="STAC URL (e.g. https://geodes-portal.cnes.fr/api/stac/)"),
    airs_url: str = typer.Argument(help="AIRS url (e.g. https://localhost/airs/)"),

    collection: str = typer.Argument(help="Name of the ARLAS Collection)"),
    catalog: str = typer.Argument(help="Name of the catalog within the collection)"),
    data_type: list[str] = typer.Option(help="Data type ()", default=None),
    product_level: list[str] = typer.Option(help="Product levels", default=None),
    start_date: str = typer.Option(help="Start date for the STAC search", default=None),
    end_date: str = typer.Option(help="End date for the STAC search", default=None),
    bbox: list[float] = typer.Option(help="BBOX (lon_min lat_min lon max lat_max)", default=None),
    max: int = typer.Option(help="Max number of feature to process", default=1000)
):
    try:
        search(stac_url, start_date, end_date, data_type, product_level, bbox, max, process_function=lambda i: add_to_airs(airs_url=airs_url, collection=collection, item=i), extra_params={"collection": collection, "catalog": catalog})
    except Exception as e:
        print("ERROR: Failled to add items: {}".format(e), file=sys.stderr)


@app.command(help="Show STAC features")
def show(
    stac_url: str = typer.Argument(help="STAC URL (e.g. https://geodes-portal.cnes.fr/api/stac/items)"),
    data_type: list[str] = typer.Option(help="Data type ()", default=None),
    product_level: list[str] = typer.Option(help="Product levels", default=None),
    start_date: str = typer.Option(help="Start date for the STAC search", default=None),
    end_date: str = typer.Option(help="End date for the STAC search", default=None),
    bbox: list[float] = typer.Option(help="BBOX (lon_min lat_min lon max lat_max)", default=None),
    max: int = typer.Option(help="Max number of feature to process", default=1000)
):
    search(stac_url, start_date, end_date, data_type, product_level, bbox, max, process_function=lambda i: print(to_json(i)))


@app.command(help="Count STAC features")
def count(
    stac_url: str = typer.Argument(help="STAC URL (e.g. https://geodes-portal.cnes.fr/api/stac/items)"),
    data_type: list[str] = typer.Option(help="Data type ()", default=None),
    product_level: list[str] = typer.Option(help="Product levels", default=None),
    start_date: str = typer.Option(help="Start date for the STAC search", default=None),
    end_date: str = typer.Option(help="End date for the STAC search", default=None),
    bbox: list[float] = typer.Option(help="BBOX (lon_min lat_min lon max lat_max)", default=None),
    max: int = typer.Option(help="Max number of feature to process", default=1000)
):
    search(stac_url, start_date, end_date, data_type, product_level, bbox, max, just_count=True)


def main():
    app()


if __name__ == "__main__":
    main()