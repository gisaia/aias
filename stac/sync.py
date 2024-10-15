import sys
import json
import requests
import typer

from airs.core.models.mapper import item_from_dict, to_json
from airs.core.models.model import Item

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
app = typer.Typer(add_completion=False, no_args_is_help=True)


def to_item(feature) -> Item:
    feature["centroid"] = [
        feature.get("centroid").get("lat"),
        feature.get("centroid").get("lon"),
    ]
    # CLEANING
    feature.pop("stac_version")
    feature.pop("stac_extensions")
    feature.pop("links")
    # ASSETS
    assets = {}
    for name, asset in feature.get("assets", {}).items():
        if (
            len(asset.get("roles", [])) == 1
            and assets.get(asset.get("roles")[0]) is None
        ):
            name = asset.get("roles")[0]
        assets[name] = asset
    feature["assets"] = assets
    # MOVE AROUND
    item = item_from_dict(feature)
    item.properties.programme = "Copernicus"
    item.properties.constellation = "Sentinel-2"
    item.properties.processing__level = feature.get("properties").get(
        "spaceborne:productLevel"
    )
    return item


def search(stac_url: str, start_date: int, end_date: int, bbox: list[float], max: int, process_function):
    data = {
        "sortBy": [{"direction": "desc", "field": "temporal:startDate"}],
        "limit": 50,
        "page": 1,
        "query": {
            "dataType": {
                "in": ["PEPS_S2_L1C", "MUSCATE_SENTINEL2_SENTINEL2_L2A", "MUSCATE_Snow_SENTINEL2_L2B-SNOW", "MUSCATE_WaterQual_SENTINEL2_L2B-WATER", "MUSCATE_SENTINEL2_SENTINEL2_L3A"]
            },
            "spaceborne:productType": {"in": ["REFLECTANCE", "REFLECTANCETOA", "S2MSI1C"]},
            "spaceborne:productLevel": {"in": ["L1C"]}
        }
    }
    if start_date: 
        data["query"]["temporal:startDate"] = start_date
    if end_date: 
        data["query"]["temporal:endDate"] = end_date
    if bbox:
        data["bbox"] = bbox
    headers = {"content-type": "application/json"}
    page = 1
    count = 1
    while page:
        data["page"] = page
        print(json.dumps(data))
        r = requests.post(url=stac_url, headers=headers, data=json.dumps(data), verify=False)
        if r.ok:
            doc = r.json()
            for feature in doc.get("features", []):
                item = to_item(feature)
                process_function(item)
                count = count + 1
                if count > max:
                    return
            pages = list(filter(lambda link: link.get("rel") == "next", doc.get("links", [])))
            if len(pages) > 0:
                page = page + 1
            else:
                page = None
        else:
            page = None
            print("Failed to fetch items from {}: {} ({})".format(stac_url, r.status_code, r.content), file=sys.stderr)


def add_to_airs(airs_url: str, collection: str, item: Item):
    requests.post("/".join([airs_url, "collections", collection, "items"]), )
    r = requests.post(url="/".join(airs_url, "collections", collection, "items"), data=to_json(item), headers={"Content-Type": "application/json"})
    if r.status_code >= 200 and r.status_code < 300:
        print("{} added".format(item.id))
    else:
        print("ERROR: Failled to add {}: {} ({})".format(item.id, r.status_code, r.content), file=sys.stderr)


@app.command(help="Add STAC features to ARLAS AIRS")
def add(
    stac_url: str = typer.Argument(help="STAC URL (e.g. https://geodes-portal.cnes.fr/api/stac/)"),
    airs_url: str = typer.Argument(help="AIRS url (e.g. https://localhost/airs/)"),
    collection: str = typer.Argument(help="Name of the ARLAS Collection)"),
    start_date: int = typer.Option(help="Start date for the STAC search", default=None),
    end_date: int = typer.Option(help="End date for the STAC search", default=None),
    bbox: list[float] = typer.Option(help="BBOX (lon_min lat_min lon max lat_max)", default=None),
    max: int = typer.Option(help="Max number of feature to process", default=1000)
):
    search(stac_url, start_date, end_date, bbox, max, lambda i: add_to_airs(airs_url=airs_url, collection=collection, item=i))


@app.command(help="Add STAC features to ARLAS AIRS")
def show(
    stac_url: str = typer.Argument(help="STAC URL (e.g. https://geodes-portal.cnes.fr/api/stac/)"),
    start_date: int = typer.Option(help="Start date for the STAC search", default=None),
    end_date: int = typer.Option(help="End date for the STAC search", default=None),
    bbox: list[float] = typer.Option(help="BBOX (lon_min lat_min lon max lat_max)", default=None),
    max: int = typer.Option(help="Max number of feature to process", default=1000)
):
    search(stac_url, start_date, end_date, bbox, max, lambda i: print(to_json(i)))


def main():
    app()


if __name__ == "__main__":
    main()