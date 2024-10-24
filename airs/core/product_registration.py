import json
import os
from datetime import datetime

import elasticsearch
import pygeohash as pgh
import pytz
import requests

import airs.core.exceptions as exceptions
import airs.core.geo as geo
import airs.core.s3 as s3
import airs.core.utils as utils
from airs.core.logger import Logger
from airs.core.models.mapper import (item_from_dict, item_from_json_file,
                                     to_airs_item, to_airs_json, to_json)
from airs.core.models.model import Asset, Band, Item, Properties, Role
from airs.core.settings import Configuration

ASSETS_NOT_FOUND = "Asset(s) not found"
ITEM_ARLAS_SUFFIX = ".airs.json"
LOGGER = Logger.logger


def get_asset_relative_path(collection: str, item_id: str, asset_name: str) -> str:
    """return the relative path to the asset file

    Args:
        collection (str): collection name
        catalog (str): catalog name
        item_id (str): item id
        asset_name (str): asset name

    Returns:
        str: relative path to the asset
    """
    if asset_name == Role.airs_item.value:
        return os.path.join(collection, "items", item_id, item_id + ITEM_ARLAS_SUFFIX)
    else:
        return os.path.join(collection, "items", item_id, "assets", asset_name)


def get_assets_relative_path(collection: str, item_id: str) -> str:
    """return the relative path to the assets directory of an item

    Args:
        collection (str): collection name
        catalog (str): catalog name
        item_id (str): item id

    Returns:
        str: relative path to the asset
    """
    return os.path.join(collection, "items", item_id, "assets")


def get_item_relative_path(collection: str, item_id: str) -> str:
    """return the relative path to the item file

    Args:
        collection (str): collection name
        catalog (str): catalog name
        item_id (str): item id

    Returns:
        str: relative path to the item file
    """
    return os.path.join(collection, "items", item_id, item_id + ITEM_ARLAS_SUFFIX)


def upload_asset(
    collection: str, item_id: str, asset_name: str, file, content_type: str
) -> str:
    """upload the asset file to the configured S3

    Args:
        collection (str): collection name
        catalog (str): catalog name
        item_id (str): item id
        asset_name (str): asset name
        file (_type_): file
        content_type (str): asset content type

            Raises:
        exceptions.InternalError: if an internal error is encountered

    Returns:
        str: key, None if not uploaded
    """
    key = get_asset_relative_path(collection, item_id, asset_name)
    return __upload_file(key, file, content_type)


def delete_asset(collection: str, item_id: str, asset_name: str):
    """delete the asset file from the configured S3

    Args:
        collection (str): collection name
        catalog (str): catalog name
        item_id (str): item id
        asset_name (str): asset name

            Raises:
        exceptions.InternalError: if an internal error is encountered

    """
    key = get_asset_relative_path(collection, item_id, asset_name)
    return __delete_file(key)


def upload_item(item: Item):
    """upload the item to the configured S3

    Args:
        item (Item): the item to upload

    Raises:
        exceptions.InternalError: if an internal error is encountered

    Returns:
        str: key, None if not uploaded
    """
    item = to_airs_item(item)
    key = get_item_relative_path(item.collection, item.id)
    return __upload_item(key, item)


def __upload_file(key, file, content_type) -> str:
    try:
        LOGGER.info("uploading {} ...".format(key))
        s3.get_client().upload_fileobj(
            file,
            Configuration.settings.s3.bucket,
            key,
            ExtraArgs={"ContentType": content_type},
        )
        LOGGER.info("{} uploaded.".format(key))
        return key
    except Exception as e:
        LOGGER.error("Failed to upload {}".format(key))
        LOGGER.exception(e)
        raise exceptions.InternalError("storage", e)


def __delete_file(key):
    try:
        LOGGER.info("deleting {} ...".format(key))
        s3.get_client().delete_object(Bucket=Configuration.settings.s3.bucket, Key=key)
        LOGGER.info("{} deleted.".format(key))
    except Exception as e:
        LOGGER.error("Failed to delete {} ".format(key))
        LOGGER.exception(e)
        raise exceptions.InternalError("storage", e)


def __delete_prefix(prefix: str):
    try:
        LOGGER.info("deleting {} ...".format(prefix))
        objects = s3.get_client().list_objects(
            Bucket=Configuration.settings.s3.bucket, Prefix=prefix
        )
        for object in objects["Contents"]:
            LOGGER.info("deleting {} ...".format(object["Key"]))
            objects = s3.get_client().delete_object(
                Bucket=Configuration.settings.s3.bucket, Key=object["Key"]
            )
            LOGGER.info("{} deleted.".format(object["Key"]))
        LOGGER.info("{} deleted.".format(prefix))
    except Exception as e:
        LOGGER.error("Failed to delete {} ".format(prefix))
        LOGGER.exception(e)
        raise exceptions.InternalError("storage", e)


