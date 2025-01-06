from pydantic import BaseModel, Field

from extensions.aproc.proc.drivers.exceptions import DriverException


class DriverConfiguration(BaseModel, extra='allow'):
    name: str | None = Field(title="Name of the driver")
    class_name: str | None = Field(title="Name of the driver class")
    configuration: dict | None = Field(title="Driver configuration")
    priority: int | None = Field(title="Driver priority. If two drivers are eligible then driver with highest priority will be selected over driver with lower priority.)")
    assets_dir: str | None = Field(None, title="Location for storing temporary asset files")

    def raise_if_not_valid(self):
        MSG = "Ingest driver configuration exception: invalid configuration for driver {}: {}"
        if self.assets_dir is None:
            raise DriverException(MSG.format(self.name, "assets_dir not configured"))
        if self.class_name is None:
            raise DriverException(MSG.format(self.name, "class_name not configured"))
        if self.name is None:
            raise DriverException(MSG.format(self.name, "name not configured"))
        if self.priority is None:
            raise DriverException(MSG.format(self.name, "priority not configured"))
