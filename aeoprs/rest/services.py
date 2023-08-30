import logging
from datetime import datetime as Datetime

from fastapi import (Body, FastAPI, File, HTTPException, Query, UploadFile,
                     status)
from starlette.requests import Request

from fastapi.responses import (JSONResponse, Response)
from pydantic import BaseModel

from aeoprs.core.models.mapper import to_json
import aeoprs.core.product_registration as rs
from aeoprs.core import exceptions, settings
from aeoprs.core.models.model import Item
from aeoprs.core.settings import Configuration

logging.basicConfig(level=logging.INFO)

api = FastAPI(version='0.0', title='ARLAS Earth Observation Product Registration Service',
    description='ARLAS Earth Observation Product Registration Service API',
)


@api.post('/collections/{collection}/items', description="Create an item. item.id must be set. Asset must exist (depends on the server configuration)")
def create_item(collection:str, item: Item, request: Request)->str:
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid identifier")
    if not item.catalog:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid catalog")
    if not item.collection:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid collection")
    if not item.collection == collection:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid collection in the item, must be the same as the one provided in the url")
    if rs.item_exists(item.collection, item.id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                        detail="Item already exists")
    try:
        return Response(content=to_json(rs.register_item(item=item)),
                            status_code=status.HTTP_201_CREATED,
                            headers={"Location":request.base_url.path+"/"+rs.get_item_relative_path(collection, item.id)})
    except exceptions.InvalidAssetsException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid asset {}: {}".format(e.assets, e.reason))
    except exceptions.InvalidItemsException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid items {}: {}".format(e.items, e.reason))


@api.put('/collections/{collection}/items/{id}', description="Update an item. Asset should/must exist (depends on the server configuration)")
def update_item(collection:str, id:str, item: Item, request: Request)->str:
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid identifier")
    if not id==item.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid identifier, must be equal in the body and the URI")
    if not item.catalog:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid catalog")
    if not item.collection:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid collection")
    if not item.collection == collection:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid collection in the item, must be the same as the one provided in the url")
    if not rs.item_exists(item):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Item does not exist, can not update")
    try:
        return Response(content=to_json(rs.register_item(item=item)),
                            status_code=status.HTTP_200_OK,
                            headers={"Location":request.base_url.path+"/"+rs.get_item_relative_path(item)})
    except exceptions.InvalidAssetsException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid asset {}: {}".format(e.assets, e.reason))
    except exceptions.InvalidItemsException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid items {}: {}".format(e.items, e.reason))

@api.delete('/collections/{collection}/items/{id}', description="Delete an item and its assets (depends on the server configuration)")
def delete_item(collection:str, id:str)->str:
    """ From https://github.com/stac-api-extensions/transaction:
        DELETE
        Must return 200 or 204 for a successful operation.
        Must return a 202 if the operation is queued for asynchronous execution.
        May return a 404 if no Item existed prior to the delete operation. Returning a 200 or 204 is also valid in this situation.
    """
    item=Item(id=id, collection=collection)
    if not rs.item_exists(collection, id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Item does not exist, can not update")
    try:
        rs.delete_item(collection, id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except exceptions.InvalidAssetsException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid asset {}: {}".format(e.assets, e.reason))
    except exceptions.InvalidItemsException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid items {}: {}".format(e.items, e.reason))

@api.get('/collections/{collection}/items/{id}', description="Retrieve an item")
def get_item(collection:str, id:str)->str:
    item=Item(id=id, collection=collection)
    if not rs.item_exists(collection, id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Item does not exist")
    try:
        return Response(content=to_json(rs.get_item(collection, id)), status_code=status.HTTP_200_OK)
    except exceptions.InvalidAssetsException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid asset {}: {}".format(e.assets, e.reason))
    except exceptions.InvalidItemsException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid items {}: {}".format(e.items, e.reason))

@api.post('/collections/{collection}/items/{item_id}/assets/{asset_name}', description="Upload an asset.")
async def upload_asset(collection:str, item_id:str, asset_name:str, file: UploadFile = File(...)):
    upload_obj = rs.upload_asset(collection=collection, item_id=item_id, asset_name=asset_name, file=file.file, content_type=file.content_type)
    if upload_obj:
        return JSONResponse(content={"msg":"Object has been uploaded to bucket successfully"},
                            status_code=status.HTTP_201_CREATED)
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="File could not be uploaded")

@api.head('/collections/{collection}/items/{item_id}/assets/{asset_name}', description="Tests if an asset exists.")
async def retrieve_asset(collection:str, item_id:str, asset_name:str):
    if rs.asset_exists(collection=collection, item_id=item_id, asset_name=asset_name):
         return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Asset not found")

@api.delete('/collections/{collection}/items/{item_id}/assets/{asset_name}', description="Delete an asset.")
async def delete_asset(collection:str, item_id:str, asset_name:str):
    if rs.asset_exists(collection=collection, item_id=item_id, asset_name=asset_name):
         rs.delete_asset(collection, item_id, asset_name)
         return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Asset not found")

@api.post('/collections/{collection}/_reindex', description="Reindex a collection")
async def delete_asset(collection:str):
    rs.reindex(collection=collection)
