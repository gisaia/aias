from pydantic import BaseModel, Extra, Field
from envyaml import EnvYAML


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


class Settings(BaseModel, extra='allow'):
    drivers: list[Driver] = Field(title="Configuration of the drivers")
    outbox_directory: str = Field(title="Directory where the downloads will be placed")
    notification_admin_emails: str = Field(title="List of admin emails for receiving download notifications, comma seperated.")
    smtp: SMPTConfiguration = Field(title="Emails address of the system that sends the emails")
    email_content_user: str = Field(title="Content of the email to be sent to the user")
    email_content_error_download: str = Field(title="Content of the email to be sent to the user")
    email_content_admin: str = Field(title="Content of the email to be sent to the admin")
    email_subject_user: str = Field(title="Subject of the email to be sent to the user")
    email_subject_error_download: str = Field(title="Subject of the email to be sent to the user")
    email_subject_admin: str = Field(title="Subject of the email to be sent to the admin")

class Configuration:
    settings: Settings | None = Field(title="aproc Download service configuration")

    @staticmethod
    def init(configuration_file: str):
        envyaml = EnvYAML(configuration_file, strict=False)
        print(envyaml.export())
        Configuration.settings = Settings(**envyaml.export())