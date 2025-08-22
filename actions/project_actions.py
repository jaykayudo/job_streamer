from actions.base import BaseAction
from client.base.interactor import BaseInteractor
from utils.types import MessageType
from services.database.project import ProjectService
from utils.logging import JobStreamerLogger
from tabulate import tabulate
from utils.types import MessageTitle
from storage.core.models import Project
from typing import Any, List
from utils.validation import is_valid_option_index_based
from services.database.bio import BioService


logger = JobStreamerLogger().get_logger()


class ProjectActions(BaseAction):
    def __init__(self, interactor: BaseInteractor):
        super().__init__(interactor)

        self.actions = {
            "create": self.create_project,
            "delete": self.delete_project,
            "list": self.list_projects,
            "get": self.get_project,
        }

    @classmethod
    def get_actions(cls) -> List[str]:
        """
        Get the actions of the project action class.
        """
        return ["create", "list", "get", "delete"]

    def handle_action_command(self, command: str):
        """
        Handle the action command.
        """
        if command.lower() in self.actions:
            self.actions[command.lower()]()
        else:
            logger.error(f"Invalid command: {command}")
            self.interactor.writer(MessageType.ERROR, "Invalid command")

    def create_project(self):
        """
        Create a new project.
        """
        self.interactor.writer(MessageType.INFO, "Creating a new project...")
        bios = BioService.get_bios()
        bios_dumped = [bio.json_dump() for bio in bios]
        bios_string = "\n".join(
            [f"{idx + 1}. {bio.name}" for idx, bio in enumerate(bios)]
        )
        self.interactor.writer(
            MessageType.INFO,
            f"Please select a bio:\n{bios_string}",
            title=MessageTitle.BIO_LIST,
            extra_context=bios_dumped,
        )
        bio_index = self.interactor.reader(prompt="Enter the number of the bio")
        if not is_valid_option_index_based(bio_index, bios):
            self.interactor.writer(MessageType.ERROR, "Invalid option")
            return
        bio = bios[int(bio_index) - 1]
        self.interactor.writer(
            MessageType.INFO, "Please provide the name of the project"
        )
        name = self.interactor.reader(prompt="Enter the name of the project")
        self.interactor.writer(
            MessageType.INFO, "Please provide the description of the project"
        )
        description = self.interactor.reader(
            prompt="Enter the description of the project", multiline=True
        )
        self.interactor.writer(
            MessageType.INFO, "Please provide the tools used in the project"
        )
        tools = self.interactor.reader(
            prompt="Enter the tools used in the project. (comma separated)"
        )
        self.interactor.writer(
            MessageType.INFO,
            "Please provide the impact of the project (leave blank if not applicable)",
        )
        impact = self.interactor.reader(
            prompt="Enter the impact of the project", multiline=True
        )
        try:
            ProjectService.create_project(
                bio_id=bio.id,
                name=name,
                description=description,
                tools=tools,
                impact=impact,
            )
            self.interactor.writer(
                MessageType.SUCCESS, f"Project created successfully: {name}"
            )
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            self.interactor.writer(MessageType.ERROR, f"Error creating project: {e}")
            return

    def delete_project(self):
        """
        Delete a project.
        """
        self.interactor.writer(MessageType.INFO, "Deleting a project...")
        projects = ProjectService.get_all_projects()
        projects_string = "\n".join(
            [f"{idx + 1}. {project.name}" for idx, project in enumerate(projects)]
        )
        self.interactor.writer(
            MessageType.INFO, f"Please select a project:\n{projects_string}"
        )
        project_index = self.interactor.reader(prompt="Enter the index of the project")
        if not is_valid_option_index_based(project_index, projects):
            self.interactor.writer(MessageType.ERROR, "Invalid option")
            return
        project = projects[int(project_index) - 1]
        try:
            ProjectService.delete_project(project.id)
            self.interactor.writer(
                MessageType.SUCCESS, f"Project deleted successfully: {project.name}"
            )
        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            self.interactor.writer(MessageType.ERROR, f"Error deleting project: {e}")
            return

    def list_projects(self):
        """
        List all projects.
        """
        self.interactor.writer(MessageType.INFO, "Listing all projects...")
        projects = ProjectService.get_all_projects()
        projects_dumped = [project.json_dump() for project in projects]
        tabulated_data = tabulate(projects_dumped, headers="keys", tablefmt="grid")
        self.interactor.writer(
            MessageType.INFO,
            tabulated_data,
            title=MessageTitle.PROJECT_LIST,
            extra_context=projects_dumped,
        )

    def get_project(self):
        """
        Get a project.
        """
        self.interactor.writer(MessageType.INFO, "Getting a project...")
        projects = ProjectService.get_all_projects()
        projects_string = "\n".join(
            [f"{idx + 1}. {project.name}" for idx, project in enumerate(projects)]
        )
        self.interactor.writer(
            MessageType.INFO, f"Please select a project:\n{projects_string}"
        )
        project_index = self.interactor.reader(prompt="Enter the index of the project")
        if not is_valid_option_index_based(project_index, projects):
            logger.error(f"Invalid option: {project_index}")
            self.interactor.writer(MessageType.ERROR, "Invalid option")
            return
        project = projects[int(project_index) - 1]
        self.interactor.writer(MessageType.INFO, f"Project: {project.name}")
        self.interactor.writer(MessageType.INFO, f"Description: {project.description}")
        self.interactor.writer(MessageType.INFO, f"Tools: {project.tools}")
        self.interactor.writer(MessageType.INFO, f"Impact: {project.impact}")
