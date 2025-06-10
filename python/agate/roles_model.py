from pydantic import BaseModel, Extra


class Role(BaseModel, extra=Extra.allow):
    description: str | list[str]
    permissions: list[str]


class Roles(BaseModel, extra=Extra.allow):
    technicalRoles: dict[str, Role]
