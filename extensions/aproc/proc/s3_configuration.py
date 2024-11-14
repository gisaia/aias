import enum
import logging
from typing import Annotated, Literal, Union
from urllib.parse import urlparse

from pydantic import BaseModel, Field, computed_field


class GoogleStorageConstants(str, enum.Enum):
    AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
    TOKEN_URI = "https://oauth2.googleapis.com/token"
    AUTH_PROVIDER_CERT_URL = "https://www.googleapis.com/oauth2/v1/certs"


class GoogleStorageApiKey(BaseModel):
    type: Literal["service_account"] = "service_account"
    project_id: str
    private_key_id: str
    private_key: str
    client_id: str | None = Field(None)
    auth_uri: Literal[GoogleStorageConstants.AUTH_URI] = GoogleStorageConstants.AUTH_URI.value
    token_uri: Literal[GoogleStorageConstants.TOKEN_URI] = GoogleStorageConstants.TOKEN_URI.value
    auth_provider_x509_cert_url: Literal[GoogleStorageConstants.AUTH_PROVIDER_CERT_URL] = GoogleStorageConstants.AUTH_PROVIDER_CERT_URL.value
    universe_domain: Literal["googleapis.com"] = "googleapis.com"

    @computed_field
    @property
    def client_x509_cert_url(self) -> str:
        return f"https://www.googleapis.com/robot/v1/metadata/x509/{self.project_id}%40appspot.gserviceaccount.com"

    @computed_field
    @property
    def client_email(self) -> str:
        return f"{self.project_id}@appspot.gserviceaccount.com"


class GoogleStorage(BaseModel):
    type: Literal["gs"] = "gs"
    bucket: str
    api_key: GoogleStorageApiKey


class HttpsStorage(BaseModel):
    type: Literal["https"] = "https"
    headers: dict[str, str]


class NoStorage(BaseModel):
    type: Literal[None] = None


Storage = Annotated[Union[GoogleStorage, HttpsStorage, NoStorage], Field(discriminator="type")]


class S3Configuration(BaseModel):
    input: Storage | None = Field(None)

    def get_storage_parameters(self, href: str, LOGGER: logging.Logger) -> dict:
        storage_type = urlparse(href).scheme

        if not storage_type or storage_type == "file" or storage_type == "http":
            return {}

        if storage_type == "https":
            if self.input.type != "https":
                LOGGER.warning("No headers is configured for HTTPS requests. Using no headers")
                return {}
            return {"headers": self.input.headers}

        if storage_type == "gs":
            from google.cloud.storage import Client
            from google.oauth2 import service_account

            if self.input.type != "gs":
                import google.auth.credentials

                LOGGER.warning("No api_key is configured for Google Storage, but requesting an item on Google Storage. Using anonymous credentials")
                credentials = google.auth.credentials.AnonymousCredentials()
            else:
                # TODO: check if bucket match ?
                api_key = self.input.api_key
                credentials = service_account.Credentials.from_service_account_info(api_key)

            client = Client("APROC", credentials=credentials)
            return {"client": client}

        raise NotImplementedError(f"Storage '{storage_type}' not compatible")
