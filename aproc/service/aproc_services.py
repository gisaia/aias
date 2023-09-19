from aproc.core.settings import Configuration
from aproc.core.processes.processes import Processes


class AprocServices:

    @staticmethod
    def init(configuration_file: str):
        Configuration.init(configuration_file=configuration_file)
        Processes.init()
