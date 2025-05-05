from abc import ABC
import mimetypes
import os
import requests
from airs.core import s3
from airs.core.models import mapper
from airs.core.models.model import Asset, Item
from aproc.core.processes.process import Process
from airs.core.settings import S3 as S3Configuration
from aias_common.access.manager import AccessManager
from extensions.aproc.proc.drivers.exceptions import ConnectionException, RegisterException

AIRS_CAN_NOT_BE_REACHED = "AIRS Service can not be reached ({})"
JSON_HEADER = {"Content-Type": "application/json"}


class ARLASServicesHelper(ABC):

    @staticmethod
    def get_item_from_arlas(arlas_url_search: str, collection: str, item_id: str, headers: dict[str, str] = {}):
        try:
            url = arlas_url_search.format(collection=collection, item=item_id)
            r = requests.get(url=url, headers={"authorization": headers.get("authorization"), "arlas-org-filter": headers.get("arlas-org-filter")})
            if r.ok:
                result = r.json()
                if result.get("hits") and len(result.get("hits")) > 0:
                    return mapper.item_from_dict(result.get("hits")[0]["data"])
                else:
                    Process.LOGGER.warn("No result found for {}/{}".format(collection, item_id))
                    return None
            else:
                Process.LOGGER.error("Error while retrieving {}/{} ({})".format(collection, item_id, r.content))
                return None
        except Exception as e:
            Process.LOGGER.error("Exception while retrieving {}/{}".format(collection, item_id))
            Process.LOGGER.exception(e)
            return None

    @staticmethod
    def get_item_from_airs(airs_endpoint: str, collection: str, item_id: str) -> Item:
        try:
            r = requests.get(url=os.path.join(airs_endpoint, "collections", collection, "items", item_id))
            if r.ok:
                return mapper.item_from_json(r.content)
            else:
                return None
        except Exception:
            return None

    @staticmethod
    def asset_in_airs(airs_endpoint: str, collection: str, item_id: str, asset_name: str) -> bool:
        try:
            r = requests.head(url=os.path.join(airs_endpoint, "collections", collection, "items", item_id, "assets", asset_name))
            if r.ok:
                return True
            else:
                return False
        except Exception:
            return False

    @staticmethod
    def get_user_email(authorization: str) -> tuple[str, str]:
        import jwt
        send_to: str = "anonymous"
        user_id: str = "anonymous"
        try:
            if authorization:
                token_content = jwt.decode(authorization.removeprefix("Bearer "), options={"verify_signature": False})  # NOSONAR
                if token_content.get("email"):
                    send_to = token_content.get("email")
                else:
                    Process.LOGGER.error("email not found in token {}".format(token_content))
                if token_content.get("sub"):
                    user_id = token_content.get("sub")
                else:
                    Process.LOGGER.error("subject not found in token {}".format(token_content))
            else:
                Process.LOGGER.error("no token in header")
        except Exception as e:
            Process.LOGGER.error("Can not open token from header")
            Process.LOGGER.exception(e)
        return (send_to, user_id)

    @staticmethod
    def dir2s3(directory: str, s3_dir: str, s3_conf: S3Configuration):
        s3_client = s3.get_client_from_configuration(s3_conf)

        upload_file_names = []
        for (source_dir, dirname, files) in os.walk(directory):
            for file in files:
                upload_file_names.append(os.path.join(source_dir, file)[len(directory):])

        for key in upload_file_names:
            local_path = os.path.join(directory, key.strip("/"))
            destpath = os.path.join(s3_dir, key.strip("/"))
            mime_type, __ = mimetypes.guess_type(local_path, strict=False)
            if mime_type:
                extra = {"ContentType": mime_type}
            else:
                extra = None
            Process.LOGGER.info("Copy {} ({}) to {}/{}".format(local_path, mime_type, s3_conf.bucket, destpath))
            with open(local_path, 'rb') as file:
                s3_client.upload_fileobj(file, s3_conf.bucket, destpath, ExtraArgs=extra)

    @staticmethod
    def upload_asset_if_managed(item: Item, asset: Asset, airs_endpoint):
        if asset.airs__managed is True:
            with AccessManager.stream(asset.href) as filedesc:
                file = {'file': (asset.name, filedesc, asset.type)}
                try:
                    r = requests.post(url=os.path.join(airs_endpoint, "collections", item.collection, "items", item.id, "assets", asset.name), files=file)
                    if r.ok:
                        Process.LOGGER.debug("asset uploaded successfully")
                    else:
                        msg = "Failed to upload asset: {} - {} on {}".format(r.status_code, r.content, airs_endpoint)
                        Process.LOGGER.error(msg)
                        raise RegisterException(msg)
                except requests.exceptions.ConnectionError:
                    msg = AIRS_CAN_NOT_BE_REACHED.format(airs_endpoint)
                    Process.LOGGER.error(msg)
                    raise ConnectionException(msg)
        else:
            Process.LOGGER.info("{} not managed".format(asset.name))

    @staticmethod
    def insert_or_update_item(item: Item, airs_endpoint) -> Item:
        item_already_exists = False
        try:
            r = requests.get(url=os.path.join(airs_endpoint, "collections", item.collection, "items", item.id), headers=JSON_HEADER)
            if r.ok:
                Process.LOGGER.debug("Item {}/{} already exists: triggers update".format(item.collection, item.id))
                item_already_exists = True
            else:
                Process.LOGGER.debug("Item {}/{} does not yes exist: triggers insert".format(item.collection, item.id))
        except requests.exceptions.ConnectionError:
            msg = "AIRS Service can not be reached ({})".format(airs_endpoint)
            Process.LOGGER.error(msg)
            raise ConnectionException(msg)
        try:
            if item_already_exists:
                Process.LOGGER.debug("update item {}/{} ...".format(item.collection, item.id))
                r = requests.put(url=os.path.join(airs_endpoint, "collections", item.collection, "items", item.id), data=mapper.to_json(item), headers=JSON_HEADER)
            else:
                Process.LOGGER.debug("Insert item {}/{} ...".format(item.collection, item.id))
                r = requests.post(url=os.path.join(airs_endpoint, "collections", item.collection, "items"), data=mapper.to_json(item), headers=JSON_HEADER)
            if r.ok:
                Process.LOGGER.debug("upsert done for item {}/{} ...".format(item.collection, item.id))
                return mapper.item_from_json(r.content)
            else:
                Process.LOGGER.error("Item has not been registered: {} - {}".format(r.status_code, r.content))
                Process.LOGGER.error(mapper.to_json(item))
                raise RegisterException("Item has not been registered: {} - {}".format(r.status_code, r.content))
        except requests.exceptions.ConnectionError:
            msg = AIRS_CAN_NOT_BE_REACHED.format(airs_endpoint)
            Process.LOGGER.error(msg)
            raise ConnectionException(msg)
