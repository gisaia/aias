import json
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from aproc.core.logger import CustomLogger as Logger
from aproc.core.models.ogc import (Conforms, ExceptionType, Execute,
                                   InlineOrRefData, LandingPage, Link,
                                   ProcessDescription, ProcessList,
                                   ProcessSummary, StatusInfo)
from aproc.core.models.ogc.job import StatusInfoList
from aproc.core.processes.exception import ProcessException
from aproc.core.processes.process import Process
from aproc.core.processes.processes import Processes
from common.exception import OGCException, RESTException

LOGGER = Logger.logger

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
            response_model_exclude_none=True,
            response_model=StatusInfoList)
def get_jobs(offset: int = 0, limit: int = 10, process_id: str = None, status: str = None):
    return Processes.list_jobs(offset=offset, limit=limit, process_id=process_id, status=status)

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
    return Processes.status(jobId)


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
    results = Processes.result(task_id=jobId)
    if results is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return JSONResponse(results)


@ROUTER.get("/jobs/resources/{resourceId}",
            response_model_exclude_none=True,
            responses={
                status.HTTP_200_OK: {
                    "model": dict[str, InlineOrRefData]
                    },
                status.HTTP_422_UNPROCESSABLE_ENTITY: {
                    "model": RESTException
                }
            })
def get_jobs_by_resource_id(resourceId: str):
    results = Processes.status_by_resource_id(resource_id=resourceId)
    if results is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return JSONResponse(list(map(lambda s: s.model_dump(), results)))


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
        title="ARLAS Processing API",
        description="ARLAS Processing API (OGC processes API)",
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
        processes.append(process.get_process_summary())
        links.append(__create_process_link(process.get_process_description(), request.base_url))

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
def get_process_description(process_id: str):
    return __get_process(process_id).get_process_description()


@ROUTER.post("/processes/{process_id}/execution",
             response_model_exclude_none=True,
             responses={
                status.HTTP_200_OK: {
                    "model": BaseModel
                    },
                status.HTTP_201_CREATED: {
                    "model": StatusInfo
                },
                status.HTTP_404_NOT_FOUND: {
                    "model": RESTException
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY: {
                    "model": RESTException
                }
             })
def post_process_execute(process_id: str, execute: Execute, request: Request):
    process = __get_process(process_id)
    try:
        if hasattr(process, "input_model"):
            inputs = execute.model_dump().get("inputs")
            context = dict(map(lambda v: v, request.headers.items()))
            job: StatusInfo = Processes.execute(process_name=process_id, headers=context, input=process.input_model(**inputs))
            job.processID = process_id
            return JSONResponse(content=job.model_dump(), status_code=status.HTTP_201_CREATED)
        return JSONResponse(content=process.execute().model_dump(), status_code=status.HTTP_200_OK)
    except Exception as e:
        LOGGER.exception(e)
        error = RESTException(type="Exception", status=500, title="Can not execute {} with inputs {}".format(process_id, execute), detail=str(e), )
        return JSONResponse(content=error.model_dump(), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
