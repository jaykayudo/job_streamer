from actions.base import BaseAction
from client.base.interactor import BaseInteractor
from utils.types import MessageType
from services.database.bio import BioService
from utils.logging import logger
from tabulate import tabulate
from utils.types import MessageTitle


class BioActions(BaseAction):
    def __init__(self, interactor: BaseInteractor):
        super().__init__(interactor)

        self.actions = {
            "create": self.create_bio,
            "delete": self.delete_bio,
            "list": self.list_bios,
        }

    def handle_action_command(self, command: str):
        """
        Handle the action command.
        """
        if command in self.actions:
            self.actions[command]()
        else:
            self.interactor.writer(MessageType.ERROR, "Invalid command")

    def create_bio(self):
        """
        Create a new bio.
        """
        self.interactor.writer(MessageType.INFO, "Creating a new bio...")
        self.interactor.writer(MessageType.INFO, "Please provide the name of the bio")
        name = self.interactor.reader(prompt="Enter the name of the bio")
        self.interactor.writer(MessageType.INFO, "Please provide the bio")
        bio = self.interactor.reader(prompt="Enter the bio")
        try:
            BioService.create_bio(name=name, bio=bio)
            self.interactor.writer(
                MessageType.SUCCESS, f"Bio created successfully: {name}"
            )
        except Exception as e:
            logger.error(f"Error creating bio: {e}")
            self.interactor.writer(MessageType.ERROR, f"Error creating bio: {e}")

    def delete_bio(self):
        """
        Delete a bio.
        """
        self.interactor.writer(MessageType.INFO, "Deleting a bio...")
        self.interactor.writer(MessageType.INFO, "Please provide the name of the bio")
        name = self.interactor.reader(prompt="Enter the name of the bio")
        try:
            BioService.delete_bio(name=name)
            self.interactor.writer(
                MessageType.SUCCESS, f"Bio deleted successfully: {name}"
            )
        except Exception as e:
            logger.error(f"Error deleting bio: {e}")
            self.interactor.writer(MessageType.ERROR, f"Error deleting bio: {e}")

    def list_bios(self):
        """
        List all the bios.
        """
        self.interactor.writer(MessageType.INFO, "Listing all the bios...")
        bios = BioService.get_bios()
        bios_dumped = [bio.json_dump() for bio in bios]
        tabulated_data = tabulate(bios_dumped, headers="keys", tablefmt="grid")
        self.interactor.writer(
            MessageType.INFO,
            tabulated_data,
            title=MessageTitle.BIO_LIST,
            extra_context=bios_dumped,
        )
