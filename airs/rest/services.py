from fastapi import APIRouter, File, Request, UploadFile, status
from fastapi.responses import JSONResponse, Response

import airs.core.product_registration as rs
from airs.core import exceptions
from airs.core.models.mapper import to_json
from airs.core.models.model import Item
from common.exception import BadRequest, Conflict, NotFound, ServerError

ROUTER = APIRouter()

__INVALID_COLLECTION_MSG__ = "Invalid collection"
__INVALID_ASSET_MSG__ = "Invalid asset {}: {}"
__INVALID_ITEM_MSG__ = "Invalid items {}: {}"


@ROUTER.post('/collections/{collection}/_init', description="Init a collection.")
def init_collection(collection: str, request: Request) -> str:
    if not collection:
        raise BadRequest(detail=__INVALID_COLLECTION_MSG__)
    return JSONResponse(content={"created": rs.init_collection(collection)},
                        status_code=status.HTTP_201_CREATED
                        )


@ROUTER.post('/collections/{collection}/items', description="Create an item. item.id must be set. Asset must exist (depends on the server configuration)")
def create_item(collection: str, item: Item, request: Request) -> str:
    """ From https://github.com/stac-api-extensions/transaction:
        POST
        When the body is a partial Item:
            Must only create a new resource.
            Must have an id field.
            Must return 409 if an Item exists for the same collection and id field values.
            Must populate the collection field in the Item from the URI.
            Must return 201 and a Location header with the URI of the newly added resource for a successful operation.
            May return the content of the newly added resource for a successful operation.
    """
    if not item.id:
        raise BadRequest(detail="Invalid identifier")
    if not item.catalog:
        raise BadRequest(detail="Invalid catalog")
    if not item.collection:
        raise BadRequest(detail=__INVALID_COLLECTION_MSG__)
    if not item.collection == collection:
        raise BadRequest(detail="Invalid collection in the item, must be the same as the one provided in the url")
    if rs.item_exists(item.collection, item.id):
        raise Conflict(detail="Item already exists")
    try:
        return Response(content=to_json(rs.register_item(item=item)),
                        status_code=status.HTTP_201_CREATED,
                        headers={"Location": request.base_url.path + "/" + rs.get_item_relative_path(collection, item.id)})
    except exceptions.InvalidAssetsException as e:
        raise NotFound(detail=__INVALID_ASSET_MSG__.format(e.assets, e.reason))
    except exceptions.InvalidItemsException as e:
        raise NotFound(detail=__INVALID_ITEM_MSG__.format(e.items, e.reason))


@ROUTER.put('/collections/{collection}/items/{id}', description="Update an item. Asset should/must exist (depends on the server configuration)")
def update_item(collection: str, id: str, item: Item, request: Request) -> str:
    """ From https://github.com/stac-api-extensions/transaction:
        PUT
        Must populate the id and collection fields in the Item from the URI.
        Must return 200 or 204 for a successful operation.
        If 200 status code is returned, the server shall return the content of the updated resource for a successful operation.
        Must return 202 if the operation is queued for asynchronous execution.
        Must return 404 if no Item exists for this resource URI.
        If the id or collection fields are different from those in the URI, status code 400 shall be returned.
    """
    if not item.id:
        raise BadRequest(detail="Invalid identifier")
    if not id == item.id:
        raise BadRequest(detail="Invalid identifier, must be equal in the body and the URI")
    if not item.catalog:
        raise BadRequest(detail="Invalid catalog")
    if not item.collection:
        raise BadRequest(detail=__INVALID_COLLECTION_MSG__)
    if not item.collection == collection:
        raise BadRequest(detail="Invalid collection in the item, must be the same as the one provided in the url")
    if not rs.item_exists(collection, item.id):
        raise BadRequest(detail="Item does not exist, can not update")
    try:
        return Response(content=to_json(rs.register_item(item=item)),
                        status_code=status.HTTP_200_OK,
                        headers={"Location": request.base_url.path + "/" + rs.get_item_relative_path(collection, item.id)})
    except exceptions.InvalidAssetsException as e:
        raise NotFound(detail=__INVALID_ASSET_MSG__.format(e.assets, e.reason))
    except exceptions.InvalidItemsException as e:
        raise NotFound(detail=__INVALID_ITEM_MSG__.format(e.items, e.reason))


@ROUTER.delete('/collections/{collection}/items/{id}', description="Delete an item and its assets (depends on the server configuration)")
def delete_item(collection: str, id: str) -> str:
    """ From https://github.com/stac-api-extensions/transaction:
        DELETE
        Must return 200 or 204 for a successful operation.
        Must return a 202 if the operation is queued for asynchronous execution.
        May return a 404 if no Item existed prior to the delete operation. Returning a 200 or 204 is also valid in this situation.
    """
    if not rs.item_exists(collection, id):
        raise NotFound(detail="Item does not exist, can not update")
    try:
        rs.delete_item(collection, id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except exceptions.InvalidAssetsException as e:
        raise NotFound(detail=__INVALID_ASSET_MSG__.format(e.assets, e.reason))
    except exceptions.InvalidItemsException as e:
        raise NotFound(detail=__INVALID_ITEM_MSG__.format(e.items, e.reason))


@ROUTER.get('/collections/{collection}/items/{id}', description="Retrieve an item")
def get_item(collection: str, id: str) -> str:
    if not rs.item_exists(collection, id):
        raise NotFound(detail="Item does not exist")
    try:
        return Response(content=to_json(rs.get_item(collection, id)), status_code=status.HTTP_200_OK)
    except exceptions.InvalidAssetsException as e:
        raise NotFound(detail=__INVALID_ASSET_MSG__.format(e.assets, e.reason))
    except exceptions.InvalidItemsException as e:
        raise NotFound(detail=__INVALID_ITEM_MSG__.format(e.items, e.reason))


@ROUTER.post('/collections/{collection}/items/{item_id}/assets/{asset_name}', description="Upload an asset.")
async def upload_asset(collection: str, item_id: str, asset_name: str, file: UploadFile = File(...)):
    upload_obj = rs.upload_asset(collection=collection, item_id=item_id, asset_name=asset_name, file=file.file, content_type=file.content_type)
    if upload_obj:
        return JSONResponse(content={"msg": "Object has been uploaded to bucket successfully"},
                            status_code=status.HTTP_201_CREATED)
    else:
        raise ServerError(detail="File could not be uploaded")


@ROUTER.head('/collections/{collection}/items/{item_id}/assets/{asset_name}', description="Tests if an asset exists.")
async def retrieve_asset(collection: str, item_id: str, asset_name: str):
    if rs.asset_exists(collection=collection, item_id=item_id, asset_name=asset_name):
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise NotFound(detail="Asset not found")


@ROUTER.delete('/collections/{collection}/items/{item_id}/assets/{asset_name}', description="Delete an asset.")
async def delete_asset(collection: str, item_id: str, asset_name: str):
    if rs.asset_exists(collection=collection, item_id=item_id, asset_name=asset_name):
        rs.delete_asset(collection, item_id, asset_name)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise NotFound(detail="Asset not found")


@ROUTER.post('/collections/{collection}/_reindex', description="Reindex a collection")
async def reindex_asset(collection: str):
    rs.reindex(collection=collection)
    return Response(status_code=status.HTTP_200_OK)
