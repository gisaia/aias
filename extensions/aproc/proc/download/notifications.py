from smtplib import SMTP

from extensions.aproc.proc.download.settings import Configuration
from aproc.core.logger import Logger

LOGGER = Logger.logger


class Notifications:
    client: SMTP = None
    login = None
    password = None
    from_addr = None

    def init():
        Notifications.client = SMTP(host=Configuration.settings.sender.host, 
                                    port=Configuration.settings.sender.port)
        Notifications.login = Configuration.settings.sender.login
        Notifications.password = Configuration.settings.sender.password
        Notifications.from_addr = Configuration.settings.sender.from_addr

    def try_send_to(msg: str, to: str, context: dict[str, str]):
        try:
            for (variable, value) in context:
                msg = msg.replace("{"+variable+"}", value)
            Notifications.client.login(user=Notifications.login, password=Notifications.password)
            Notifications.client.send_message(msg, Notifications.from_addr, to_addrs=to)
            Notifications.client.quit()
        except Exception as e:
            LOGGER.error("Error wile sending email to {}".format(send_to))
            LOGGER.exception(e)
