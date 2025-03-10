import os
import shutil
import uuid
from datetime import datetime

from celery import shared_task
from pydantic import BaseModel, Field

from airs.core.models.model import Item
from aproc.core.logger import Logger
from aproc.core.models.ogc import ProcessDescription, ProcessSummary
from aproc.core.models.ogc.enums import JobControlOptions, TransmissionMode
from aproc.core.processes.process import Process
from aproc.core.settings import Configuration as AprocConfiguration
from aproc.core.utils import base_model2description
from extensions.aproc.proc.access.manager import AccessManager
from extensions.aproc.proc.dc3build.drivers.dc3_driver import DC3Driver
from extensions.aproc.proc.dc3build.model.dc3build_input import \
    InputDC3BuildProcess
from extensions.aproc.proc.dc3build.settings import \
    Configuration as InputDC3BuildConfiguration
from extensions.aproc.proc.drivers.driver_manager import DriverManager
from extensions.aproc.proc.drivers.exceptions import (APROCException, DriverException,
                                                      RegisterException)
from extensions.aproc.proc.processes.arlas_services_helper import \
    ARLASServicesHelper
from extensions.aproc.proc.variables import (ARLAS_COLLECTION_KEY,
                                             ARLAS_ITEM_ID_KEY,
                                             CUBE_FAILED_MSG, EVENT_ACTION,
                                             EVENT_CATEGORY_KEY,
                                             EVENT_KIND_KEY, EVENT_MODULE_KEY,
                                             EVENT_OUTCOME_KEY, EVENT_REASON,
                                             EVENT_TYPE_KEY, USER_ACTION_KEY,
                                             USER_EMAIL_KEY, USER_ID_KEY)

AIAS_VERSION = os.getenv("AIAS_VERSION", "0.0")
DRIVERS_CONFIGURATION_FILE_PARAM_NAME = "drivers"
LOGGER = Logger.logger


class OutputDC3BuildProcess(BaseModel):
    item_location: str = Field(title="Item location", description="Location of the Item on the ARLAS Item Registration Service")
    id: str = Field(title="Identifier", description="Identifier of the cube item within the collection")
    collection: str = Field(title="Collection", description="Collection that contains the item")
    catalog: str = Field(title="Catalog", description="Catalog that contains the item")


summary: ProcessSummary = ProcessSummary(
    title="Build a cube based on catalog items, then register the result in ARLAS.",
    description="Build a data cube (time serie of observations) based on groups of items, each group representing a time slice. The result is registered in ARLAS",
    keywords=["cube", "build", "datacube", "dc3build"],
    id="dc3build",
    version=AIAS_VERSION,
    jobControlOptions=[JobControlOptions.async_execute],
    outputTransmission=[TransmissionMode.reference],
    # TODO: provide the links if any => link could be the execute endpoint  # NOSONAR
    links=[]
)

description: ProcessDescription = ProcessDescription(
    **summary.model_dump(exclude_none=True, exclude_unset=True),
    inputs=base_model2description(InputDC3BuildProcess),
    outputs=base_model2description(OutputDC3BuildProcess)
)


