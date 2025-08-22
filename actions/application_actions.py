from actions.base import BaseAction
from client.base.interactor import BaseInteractor
from utils.types import MessageType
from services.database.application import ApplicationService
from utils.logging import JobStreamerLogger
from tabulate import tabulate
from utils.types import MessageTitle
from storage.core.models import Application
from typing import Any, List
from utils.validation import is_valid_option_index_based
from services.database.bio import BioService


logger = JobStreamerLogger().get_logger()


class ApplicationActions(BaseAction):
    def __init__(self, interactor: BaseInteractor):
        super().__init__(interactor)

        self.actions = {
            "delete": self.delete_application,
            "list": self.list_applications,
            "get": self.get_application,
        }

    @classmethod
    def get_actions(cls) -> List[str]:
        """
        Get the actions of the action class.
        """
        return ["list", "get", "delete"]

    def handle_action_command(self, command: str):
        """
        Handle the action command.
        """
        if command.lower() in self.actions:
            self.actions[command.lower()]()
        else:
            logger.error(f"Invalid command: {command}")
            self.interactor.writer(MessageType.ERROR, "Invalid command")

    def list_applications(self):
        """
        List all applications.
        """
        self.interactor.writer(MessageType.INFO, "Listing all applications...")
        applications = ApplicationService.get_applications()
        applications_dumped = [application.json_dump() for application in applications]
        tabulated_data = tabulate(applications_dumped, headers="keys", tablefmt="grid")
        self.interactor.writer(
            MessageType.INFO,
            tabulated_data,
            title=MessageTitle.APPLICATION_LIST,
            extra_context=applications_dumped,
        )

    def get_application(self):
        """
        Get an application.
        """
        self.interactor.writer(MessageType.INFO, "Getting an application...")
        applications = ApplicationService.get_applications()
        applications_dumped = [application.json_dump() for application in applications]
        applications_string = "\n".join(
            [
                f"{idx + 1}. {application.job_title}"
                for idx, application in enumerate(applications)
            ]
        )
        self.interactor.writer(
            MessageType.INFO,
            f"Please select an application:\n{applications_string}",
            title=MessageTitle.APPLICATION_LIST,
            extra_context=applications_dumped,
        )
        application_index = self.interactor.reader(
            prompt="Enter the index of the application"
        )
        if not is_valid_option_index_based(application_index, applications):
            self.interactor.writer(MessageType.ERROR, "Invalid option")
            return
        application = applications[int(application_index) - 1]
        self.interactor.writer(
            MessageType.INFO, f"Application: {application.job_title}"
        )
        self.interactor.writer(MessageType.INFO, f"Platform: {application.platform}")
        self.interactor.writer(
            MessageType.INFO, f"Job Description: {application.job_description}"
        )
        self.interactor.writer(MessageType.INFO, f"Job URL: {application.job_url}")
        self.interactor.writer(
            MessageType.INFO, f"Job Location: {application.job_location}"
        )
        self.interactor.writer(
            MessageType.INFO, f"Job Salary: {application.job_salary}"
        )
        self.interactor.writer(
            MessageType.INFO, f"Job Company: {application.job_company}"
        )
        self.interactor.writer(
            MessageType.INFO, f"Job Company URL: {application.job_company_url}"
        )
        self.interactor.writer(
            MessageType.INFO,
            f"Application Detail File Path: {application.application_detail_file_path}",
        )

    def delete_application(self):
        """
        Delete an application.
        """
        self.interactor.writer(MessageType.INFO, "Deleting an application...")
        applications = ApplicationService.get_applications()
        applications_dumped = [application.json_dump() for application in applications]
        applications_string = "\n".join(
            [
                f"{idx + 1}. {application.job_title}"
                for idx, application in enumerate(applications)
            ]
        )
        self.interactor.writer(
            MessageType.INFO,
            f"Please select an application:\n{applications_string}",
            title=MessageTitle.APPLICATION_LIST,
            extra_context=applications_dumped,
        )
        application_index = self.interactor.reader(
            prompt="Enter the index of the application"
        )
        if not is_valid_option_index_based(application_index, applications):
            self.interactor.writer(MessageType.ERROR, "Invalid option")
            return
        application = applications[int(application_index) - 1]
        try:
            ApplicationService.delete_application(application.id)
            logger.info(f"Application deleted successfully: {application.job_title}")
            self.interactor.writer(
                MessageType.SUCCESS,
                f"Application deleted successfully: {application.job_title}",
            )
        except Exception as e:
            logger.error(f"Error deleting application: {e}")
            self.interactor.writer(
                MessageType.ERROR, f"Error deleting application: {e}"
            )
            return
