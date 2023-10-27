import datetime
import json
import uuid
from email.message import EmailMessage
from smtplib import SMTP

import elasticsearch
import requests

from airs.core.models import mapper
from airs.core.models.model import Item, Properties
from aproc.core.logger import Logger
from extensions.aproc.proc.download.drivers.exceptions import DriverException
from extensions.aproc.proc.download.settings import Configuration

LOGGER = Logger.logger


class Notifications:

    def init():
        LOGGER.info("SMTP configuration: {}".format(Configuration.settings.smtp.model_dump_json()))

    def report(item: Item, subject: str, msg: str, to: list[str], context: dict[str, str], outcome: str = None):
        if outcome:
            try:
                doc: Item = Item()
                doc.id = str(uuid.uuid4())
                doc.properties = Properties()
                doc.properties.__setattr__("user", context.get("arlas-user-email", "anonymous"))
                doc.properties.__setattr__("download_datetime", int(datetime.datetime.now().timestamp()))
                doc.properties.__setattr__("outcome", outcome)
                if item is not None:
                    doc.properties.__setattr__("id_from_source", item.id)
                    doc.centroid = item.centroid
                    doc.geometry = item.geometry
                    doc.collection = item.collection
                    doc.bbox = item.bbox
                    doc.catalog = item.catalog
                    doc.properties.constellation = item.properties.constellation
                    doc.properties.datetime = int(item.properties.datetime.timestamp())
                    doc.properties.data_type = item.properties.data_type
                    doc.properties.instrument = item.properties.instrument
                    doc.properties.item_format = item.properties.item_format
                    doc.properties.item_type = item.properties.item_type
                    doc.properties.main_asset_format = item.properties.main_asset_format
                    doc.properties.programme = item.properties.programme
                    doc.properties.observation_type = item.properties.observation_type
                    doc.properties.sensor = item.properties.sensor
                    doc.properties.sensor_type = item.properties.sensor_type
                else:
                    doc.collection = context.get("collection", None)
                    doc.properties.__setattr__("id_from_source", context.get("item_id", None))
                    doc.properties.__setattr__("reason", context.get("error", None))
                    doc.centroid = [0.0, 0.0]
                    doc.geometry = {"type": "Point", "coordinates": [0.0, 0.0]}

                if not Notifications.__getES().indices.exists(index=Configuration.settings.index_for_download.index_name):
                    LOGGER.info("Index {} does not exists. Attempt to create it with mapping from {} and {}".format(Configuration.settings.index_for_download.index_name, Configuration.settings.arlaseo_mapping_url, Configuration.settings.download_mapping_url))
                    mapping = Notifications.__fetch_mapping__(Configuration.settings.arlaseo_mapping_url)
                    mapping["properties"]["properties"]["properties"].update(Notifications.__fetch_mapping__(Configuration.settings.download_mapping_url)["properties"]["properties"]["properties"])
                    Notifications.__getES().indices.create(index=Configuration.settings.index_for_download.index_name, mappings=mapping)
                    LOGGER.info("Mapping {} updated.".format(Configuration.settings.index_for_download.index_name))
                else:
                    LOGGER.debug("Index {} found.".format(Configuration.settings.index_for_download.index_name))

                Notifications.__getES().index(
                    index=Configuration.settings.index_for_download.index_name,
                    document=mapper.to_airs_json(doc),
                    id=doc.id
                )
            except Exception as e:
                LOGGER.error("Can not report download in elasticsearch")
                LOGGER.error(e)
        if (not subject and not msg) or not to or to == "anonymous":
            return
        try:
            if context is not None:
                msg = msg.format(**context)
                subject = subject.format(**context)
            email = EmailMessage()
            email.set_content(msg)
            email['Subject'] = subject
            email['From'] = Configuration.settings.smtp.from_addr
            email['To'] = ",".join(to)
            client = SMTP(host=Configuration.settings.smtp.host,
                          port=Configuration.settings.smtp.port)
            client.login(user=Configuration.settings.smtp.login, password=Configuration.settings.smtp.password)
            client.sendmail(msg=email.as_string(), from_addr=Configuration.settings.smtp.from_addr, to_addrs=to)
            client.quit()
        except Exception as e:
            LOGGER.error("Error while sending email.")
            LOGGER.exception(e)

    def __fetch_mapping__(location: str):
        if (location.startswith("http")):
            r = requests.get(location, verify=False)
            if r.ok:
                return r.json()["mappings"]
            else:
                LOGGER.error("Can not fetch the mapping for creating the ARLAS index. Aborting ...")
                raise Exception("Can not fetch the mapping for creating the ARLAS index. Aborting ...")
        else:
            with open(location) as f:
                return json.load(f)["mappings"]

    def __getES() -> elasticsearch.Elasticsearch:
        if Configuration.settings.index_for_download.login:
            return elasticsearch.Elasticsearch(Configuration.settings.index_for_download.endpoint_url, basic_auth=(Configuration.settings.index_for_download.login, Configuration.settings.index_for_download.pwd), verify_certs=False)
        else:
            return elasticsearch.Elasticsearch(Configuration.settings.index_for_download.endpoint_url, verify_certs=False)
