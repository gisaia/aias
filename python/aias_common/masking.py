import re
from collections.abc import Mapping

from pydantic import BaseModel

_SENSITIVE_HEADERS = frozenset({
    "authorization",
    "proxy-authorization",
    "cookie",
    "set-cookie",
    "x-api-key",
    "x-auth-token",
})

_DEFAULT_TOKEN_PARAMS = ("access_token", "id_token", "token", "jwt")

_BEARER = re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]{20,}")
_JWT = re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]*")
_URL_CREDS = re.compile(r"(?i)(\b[a-z][a-z0-9+.-]*://[^:/\s@]*:)[^@\s/]+(@)")

_SENSITIVE_KEY = re.compile(
    r"(?i)(pass(word|wd)?|pwd|secret|token|api[_-]?key|credential|"
    r"private[_-]?key|authorization|cookie)"
)


def mask(
        obj,
        *extra_names: str,
):
    """Recursively mask sensitive keys and credentials embedded in strings.

    This is the single entry point for headers, mappings, Pydantic models,
    sequences and plain strings.
    """
    if isinstance(obj, BaseModel):
        return mask(obj.model_dump(mode="python"), *extra_names)

    if isinstance(obj, Mapping):
        sensitive_headers = _SENSITIVE_HEADERS | {
            name.lower()
            for name in extra_names
            if name
        }

        return {
            key: "***"
            if isinstance(key, str)
               and (
                       key.lower() in sensitive_headers
                       or _SENSITIVE_KEY.search(key)
               )
            else mask(value, *extra_names)
            for key, value in obj.items()
        }

    if isinstance(obj, (list, tuple, set)):
        return [mask(item, *extra_names) for item in obj]

    if isinstance(obj, str):
        return mask_secrets_in_text(obj, *extra_names)

    return obj


def mask_secrets_in_text(
        text: str,
        *extra_param_names: str,
) -> str:
    """Mask token query parameters, Bearer values, JWTs and URL credentials."""
    names = "|".join(
        re.escape(name)
        for name in (*_DEFAULT_TOKEN_PARAMS, *extra_param_names)
        if name
    )

    text = re.sub(rf"(?i)((?:^|[?&])(?:{names})=)[^\s]+", r"\1***", text)
    text = _URL_CREDS.sub(r"\1***\2", text)
    text = _BEARER.sub(r"\1***", text)
    return _JWT.sub("***", text)