from aproc.core.settings import Configuration
from aproc.core.processes.processes import Processes


class AprocServices:

    @staticmethod
    def init():
        Processes.init()
