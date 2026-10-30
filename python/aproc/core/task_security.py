import json
import os

from celery import Task
from cryptography.fernet import Fernet, MultiFernet

FORWARDED_HEADERS = frozenset({"authorization","arlas-org-filter","x-request-id"})
ENCRYPT_KEY = "_encrypt"
MAX_AGE_SECONDS = 3600

_keys = [k.strip() for k in os.environ.get("APROC_TASK_ENCRYPTION_KEYS", "").split(",") if k.strip()]
_FERNET = MultiFernet([Fernet(k) for k in _keys]) if _keys else None


def forwardable(headers: dict[str, str] | None) -> dict[str, str]:
    return {k: v for k, v in (headers or {}).items() if k.lower() in FORWARDED_HEADERS}


def encrypt_headers(headers: dict[str, str]) -> dict[str, str]:
    if _FERNET is None:
        raise RuntimeError("APROC_TASK_ENCRYPTION_KEYS is not set: unable to encrypt forwarded headersr")
    return {ENCRYPT_KEY: _FERNET.encrypt(json.dumps(headers).encode()).decode()}


def decrypt_headers(value):
    if isinstance(value, dict) and ENCRYPT_KEY in value:
        if _FERNET is None:
            raise RuntimeError("APROC_TASK_ENCRYPTION_KEYS is not set: cannot decrypt headers")
        return json.loads(_FERNET.decrypt(value[ENCRYPT_KEY].encode(), ttl=MAX_AGE_SECONDS))
    return value or {}


class EncryptHeadersTask(Task):
    def __call__(self, *args, **kwargs):
        if "headers" in kwargs:
            kwargs["headers"] = decrypt_headers(kwargs["headers"])
        return super().__call__(*args, **kwargs)