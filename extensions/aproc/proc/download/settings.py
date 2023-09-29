from pydantic import BaseModel, Extra, Field
from envyaml import EnvYAML


class Driver(BaseModel, extra=Extra.allow):
    name: str | None = Field(title="Name of the driver")
    class_name: str | None = Field(title="Name of the driver class")
    configuration: dict | None = Field(title="Driver configuration")
    priority: int | None = Field(title="Driver priority. If two drivers are eligible then driver with highest priority will be selected over driver with lower priority.)")


class SMPTConfiguration(BaseModel, extra='allow'):
    host: str
    port: int
    login: str
    password: str
    from_addr: str


class Settings(BaseModel, extra='allow'):
    drivers: list[Driver] = Field(title="Configuration of the drivers")
    outbox_directory: str = Field(title="Directory where the downloads will be placed")
    notification_admin_emails: list[str] = Field(title="List of admin emails for receiving download notifications")
    sender: SMPTConfiguration = Field(title="Emails address of the system that sends the emails")
    email_content_user: str = Field(title="Content of the email to be sent to the user")
    email_content_error_download: str = Field(title="Content of the email to be sent to the user")
    email_conent_admin: str = Field(title="Content of the email to be sent to the admin")
    email_conent_download_launched_admin: str = Field(title="Content of the email to be sent to the admin when a download request has been launched")


class Configuration:
    settings: Settings | None = Field(title="aproc Service configuration")

    @staticmethod
    def init(configuration_file: str):
        envyaml = EnvYAML(configuration_file, strict=False)
        Configuration.settings = Settings(drivers=envyaml.get("drivers"))
