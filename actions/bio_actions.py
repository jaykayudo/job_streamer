from actions.base import BaseAction
from client.base.interactor import BaseInteractor
from utils.types import MessageType
from services.database.bio import BioService
from utils.logging import logger
from tabulate import tabulate
from utils.types import MessageTitle
from storage.core.models import Bio
from typing import Any


class BioActions(BaseAction):
    def __init__(self, interactor: BaseInteractor):
        super().__init__(interactor)

        self.actions = {
            "create": self.create_bio,
            "delete": self.delete_bio,
            "list": self.list_bios,
            "get": self.get_bio,
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
        
        bios_dumped = [self._filter_out_projects_and_work_experiences(bio) for bio in bios]
        
        tabulated_data = tabulate(bios_dumped, headers="keys", tablefmt="grid")
        self.interactor.writer(
            MessageType.INFO,
            tabulated_data,
            title=MessageTitle.BIO_LIST,
            extra_context=bios_dumped,
        )
        
    def _filter_out_projects_and_work_experiences(self, bio: Bio) -> list[dict[str, Any]]:
        """
        Filter out the projects and work experiences of a bio.
        This is done to avoid the message being too large.
        """
        bio_dumped = bio.json_dump()
        bio_dumped.pop("projects")
        bio_dumped.pop("work_experiences")
        return bio_dumped
    
    def get_bio(self):
        """
        Get a bio.
        """
        self.interactor.writer(MessageType.INFO, "Getting a bio...")
        name = self.interactor.reader(prompt="Enter the name of the bio")
        try:
            bio = BioService.get_bio(name=name)
            json_dumped_projects = [project.json_dump() for project in bio.projects]
            tabulated_projects = tabulate(json_dumped_projects, headers="keys", tablefmt="grid")
            json_dumped_work_experiences = [work_experience.json_dump() for work_experience in bio.work_experiences]
            tabulated_work_experiences = tabulate(json_dumped_work_experiences, headers="keys", tablefmt="grid")
            full_message = f"""
            Name: {bio.name}
            Bio: {bio.bio}
            Projects:
            {tabulated_projects}
            Work Experiences:
            {tabulated_work_experiences}
            ================================================
            """
            self.interactor.writer(MessageType.INFO, full_message, title=MessageTitle.BIO_LIST, extra_context=bio.json_dump())
        except Exception as e:
            logger.error(f"Error getting bio: {e}")
            self.interactor.writer(MessageType.ERROR, f"Error getting bio: {e}")

    
