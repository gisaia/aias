from pydantic import BaseModel, Field


class StorageSettings(BaseModel, extra='allow'):
    type: str = Field(title='Type of storage used')


class AccessManagerSettings(BaseModel):
    storages: list[StorageSettings] = Field(title="List of configurations for the available storages")
    tmp_dir: str = Field(title="Temporary directory in which to write files that will be deleted")
