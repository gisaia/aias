from pydantic import BaseModel, Extra, Field
from envyaml import EnvYAML
import json

from airs.core.settings import S3


class Driver(BaseModel, extra=Extra.allow):
    name: str | None = Field(title="Name of the driver")
    class_name: str | None = Field(title="Name of the driver class")
    configuration: dict | None = Field(title="Driver configuration")
    priority: int | None = Field(title="Driver priority. If two drivers are eligible then driver with highest priority will be selected over driver with lower priority.)")


class SMPTConfiguration(BaseModel, extra='allow'):
    host: str = Field(title="smtp host")
    port: int = Field(title="smtp port")
    login: str = Field(title="smtp user login")
    password: str = Field(title="smtp user password")
    from_addr: str = Field(title="Emails address of the system that sends the emails")


class Index(BaseModel, extra=Extra.allow):
    index_name: str
    endpoint_url: str
    login: str = Field(None)
    pwd: str = Field(None)


class Settings(BaseModel, extra='allow'):
    arlas_url_search: str = Field(title="ARLAS URL Search (ex http://arlas-server:9999/arlas/explore/{collection}/_search?f=id:eq:{item})")
    drivers: list[Driver] = Field(title="Configuration of the drivers")
    outbox_directory: str = Field(title="Directory where the downloads will be placed. Must be configured, even so you enabled outbox_s3")
    outbox_s3: S3 | None = Field(title="S3 bucket where the downloads will be placed. If configured, outbox_directory will be cleaned")
    clean_outbox_directory: bool = Field(True, title="Clean outbox directory once files copied on S3")
    notification_admin_emails: str = Field(title="List of admin emails for receiving download notifications, comma seperated.")
    smtp: SMPTConfiguration = Field(title="Emails address of the system that sends the emails")
    email_content_user: str = Field(title="Content of the email to be sent to the user")
    email_content_error_download: str = Field(title="Content of the email to be sent to the user")
    email_content_admin: str = Field(title="Content of the email to be sent to the admin")
    email_subject_user: str = Field(title="Subject of the email to be sent to the user")
    email_subject_error_download: str = Field(title="Subject of the email to be sent to the user")
    email_subject_admin: str = Field(title="Subject of the email to be sent to the admin")
    email_path_prefix_add: str = Field(title="Prefix to add to the download paths presented to the users/admin")
    email_path_to_windows: bool = Field(False, title="Whether to change or not the path seperators for windows")
    email_request_subject_user: str = Field(title="Content of the subject to be sent to the user when download request submitted")
    email_request_content_user: str = Field(title="Content of the email to be sent to the user when download request submitted")
    email_request_subject_admin: str = Field(title="Content of the subject to be sent to the admins when download request submitted")
    email_request_content_admin: str = Field(title="Content of the email to be sent to the admins when download request submitted")
    index_for_download: Index = Field(title="Configuration of the elasticsearch index for reporting downloads")
    arlaseo_mapping_url: str = Field(title="Location of the arlas eo mapping")
    download_mapping_url: str = Field(title="Location of the download requests mapping")


class Configuration:
    settings: Settings | None = Field(title="aproc Download service configuration")

    @staticmethod
    def init(configuration_file: str):
        envyaml = EnvYAML(configuration_file, strict=False)
        Configuration.settings = Settings(**envyaml.export())
        return Configuration.settings