def __upload_item(key, item: Item) -> str:
    try:
        LOGGER.info("uploading {} ...".format(key))
        s3.get_client().put_object(
            Bucket=Configuration.settings.s3.bucket,
            Key=key,
            Body=to_json(item),
            ContentType="application/json",
        )
        LOGGER.info("{} uploaded.".format(key))
        return key
    except Exception as e:
        LOGGER.error(
            "Failed to upload {} on bucket {}".format(
                key, Configuration.settings.s3.bucket
            )
        )
        LOGGER.exception(e)
        raise exceptions.InternalError("storage", e)


def asset_exists(collection: str, item_id: str, asset_name: str) -> bool:
    """check whether the asset exists or not on the configured S3

    Args:
        collection (str): collection name
        catalog (str): catalog name
        item_id (str): item id
        asset_name (str): asset name

    Returns:
        bool: True if found on the S3, False otherwise
    """
    key = get_asset_relative_path(collection, item_id, asset_name)
    try:
        h = s3.get_client().head_object(
            Bucket=Configuration.settings.s3.bucket, Key=key
        )
        LOGGER.info(h)
        return True
    except Exception as e:
        LOGGER.debug(e)
        return False


def delete_item(collection: str, item_id: str):
    if not __getES().indices.exists(index=__get_es_index_name(collection)):
        raise exceptions.InvalidItemsException(
            [item_id], reason="Collection does not exist"
        )
    __getES().delete(index=__get_es_index_name(collection), id=item_id)
    prefix = get_assets_relative_path(collection, item_id)
    __delete_prefix(prefix)
    LOGGER.info("deleting {} ...".format(get_item_relative_path(collection, item_id)))
    s3.get_client().delete_object(
        Bucket=Configuration.settings.s3.bucket,
        Key=get_item_relative_path(collection, item_id),
    )
    LOGGER.info("{} deleted.".format(get_item_relative_path(collection, item_id)))


def __fetch_mapping__():
    if Configuration.settings.arlaseo_mapping_url.startswith("http"):
        r = requests.get(Configuration.settings.arlaseo_mapping_url, verify=False)
        if r.ok:
            return r.json()["mappings"]
        else:
            LOGGER.error(
                "Can not fetch the mapping for creating the ARLAS index. Aborting ..."
            )
            raise exceptions.InternalError("elasticsearch", r.reason)
    else:
        with open(Configuration.settings.arlaseo_mapping_url) as f:
            return json.load(f)["mappings"]


def init_collection(collection: str) -> bool:
    if not __getES().indices.exists(index=__get_es_index_name(collection)):
        LOGGER.info(
            "Index {} does not exists. Attempt to create it with mapping from {}".format(
                __get_es_index_name(collection),
                Configuration.settings.arlaseo_mapping_url,
            )
        )
        mapping = __fetch_mapping__()
        __getES().indices.create(
            index=__get_es_index_name(collection), mappings=mapping
        )
        LOGGER.info("Index {} created.".format(__get_es_index_name(collection)))
        return True
    else:
        LOGGER.debug("Index {} found.".format(__get_es_index_name(collection)))
        return False


def register_item(item: Item) -> Item:
    """Register an item

    Args:
        collection (str): collection name
        catalog (str): catalog name
        item_id (str): item id
        check_assets_links (bool, optional): If True, the service checks that the assets exist, if not an exception is raised. Defaults to True.

    Raises:
        exceptions.InvalidAssetsException: if an asset is not found
        exceptions.InternalError: if an internal error is encountered

    Returns:
        Item: The registered item
    """
    item = to_airs_item(item)
    __check_register_item_params(item)
    for asset in item.assets.values():
        if asset.airs__managed is None:
            asset.airs__managed = True
    not_found = __not_found_assets(item)
    if len(not_found) > 0:
        raise exceptions.InvalidAssetsException(not_found, ASSETS_NOT_FOUND)
    __set_assets_links(item)
    LOGGER.info("Indexing {} in ARLAS".format(item.id))
    __dates_to_times(item)
    __collect_bands(item)
    __add_generated_fields(item)
    upload_item(item)
    init_collection(item.collection)
    resp = __getES().index(
        index=__get_es_index_name(item.collection),
        id=item.id,
        document=to_airs_json(item),
    )
    LOGGER.info("Indexing result:{}".format(resp["result"]))
    return item