class AprocProcess(Process):

    @staticmethod
    def init(configuration: dict):
        if configuration.get(DRIVERS_CONFIGURATION_FILE_PARAM_NAME):
            InputDC3BuildConfiguration.init(configuration_file=configuration.get(DRIVERS_CONFIGURATION_FILE_PARAM_NAME))
            InputDC3BuildConfiguration.raise_if_not_valid()
            DriverManager.init(summary.id, InputDC3BuildConfiguration.settings.drivers)
        else:
            raise DriverException("Invalid configuration for dc3build drivers ({})".format(configuration))
        AprocProcess.input_model = InputDC3BuildProcess
        description.inputs.get("include_drivers").schema_.items.enum = DriverManager.driver_names(summary.id)
        description.inputs.get("exclude_drivers").schema_.items.enum = DriverManager.driver_names(summary.id)

        AccessManager.init()

    @staticmethod
    def get_process_description() -> ProcessDescription:
        return description

    @staticmethod
    def get_process_summary() -> ProcessSummary:
        return summary

    @staticmethod
    def __get_driver__(input: InputDC3BuildProcess) -> DC3Driver:
        driver: DC3Driver = None
        if input.composition and len(input.composition) > 0 and len(input.composition[0].dc3__references) and input.composition[0].dc3__references[0]:
            reference = input.composition[0].dc3__references[0]
            item: Item = ARLASServicesHelper.get_item_from_airs(airs_endpoint=AprocConfiguration.settings.airs_endpoint, collection=reference.dc3__collection, item_id=reference.dc3__id)
            driver = DriverManager.solve(summary.id, item, include_drivers=input.include_drivers, exclude_drivers=input.exclude_drivers)

        if driver is None:
            error_msg = "No driver found for {}/{}".format(reference.dc3__collection, reference.dc3__id)
            LOGGER.info(CUBE_FAILED_MSG, extra={EVENT_KIND_KEY: "event", EVENT_CATEGORY_KEY: "file", EVENT_TYPE_KEY: USER_ACTION_KEY, EVENT_ACTION: "dc3build", EVENT_OUTCOME_KEY: "failure", EVENT_REASON: error_msg, EVENT_MODULE_KEY: "aproc-dc3build", ARLAS_COLLECTION_KEY: reference.dc3__collection, ARLAS_ITEM_ID_KEY: reference.dc3__id})
            LOGGER.error(error_msg)
            raise DriverException(error_msg)
        else:
            return driver

    @staticmethod
    def before_execute(**kwargs) -> dict[str, str]:
        headers: dict[str, str] = kwargs.pop("headers")
        dc3build_input: InputDC3BuildProcess = InputDC3BuildProcess(**kwargs)
        AprocProcess.__get_driver__(input=dc3build_input)
        (send_to, user_id) = ARLASServicesHelper.get_user_email(headers.get("authorization"))
        for group in dc3build_input.composition:
            for reference in group.dc3__references:
                LOGGER.debug("checking for item access {}/{} for {}".format(reference.dc3__collection, reference.dc3__id, send_to))
                item: Item = ARLASServicesHelper.get_item_from_arlas(arlas_url_search=InputDC3BuildConfiguration.settings.arlas_url_search, collection=reference.dc3__collection, item_id=reference.dc3__id, headers=headers)
                if item is None:
                    error_msg = "{}/{} not found".format(reference.dc3__collection, reference.dc3__id)
                    LOGGER.error(error_msg)
                    LOGGER.info(CUBE_FAILED_MSG, extra={EVENT_KIND_KEY: "event", EVENT_CATEGORY_KEY: "file", EVENT_TYPE_KEY: USER_ACTION_KEY, EVENT_ACTION: "dc3build", EVENT_OUTCOME_KEY: "failure", EVENT_REASON: error_msg, USER_ID_KEY: user_id, USER_EMAIL_KEY: send_to, EVENT_MODULE_KEY: "aproc-dc3build", ARLAS_COLLECTION_KEY: reference.dc3__collection, ARLAS_ITEM_ID_KEY: reference.dc3__id})
                    raise RegisterException(error_msg)
                else:
                    LOGGER.debug("{} can access {}/{}".format(send_to, reference.dc3__collection, reference.dc3__id))
        return {}

    @shared_task(bind=True, track_started=True)
    def execute(self, **kwargs) -> dict:
        headers: dict[str, str] = kwargs.pop("headers")
        (send_to, user_id) = ARLASServicesHelper.get_user_email(headers.get("authorization"))
        dc3build_input: InputDC3BuildProcess = InputDC3BuildProcess(**kwargs)
        driver: DC3Driver = None
        items = {}
        for group in dc3build_input.composition:
            for reference in group.dc3__references:
                LOGGER.debug("checking for item access {}/{} for {}".format(reference.dc3__collection, reference.dc3__id, send_to))
                item = ARLASServicesHelper.get_item_from_arlas(arlas_url_search=InputDC3BuildConfiguration.settings.arlas_url_search, collection=reference.dc3__collection, item_id=reference.dc3__id, headers=headers)
                id_to_item = items.get(item.collection, {})
                id_to_item[item.id] = item
                items[item.collection] = id_to_item
        if dc3build_input.composition and len(dc3build_input.composition) > 0 and len(dc3build_input.composition[0].dc3__references):
            reference = dc3build_input.composition[0].dc3__references[0]
            item: Item = ARLASServicesHelper.get_item_from_airs(airs_endpoint=AprocConfiguration.settings.airs_endpoint, collection=reference.dc3__collection, item_id=reference.dc3__id)
            driver = DriverManager.solve(summary.id, item, include_drivers=dc3build_input.include_drivers, exclude_drivers=dc3build_input.exclude_drivers)
            if driver is None:
                error_msg = "No driver found for {}/{}".format(reference.dc3__collection, reference.dc3__id)
                LOGGER.info(CUBE_FAILED_MSG, extra={EVENT_KIND_KEY: "event", EVENT_CATEGORY_KEY: "file", EVENT_TYPE_KEY: USER_ACTION_KEY, EVENT_ACTION: "dc3build", EVENT_OUTCOME_KEY: "failure", EVENT_REASON: error_msg, EVENT_MODULE_KEY: "aproc-dc3build", ARLAS_COLLECTION_KEY: reference.dc3__collection, ARLAS_ITEM_ID_KEY: reference.dc3__id})
                LOGGER.error(error_msg)
                raise DriverException(error_msg)
        item_id = uuid.uuid4().hex
        working_dir = driver.get_working_dir(item_id)
        try:
            item = driver.create_cube(dc3_request=dc3build_input, items=items, target_directory=working_dir)
            item.collection = dc3build_input.target_collection
            item.catalog = dc3build_input.target_catalog
            item.properties.created = round(datetime.now().timestamp())
            item.properties.updated = round(datetime.now().timestamp())
            item.id = item_id
            i: int = 0
            errors = AprocProcess.check_item(item)
            if len(errors) > 0:
                error_msg = "Failed to register asset: invalid item:" + ",".join(errors)
                LOGGER.error(error_msg)
                raise RegisterException(error_msg)
            for asset_name, asset in item.assets.items():
                if asset.airs__managed:
                    if asset.href.startswith(working_dir):
                        # updload asset
                        AprocProcess.update_task_status(LOGGER, self, state='PROGRESS', meta={'step': 'upload_asset', 'current': i, 'asset': asset_name, 'total': len(item.assets), "ACTION": "INGEST", "TARGET": item.id})
                        ARLASServicesHelper.upload_asset_if_managed(item=item, asset=asset, airs_endpoint=AprocConfiguration.settings.airs_endpoint)
                        i += 1
                    else:
                        error_msg = "Failed to register asset: invalid asset location ({})".format(asset.href)
                        LOGGER.error(error_msg)
                        raise RegisterException(error_msg)
                else:
                    LOGGER.warning("Asset {} is not managed. Its content ({}) will not be copied and could be lost.".format(asset_name, asset.href))
            AprocProcess.update_task_status(LOGGER, self, state='PROGRESS', meta={'step': 'register_item', "ACTION": "INGEST", "TARGET": item.id})
            item: Item = ARLASServicesHelper.insert_or_update_item(item, AprocConfiguration.settings.airs_endpoint)
            return OutputDC3BuildProcess(collection=item.collection, catalog=item.catalog, id=item.id, item_location="/".join([AprocConfiguration.settings.airs_endpoint, "collections", item.collection, "items", item.id])).model_dump(exclude_none=True, exclude_unset=True)
        except Exception as e:
            error_msg = "Failed to build the cube. ({})".format(e.args)
            LOGGER.info(CUBE_FAILED_MSG, extra={EVENT_KIND_KEY: "event", EVENT_CATEGORY_KEY: "file", EVENT_TYPE_KEY: USER_ACTION_KEY, EVENT_ACTION: "enrich", EVENT_OUTCOME_KEY: "failure", EVENT_REASON: error_msg, EVENT_MODULE_KEY: "aproc-dc3build"})
            LOGGER.error(error_msg)
            LOGGER.exception(e)
            raise APROCException(error_msg)
        finally:
            if working_dir.startswith(DC3Driver.assets_dir):
                shutil.rmtree(working_dir)  # !DELETE!

    @staticmethod
    def check_item(item: Item, check_asset_exists: bool = True) -> list[str]:
        errors = []
        if item.id is None:
            errors.append("Item's id must be defined")
        if item.catalog is None:
            errors.append("Item's catalog must be defined")
        if item.collection is None:
            errors.append("Item's collection must be defined")
        if item.centroid is None:
            errors.append("Item's centroid must be defined")
        if item.geometry is None:
            errors.append("Item's geometry must be defined")
        if item.bbox is None:
            errors.append("Item's bbox must be defined")
        if item.assets is None:
            errors.append("Item's assets must be defined")
        if item.properties is None:
            errors.append("Item's properties must be defined")

        if item.properties:
            if item.properties.start_datetime is None:
                errors.append("Item's property start_datetime must be defined")
            if item.properties.end_datetime is None:
                errors.append("Item's property end_datetime must be defined")
            if item.properties.datetime is None:
                errors.append("Item's property datetime must be defined")
            if item.properties.keywords is None:
                errors.append("Item's property keywords must be defined")
            if item.properties.gsd is None:
                errors.append("Item's property gsd must be defined")
            if item.properties.item_format is None:
                errors.append("Item's property item_format must be defined")
            if item.properties.item_type is None:
                errors.append("Item's property item_type must be defined")
            if item.properties.main_asset_format is None:
                errors.append("Item's property main_asset_format must be defined")
            if item.properties.main_asset_name is None:
                errors.append("Item's property main_asset_name must be defined")
            if item.properties.eo__bands is None:
                errors.append("Item's property eo__bands must be defined")
            if item.properties.cube__variables is None:
                errors.append("Item's property cube__variables must be defined")
            if item.properties.proj__epsg is None:
                errors.append("Item's property proj__epsg must be defined")
            if item.properties.dc3__composition is None:
                errors.append("Item's property dc3__composition must be defined")
            if item.properties.cube__dimensions is None:
                errors.append("Item's property cube__dimensions must be defined")

        if item.assets:
            for asset_name, asset in item.assets.items():
                if asset_name != "airs_item":
                    if asset_name != asset.name:
                        errors.append("Item's asset key in assets must be the same as the asset.name property")
                    if asset.size is None:
                        errors.append("Item's asset {} property size must be defined".format(asset_name))
                    if asset.type is None:
                        errors.append("Item's asset {} property type must be defined".format(asset_name))
                    if asset.href is None:
                        errors.append("Item's asset {} property href must be defined".format(asset_name))
                    if asset.asset_format is None:
                        errors.append("Item's asset {} property asset_format must be defined".format(asset_name))
                    if asset.asset_type is None:
                        errors.append("Item's asset {} property asset_type must be defined".format(asset_name))
                    if asset.airs__managed is None:
                        errors.append("Item's asset {} property airs__managed must be defined".format(asset_name))
                    if asset.title is None:
                        errors.append("Item's asset {} property title must be defined".format(asset_name))
                    if asset.description is None:
                        errors.append("Item's asset {} property description must be defined".format(asset_name))
                    if asset.roles is None or len(asset.roles) == 0:
                        errors.append("Item's asset {} property roles must be defined and must contain at least one role".format(asset_name))
                    if asset.airs__managed:
                        if asset.href is None or (check_asset_exists and not os.path.exists(asset.href)):
                            errors.append("Item's asset {} href {} not found on file system".format(asset_name, asset.href))

        if item.properties.eo__bands:
            for band in item.properties.eo__bands:
                if band.name is None:
                    errors.append("Item's band property name must be defined")
                if band.asset is None:
                    errors.append("Item's band {} property asset must be defined".format(band.name))
                if band.index is None:
                    errors.append("Item's band {} property index must be defined".format(band.name))
        return errors
