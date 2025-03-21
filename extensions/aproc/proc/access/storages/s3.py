import os
from typing import Literal
from urllib.parse import urlparse, urlunparse

from pydantic import BaseModel, Field, computed_field

from extensions.aproc.proc.access.file import File
from extensions.aproc.proc.access.storages.abstract import AbstractStorage


class S3ApiKey(BaseModel):
    access_key: str
    secret_key: str


class S3Storage(AbstractStorage):
    type: Literal["s3"] = "s3"
    is_local: Literal[False] = False
    bucket: str
    endpoint: str
    api_key: S3ApiKey | None = Field(default=None)
    max_objects: int = Field(default=1000, description="Maximum number of objects to fetch when listing elements in a directory")

    @computed_field
    @property
    def is_anon_client(self) -> bool:
        return self.api_key is None

    def get_storage_parameters(self):
        import boto3

        if self.is_anon_client:
            from botocore import UNSIGNED
            from botocore.client import Config

            client = boto3.client(
                "s3",
                region_name="auto",
                endpoint_url=self.endpoint,
                config=Config(signature_version=UNSIGNED)
            )
        else:
            client = boto3.client(
                "s3",
                region_name="auto",
                endpoint_url=self.endpoint,
                aws_access_key_id=self.api_key.access_key,
                aws_secret_access_key=self.api_key.secret_key,
            )

        return {"client": client}

    def supports(self, href: str):
        scheme = urlparse(href).scheme
        netloc = urlparse(href).netloc

        if scheme == "s3":
            return netloc == self.bucket
        elif scheme == "http":
            return f"{scheme}://{netloc}" == self.endpoint
        return False

    def exists(self, href: str):
        import botocore.exceptions

        try:
            return self.__head_object(href)['ResponseMetadata']['HTTPStatusCode'] == 200
        except botocore.exceptions.ClientError:
            return self.is_dir(href)

    def get_rasterio_session(self):
        import rasterio.session

        params = {}

        if self.is_anon_client:
            params["session"] = rasterio.session.AWSSession(
                aws_unsigned=True,
                endpoint_url=self.endpoint
            )
        else:
            params["session"] = rasterio.session.AWSSession(
                aws_access_key_id=self.api_key.access_key,
                aws_secret_access_key=self.api_key.secret_key,
                endpoint_url=self.endpoint
            )

        return params

    def __get_href_key(self, href: str):
        return urlparse(href).path.removeprefix(f"/{self.bucket}/")

    def pull(self, href: str, dst: str):
        import botocore.client

        super().pull(href, dst)

        client: botocore.client.BaseClient = self.get_storage_parameters()["client"]

        obj = client.get_object(Bucket=self.bucket, Key=self.__get_href_key(href))
        with open(dst, "wb") as f:
            for chunk in obj['Body'].iter_chunks(50 * 1024):
                f.write(chunk)

    def __head_object(self, href: str):
        return self.get_storage_parameters()["client"].head_object(
                Bucket=self.bucket,
                Key=self.__get_href_key(href)
            )

    def is_file(self, href: str):
        import botocore.exceptions

        try:
            return self.__head_object(href)['ResponseMetadata']['HTTPStatusCode'] == 200
        except botocore.exceptions.ClientError:
            return False

    def __list_objects(self, href: str):
        return self.get_storage_parameters()["client"].list_objects_v2(
            Bucket=self.bucket,
            Prefix=self.__get_href_key(href).removesuffix("/") + "/",
            Delimiter="/",
            MaxKeys=self.max_objects
        )

    def is_dir(self, href: str):
        return self.__list_objects(href)['KeyCount'] > 0

    def get_file_size(self, href: str):
        return self.__head_object(href)['ContentLength']

    def __update_url__(self, source: str, path: str):
        url = urlparse(source)
        components = list(url[:])
        if len(components) == 5:
            components.append('')
        components[2] = os.path.join(self.bucket, path)
        return urlunparse(tuple(components))

    def listdir(self, source: str) -> list[File]:
        objects = self.__list_objects(source)

        files = list(map(lambda c: File(
            name=os.path.basename(c["Key"]),
            path=self.__update_url__(source, c["Key"]),
            is_dir=False,
            last_modification_date=c["LastModified"]), objects["Contents"]))

        dirs = []
        if objects.get("CommonPrefixes"):
            dirs = list(map(lambda d: File(
                name=os.path.basename(d["Prefix"].removesuffix("/")),
                path=self.__update_url__(source, d["Prefix"]),
                is_dir=True), objects["CommonPrefixes"]))

        return files + dirs

    def get_last_modification_time(self, href: str):
        return self.__head_object(href)['LastModified'].timestamp()

    def get_creation_time(self, href: str):
        # There is no difference in s3 between last update and creation date
        return self.get_last_modification_time(href)

    def makedir(self, href: str, strict=False):
        if strict:
            raise PermissionError("Creating a folder on a remote storage is not permitted")

    def clean(self, href: str):
        raise PermissionError("Deleting files on a remote storage is not permitted")
