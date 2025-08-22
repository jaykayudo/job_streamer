from actions.base import BaseAction
from client.base.interactor import BaseInteractor
from utils.types import MessageType
from services.database.work_experience import WorkExperienceService
from utils.logging import JobStreamerLogger
from tabulate import tabulate
from utils.types import MessageTitle
from storage.core.models import WorkExperience
from typing import Any, List
from services.database.bio import BioService
from utils.validation import is_valid_option_index_based

logger = JobStreamerLogger().get_logger()


class WorkExperienceActions(BaseAction):
    def __init__(self, interactor: BaseInteractor):
        super().__init__(interactor)

        self.actions = {
            "create": self.create_work_experience,
            "get": self.get_work_experience,
            "delete": self.delete_work_experience,
            "list": self.list_work_experiences,
        }

    @classmethod
    def get_actions(cls) -> List[str]:
        """
        Get the actions of the work experience action class.
        """
        return ["create", "get", "delete", "list"]

    def handle_action_command(self, command: str):
        """
        Handle the action command.
        """
        if command.lower() in self.actions:
            self.actions[command.lower()]()
        else:
            logger.error(f"Invalid command: {command}")
            self.interactor.writer(MessageType.ERROR, "Invalid command")

    def create_work_experience(self):
        """
        Create a work experience.
        """
        self.interactor.writer(MessageType.INFO, "Creating a work experience...")
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
        self.interactor.writer(MessageType.INFO, "Please provide the company name")
        company_name = self.interactor.reader(prompt="Enter the company name")
        self.interactor.writer(MessageType.INFO, "Please provide the role")
        role = self.interactor.reader(prompt="Enter the role")
        self.interactor.writer(MessageType.INFO, "Please provide the start date")
        start_date = self.interactor.reader(prompt="Enter the start date")
        self.interactor.writer(
            MessageType.INFO,
            "Please provide the end date (leave blank if not applicable)",
        )
        end_date = self.interactor.reader(prompt="Enter the end date")
        self.interactor.writer(MessageType.INFO, "Please provide the description")
        description = self.interactor.reader(
            prompt="Enter the description", multiline=True
        )
        try:
            WorkExperienceService.create_work_experience(
                bio_id=bio.id,
                company_name=company_name,
                role=role,
                start_date=start_date,
                end_date=end_date,
                description=description,
            )
            logger.info(f"Work experience created successfully: {company_name}")
            self.interactor.writer(
                MessageType.SUCCESS,
                f"Work experience created successfully: {company_name}",
            )
        except Exception as e:
            logger.error(f"Error creating work experience: {e}")
            self.interactor.writer(
                MessageType.ERROR, f"Error creating work experience: {e}"
            )
            return

    def get_work_experience(self):
        """
        Get a work experience.
        """
        self.interactor.writer(MessageType.INFO, "Getting a work experience...")
        work_experiences = WorkExperienceService.get_all_work_experiences()
        work_experiences_dumped = [
            work_experience.json_dump() for work_experience in work_experiences
        ]
        work_experiences_string = "\n".join(
            [
                f"{idx + 1}. {work_experience}"
                for idx, work_experience in enumerate(work_experiences)
            ]
        )
        self.interactor.writer(
            MessageType.INFO,
            f"Please select a work experience:\n{work_experiences_string}",
            title=MessageTitle.WORK_EXPERIENCE_LIST,
            extra_context=work_experiences_dumped,
        )
        work_experience_index = self.interactor.reader(
            prompt="Enter the number of the work experience"
        )
        if not is_valid_option_index_based(work_experience_index, work_experiences):
            self.interactor.writer(MessageType.ERROR, "Invalid option")
            return
        work_experience = work_experiences[int(work_experience_index) - 1]
        self.interactor.writer(
            MessageType.INFO, f"Work experience: {work_experience.company_name}"
        )
        self.interactor.writer(MessageType.INFO, f"Role: {work_experience.role}")
        self.interactor.writer(
            MessageType.INFO, f"Start Date: {work_experience.start_date}"
        )
        self.interactor.writer(
            MessageType.INFO, f"End Date: {work_experience.end_date}"
        )
        self.interactor.writer(
            MessageType.INFO, f"Description: {work_experience.description}"
        )

    def delete_work_experience(self):
        """
        Delete a work experience.
        """
        self.interactor.writer(MessageType.INFO, "Deleting a work experience...")
        work_experiences = WorkExperienceService.get_all_work_experiences()
        work_experiences_dumped = [
            work_experience.json_dump() for work_experience in work_experiences
        ]
        work_experiences_string = "\n".join(
            [
                f"{idx + 1}. {work_experience}"
                for idx, work_experience in enumerate(work_experiences)
            ]
        )
        self.interactor.writer(
            MessageType.INFO,
            f"Please select a work experience:\n{work_experiences_string}",
            title=MessageTitle.WORK_EXPERIENCE_LIST,
            extra_context=work_experiences_dumped,
        )
        work_experience_index = self.interactor.reader(
            prompt="Enter the number of the work experience"
        )
        if not is_valid_option_index_based(work_experience_index, work_experiences):
            self.interactor.writer(MessageType.ERROR, "Invalid option")
            return
        work_experience = work_experiences[int(work_experience_index) - 1]
        try:
            WorkExperienceService.delete_work_experience(work_experience.id)
            logger.info(
                f"Work experience deleted successfully: {work_experience.company_name}"
            )
            self.interactor.writer(
                MessageType.SUCCESS,
                f"Work experience deleted successfully: {work_experience.company_name}",
            )
        except Exception as e:
            logger.error(f"Error deleting work experience: {e}")
            self.interactor.writer(
                MessageType.ERROR, f"Error deleting work experience: {e}"
            )
            return

    def list_work_experiences(self):
        """
        List all work experiences.
        """
        self.interactor.writer(MessageType.INFO, "Listing all work experiences...")
        work_experiences = WorkExperienceService.get_all_work_experiences()
        work_experiences_dumped = [
            work_experience.json_dump() for work_experience in work_experiences
        ]
        tabulated_data = tabulate(
            work_experiences_dumped, headers="keys", tablefmt="grid"
        )
        self.interactor.writer(
            MessageType.INFO,
            tabulated_data,
            title=MessageTitle.WORK_EXPERIENCE_LIST,
            extra_context=work_experiences_dumped,
        )
