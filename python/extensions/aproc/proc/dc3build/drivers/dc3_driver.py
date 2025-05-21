import tempfile
from abc import abstractmethod

from aias_common.access.manager import AccessManager
from airs.core.models.model import Item
from extensions.aproc.proc.dc3build.model.dc3build_input import \
    InputDC3BuildProcess
from extensions.aproc.proc.drivers.abstract_driver import AbstractDriver


class DC3Driver(AbstractDriver):
    alternative_asset_href_field = None

    def __init__(self):
        super().__init__()

    def get_working_dir(self, key: str) -> str:
        """Provides the directory for storing the files

        Args:
            url (str): the original url

        Returns:
            str: the directory for storing the assets
        """
        AccessManager.makedir(self.assets_dir)
        return tempfile.mkdtemp(dir=self.assets_dir, prefix="{}_{}".format(self.name, key))

    @staticmethod
    def init(configuration: dict) -> None:
        if configuration:
            DC3Driver.alternative_asset_href_field = configuration.get("alternative_asset_href_field")

    @staticmethod
    def __flat_items__(items: dict[str, dict[str, Item]]) -> list[Item]:
        its = list(map(lambda v: list(v.values()), items.values()))
        return [x for xs in its for x in xs]

    @abstractmethod
    def create_cube(self, dc3_request: InputDC3BuildProcess, items: dict[str, dict[str, Item]], target_directory: str) -> Item:
        """Create a datacube based on item assembled in groups. Each group corresponds to a time slice. The generated cube (and metadata files) must be placed in target_directory.
        The generated files must be referenced in the assets. Thoses assets must be managed so that the files are uploaded. Use unmanaged assets to point at external resources.

        The returned item is added in ARLAS AIRS and assets are placed in the object store by the dc3build process.

        Args:
            dc3_request (InputDC3BuildProcess): The description of cube to build with the item references
            target_directory (str): where the cube should be placed
            items (dict[str, dict[str, Item]]): STAC AIRS Items as a dictionnary: the key contains the collection name, the value contains a dictionnary: this second dictionnary contains the item id as the key, the AIRS STAC Item as value.
        Returns:
            Item: the STAC AIRS Item.
        """
        ...
