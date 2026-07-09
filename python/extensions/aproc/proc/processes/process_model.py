from pydantic import Field
from aproc.core.models.ogc.execute import Subscriber
from aproc.core.processes.process import InputProcess as _InputProcess


class InputProcess(_InputProcess):
    include_drivers: list[str] = Field(default=[], title="List of drivers to include. If none, all are included")
    exclude_drivers: list[str] = Field(default=[], title="List of drivers to exclude. If none, none are excluded")
    cascade_subscriber: bool = Field(default=False, title="Whether the subscriber should be cascaded to the sub jobs or not")


class OutputProcess(_InputProcess):
    sub_jobs: list[str] = Field(default=[], title="Sub jobs", description="List of sub jobs that have been created for the process", minOccurs=0, maxOccurs=-1)
    message: str = Field(default="", title="Message", description="Message that can be returned by the process", minOccurs=0, maxOccurs=1)
    error: str = Field(default="", title="Error", description="Error that can be returned by the process", minOccurs=0, maxOccurs=1)
    process: str = Field(title="Process", description="Name of the process that has been executed", minOccurs=0, maxOccurs=1)
