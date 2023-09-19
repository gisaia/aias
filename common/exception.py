import attrs


# Can't use BaseModel due to conflicting inheritances
@attrs.define
class OGCException(Exception):
    type: str
    title: str | None = None
    status: int | None = None
    detail: str | None = None
    instance: str | None = None


@attrs.define
class BadRequest(OGCException):
    type: str = "bad request"
    status: int = 400
