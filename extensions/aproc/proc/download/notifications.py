from email.message import EmailMessage
from smtplib import SMTP

from extensions.aproc.proc.download.settings import Configuration
from aproc.core.logger import Logger

LOGGER = Logger.logger


class Notifications:

    def init():
        LOGGER.info("SMTP configuration: {}".format(Configuration.settings.smtp.model_dump_json()))

    def try_send_to(subject: str, msg: str, to: list[str], context: dict[str, str]):
        if (not subject and not msg) or not to or to == "anonymous":
            return
        try:
            if context is not None:
                context["arlas-user-email"] = to
                msg = msg.format(**context)
                subject = subject.format(**context)
            email = EmailMessage()
            email.set_content(msg)
            email['Subject'] = subject
            email['From'] = Configuration.settings.smtp.from_addr
            email['To'] = ",".join(to)
            client = SMTP(host=Configuration.settings.smtp.host, 
                          port=Configuration.settings.smtp.port)
            client.login(user=Configuration.settings.smtp.login, password=Configuration.settings.smtp.password)
            client.sendmail(msg=email.as_string(), from_addr=Configuration.settings.smtp.from_addr, to_addrs=to)
            client.quit()
        except Exception as e:
            LOGGER.error("Error while sending email.")
            LOGGER.exception(e)
