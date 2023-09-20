from fastapi import APIRouter, Request, status
from pydantic import BaseModel

from aproc.core.models.exception import RESTException
from aproc.core.models.ogc import (Conforms, ExceptionType, Execute,
                                   InlineOrRefData, LandingPage, Link,
                                   ProcessDescription, ProcessList,
                                   ProcessSummary, StatusInfo)
from aproc.core.processes.exception import ProcessException
from aproc.core.processes.process import Process
from aproc.core.processes.processes import Processes
from aproc.core.utils import execute2inputs
from common.exception import OGCException
from aproc.core.logger import CustomLogger as Logger

LOGGER = Logger.get_logger()

ROUTER = APIRouter()
ROOT_CONFORMANCE = "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf"


@ROUTER.get("/conformance",
            response_model=Conforms,
            response_model_exclude_none=True)
def get_conformance() -> Conforms:
    return Conforms(
        conformsTo=[
            f"{ROOT_CONFORMANCE}/core",
            f"{ROOT_CONFORMANCE}/ogc-process-description",
            f"{ROOT_CONFORMANCE}/job-list",
            f"{ROOT_CONFORMANCE}/json",
            f"{ROOT_CONFORMANCE}/oas30",
        ]
    )


@ROUTER.get("/jobs",
            response_model_exclude_none=True)
def get_jobs():
    raise OGCException(type=ExceptionType.NOT_IMPLEMENTED.value,
                       status=status.HTTP_501_NOT_IMPLEMENTED)


@ROUTER.get("/jobs/{jobId}",
            response_model_exclude_none=True,
            responses={
                status.HTTP_200_OK: {
                    "model": StatusInfo
                    },
                status.HTTP_422_UNPROCESSABLE_ENTITY: {
                    "model": RESTException
                }
            })
def get_job(jobId: str):
    raise OGCException(type=ExceptionType.NOT_IMPLEMENTED.value,
                       status=status.HTTP_501_NOT_IMPLEMENTED)


@ROUTER.delete("/jobs/{jobId}",
               response_model_exclude_none=True,
               responses={
                status.HTTP_200_OK: {
                    "model": StatusInfo
                    },
                status.HTTP_422_UNPROCESSABLE_ENTITY: {
                    "model": RESTException
                }
               })
def delete_job(jobId: str):
    raise OGCException(type=ExceptionType.NOT_IMPLEMENTED.value,
                       status=status.HTTP_501_NOT_IMPLEMENTED)


@ROUTER.get("/jobs/{jobId}/results",
            response_model_exclude_none=True,
            responses={
                status.HTTP_200_OK: {
                    "model": dict[str, InlineOrRefData]
                    },
                status.HTTP_422_UNPROCESSABLE_ENTITY: {
                    "model": RESTException
                }
            })
def get_job_result(jobId: str):
    raise OGCException(type=ExceptionType.NOT_IMPLEMENTED.value,
                       status=status.HTTP_501_NOT_IMPLEMENTED)


@ROUTER.get("/",
            response_model=LandingPage,
            response_model_exclude_none=True)
def get_landing_page(request: Request) -> LandingPage:
    server_root = str(request.base_url).rstrip("/")

    api_definition = Link(
        href=server_root + "/openapi.json",
        rel="service-desc",
        type="application/vnd.oai.openapi+json;version=3.0",
        title="OpenAPI service description",
    )
    conformance = Link(
        href=server_root + "/conformace",
        rel="http://www.opengis.net/def/rel/ogc/1.0/conformance",
        type="application/json",
        title="OGC API - Processes conformance classes " +
              "implemented by this server"
    )
    processes = Link(
        href=server_root + "/processes",
        rel="http://www.opengis.net/def/rel/ogc/1.0/processes",
        type="application/json",
        title="Metadata about the processes"
    )
    jobs = Link(
        href=server_root + "/jobs",
        rel="http://www.opengis.net/def/rel/ogc/1.0/job-list",
        title="The endpoint for job monitoring"
    )

    return LandingPage(
        title="Datacube Builder API",
        description="OGC processes complaint API",
        links=[
            api_definition, conformance, processes, jobs
        ]
    )


def __create_process_link(process: ProcessDescription, server_root_path: str) -> Link:
    return Link(
        href=f"{str(server_root_path).rstrip('/')}/processes/{process.id}",
        title=f"Link for the {process.description}")


@ROUTER.get("/processes",
            response_model=ProcessList,
            response_model_exclude_none=True)
def get_processes_list(request: Request) -> ProcessList:
    processes: list[ProcessSummary] = []
    links: list[Link] = []

    for process in Processes.processes:
        processes.append(process.getProcessSummary())
        links.append(__create_process_link(process.getProcessDescription(), request.base_url))

    return ProcessList(
        processes=processes,
        links=links
    )


def __get_process(process_id: str) -> Process:
    try:
        return Processes.get_process(process_id)
    except ProcessException:
        raise OGCException(type=ExceptionType.URI_NOT_FOUND.value,
                           status=status.HTTP_404_NOT_FOUND,
                           detail=f"'{process_id}' is not a valid id.")


@ROUTER.get("/processes/{process_id}",
            response_model=ProcessDescription,
            response_model_exclude_unset=True,
            responses={
                status.HTTP_200_OK: {
                    "model": ProcessDescription
                    },
                status.HTTP_404_NOT_FOUND: {
                    "model": RESTException
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY: {
                    "model": RESTException
                }
            })
def get_process_summary(process_id: str):
    return __get_process(process_id).getProcessSummary()


@ROUTER.post("/processes/{process_id}/execution",
             response_model_exclude_none=True,
             responses={
                status.HTTP_200_OK: {
                    "model": BaseModel
                    },
                status.HTTP_404_NOT_FOUND: {
                    "model": RESTException
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY: {
                    "model": RESTException
                }
             })
def post_process_execute(process_id: str, execute: Execute):
    process = __get_process(process_id)

    if hasattr(process, "input_model"):
        return process.execute(process.input_model(**execute2inputs(execute)))
    return process.execute()