def reindex(collection: str):
    """Reindex a collection based on the object storage
    Args:
        collection (str): name of the collection to reindex
    """
    keys = s3.get_matching_s3_objects(
        Configuration.settings.s3.bucket, collection, ITEM_ARLAS_SUFFIX
    )
    LOGGER.info("Start reindexing collection {}".format(collection))
    for key in keys:
        tmp_file = "tmp" + ITEM_ARLAS_SUFFIX
        LOGGER.info("Reindexing item from {}".format(key))
        LOGGER.info(
            s3.get_client().download_file(
                Configuration.settings.s3.bucket, key, tmp_file
            )
        )
        with open(tmp_file, "r") as f:
            item = item_from_json_file(f)
            LOGGER.debug(item)
            register_item(item)
        os.remove(tmp_file)
    LOGGER.info("Done with reindexing collection {}".format(collection))


def item_exists(collection: str, item_id: str) -> bool:
    if not __getES().indices.exists(index=__get_es_index_name(collection)):
        LOGGER.info("index {} does not exists".format(__get_es_index_name(collection)))
        return False
    try:
        __getES().get(index=__get_es_index_name(collection), id=item_id)
    except elasticsearch.NotFoundError:
        return False
    return True


def get_item(collection: str, item_id: str) -> Item:
    if not __getES().indices.exists(index=__get_es_index_name(collection)):
        raise exceptions.InvalidItemsException(
            [item_id], reason="Collection does not exist"
        )
    r = __getES().get(index=__get_es_index_name(collection), id=item_id)
    return item_from_dict(r["_source"])


def __collect_bands(item: Item) -> Item:
    bands: dict[str, Band] = {}
    item.properties.eo__bands = item.properties.eo__bands or {}
    for band in item.properties.eo__bands:
        bands[band.name] = band
    if item.assets is not None:
        for asset in item.assets.values():
            if asset.eo__bands is not None:
                for band in asset.eo__bands:
                    bands[band.name] = band
    item.properties.eo__bands = list(bands.values())
    return item


def __dates_to_times(item: Item) -> Item:
    item.properties.datetime = int(item.properties.datetime.timestamp())
    if item.properties.start_datetime is not None:
        item.properties.start_datetime = int(item.properties.start_datetime.timestamp())
    if item.properties.end_datetime is not None:
        item.properties.end_datetime = int(item.properties.end_datetime.timestamp())
    return item


def __add_generated_fields(item: Item) -> Item:
    if item.centroid:
        item.properties.generated__geohash2 = pgh.encode(
            item.centroid[1], item.centroid[0], precision=2
        )
        item.properties.generated__geohash3 = pgh.encode(
            item.centroid[1], item.centroid[0], precision=3
        )
        item.properties.generated__geohash4 = pgh.encode(
            item.centroid[1], item.centroid[0], precision=4
        )
        item.properties.generated__geohash5 = pgh.encode(
            item.centroid[1], item.centroid[0], precision=5
        )
    if item.assets is not None:
        for asset in item.assets.values():
            if Role.overview.value in asset.roles:
                item.properties.generated__has_overview = True
            if Role.thumbnail.value in asset.roles:
                item.properties.generated__has_thumbnail = True
            if Role.data in asset.roles:
                item.properties.generated__has_data = True
            if Role.metadata.value in asset.roles:
                item.properties.generated__has_metadata = True
            if Role.cog.value in asset.roles:
                item.properties.generated__has_cog = True
            if Role.zarr.value in asset.roles:
                item.properties.generated__has_zarr = True
    acquisition = datetime.fromtimestamp(item.properties.datetime)
    try:
        acquisition = pytz.UTC.localize(acquisition)
    except Exception:
        ...  # LOGGER.error("Can not localize {}: {}".format(acquisition, e))
    item.properties.generated__day_of_week = acquisition.weekday()
    item.properties.generated__day_of_year = int(acquisition.strftime("%j"))
    item.properties.generated__hour_of_day = acquisition.hour
    item.properties.generated__minute_of_day = (
        acquisition.hour * 60 + acquisition.minute
    )
    item.properties.generated__season = utils.Utils.get_season(acquisition)
    item.properties.generated__month = acquisition.month
    item.properties.generated__year = acquisition.year
    if item.geometry and item.geometry["coordinates"]:
        if (
            item.geometry["type"].lower() == "polygon"
            and item.geometry["coordinates"][0]
        ):
            item.properties.generated__tltrbrbl = geo.getCorners(
                item.geometry["coordinates"][0]
            ).tltrbrbl()
        if (
            item.geometry["type"].lower() == "multipolygon"
            and item.geometry["coordinates"][0]
            and item.geometry["coordinates"][0][0]
        ):
            item.properties.generated__tltrbrbl = geo.getCorners(
                item.geometry["coordinates"][0][0]
            ).tltrbrbl()
    item.properties.generated__band_names = list(
        filter(
            lambda name: name is not None,
            map(lambda band: band.name, item.properties.eo__bands),
        )
    )
    item.properties.generated__band_common_names = list(
        filter(
            lambda common_name: common_name is not None,
            map(lambda band: band.common_name, item.properties.eo__bands),
        )
    )
    return item


def __set_assets_links(item: Item) -> Item:
    for asset_name in item.assets:
        asset = item.assets[asset_name]
        if asset.airs__managed is True:
            LOGGER.info("Asset {} is maneged".format(asset_name))
            object_relative_path = get_asset_relative_path(
                item.collection, item.id, asset_name
            )
            asset.name = asset_name
            asset.href = Configuration.settings.s3.asset_http_endpoint_url.format(
                Configuration.settings.s3.bucket, object_relative_path
            )
            asset.airs__object_store_bucket = Configuration.settings.s3.bucket
            asset.airs__object_store_key = object_relative_path
            asset.storage__platform = Configuration.settings.s3.platform
            asset.storage__tier = Configuration.settings.s3.tier
        else:
            LOGGER.info("Asset {} is not maneged".format(asset_name))
    item_relative_path = get_item_relative_path(item.collection, item.id)
    item.assets[Role.airs_item.value] = Asset(
        name=Role.airs_item.value,
        href=Configuration.settings.s3.asset_http_endpoint_url.format(
            Configuration.settings.s3.bucket, item_relative_path
        ),
        description="ARLAS item for {}".format(item.id),
        title="ARLAS item for {}".format(item.id),
        type="application/json",
        roles=[Role.airs_item.value],
    )
    item.assets[Role.airs_item.value].airs__managed = True
    item.assets[Role.airs_item.value].airs__object_store_bucket = (
        Configuration.settings.s3.bucket
    )
    item.assets[Role.airs_item.value].airs__object_store_key = item_relative_path
    item.assets[Role.airs_item.value].storage__platform = (
        Configuration.settings.s3.platform
    )
    item.assets[Role.airs_item.value].storage__tier = Configuration.settings.s3.tier
    return item


def __not_found_assets(item: Item) -> list[str]:
    not_found = []
    for asset_name in item.assets:
        asset = item.assets[asset_name]
        if asset.airs__managed is True:
            if not asset_exists(item.collection, item.id, asset_name=asset_name):
                not_found.append(
                    get_asset_relative_path(item.collection, item.id, asset_name)
                )
    return not_found


def __check_register_item_params(item: Item):
    if item.collection is None or len(item.collection) == 0:
        raise exceptions.InvalidItemsException(
            [item.id], reason="Empty collection name"
        )
    if item.catalog is None or len(item.catalog) == 0:
        raise exceptions.InvalidItemsException([item.id], reason="Empty catalog name")
    if item is None:
        raise exceptions.InvalidItemsException([], reason="Empty item")
    if item.id is None:
        raise exceptions.InvalidItemsException([], reason="Item id is not set")
    if not geo.valid_bbox(item.bbox):
        raise exceptions.InvalidItemsException(
            [item.id], reason="Item bbox is not set or is not valid"
        )
    if item.centroid is None:
        raise exceptions.InvalidItemsException(
            [item.id], reason="Item centroid is not set or is not valid"
        )
    if item.geometry is None:
        raise exceptions.InvalidItemsException(
            [item.id], reason="Item geometry is not set or is not valid"
        )
    if item.properties is None:
        item.properties = Properties()
    if (
        item.properties.datetime is None
        and item.properties.start_datetime is None
        and item.properties.end_datetime is None
    ):
        raise exceptions.InvalidItemsException(
            [item.id],
            reason="item.properties.datetime or item.properties.start_datetime and item.properties.end_datetime must be set",
        )
    if item.properties.datetime is None:
        item.properties.datetime = (
            item.properties.start_datetime
        )  # Fall back date, necessary for ARLAS
    if item.assets is None:
        item.assets = {}


def __get_es_index_name(collection: str) -> str:
    if Configuration.settings.index.collection_prefix:
        return Configuration.settings.index.collection_prefix + "_" + collection
    else:
        return collection


def __getES():
    if Configuration.settings.index.login:
        return elasticsearch.Elasticsearch(
            Configuration.settings.index.endpoint_url,
            basic_auth=(
                Configuration.settings.index.login,
                Configuration.settings.index.pwd,
            ),
            verify_certs=False,
        )
    else:
        return elasticsearch.Elasticsearch(Configuration.settings.index.endpoint_url)
