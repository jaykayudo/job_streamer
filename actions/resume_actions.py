from actions.base import BaseAction
from client.base.interactor import BaseInteractor
from utils.types import MessageType
from services.database.resume import ResumeService
from utils.logging import JobStreamerLogger
from utils.types import MessageTitle
from tabulate import tabulate

logger = JobStreamerLogger().get_logger()


class ResumeActions(BaseAction):
    def __init__(self, interactor: BaseInteractor):
        super().__init__(interactor)

        self.actions = {
            "create": self.create_resume,
            "delete": self.delete_resume,
            "list": self.list_resumes,
        }

    def handle_action_command(self, command: str):
        """
        Handle the action command.
        """
        if command in self.actions:
            self.actions[command]()
        else:
            logger.error(f"Invalid command: {command}")
            self.interactor.writer(MessageType.ERROR, "Invalid command")

    def create_resume(self):
        """
        Create a new resume.
        """
        self.interactor.writer(MessageType.INFO, "Creating a new resume...")
        self.interactor.writer(
            MessageType.INFO, "Please provide the name of the resume"
        )
        name = self.interactor.reader(prompt="Enter the name of the resume")
        self.interactor.writer(
            MessageType.INFO,
            "Please provide the path of the resume",
        )
        file_path = self.interactor.reader(prompt="Enter the path of the resume")
        try:
            resume = ResumeService.create_resume(name=name, file_path=file_path)
        except Exception as e:
            logger.error(f"Error creating resume: {e}")
            self.interactor.writer(MessageType.ERROR, f"Error creating resume: {e}")
            return
        self.interactor.writer(
            MessageType.SUCCESS, f"Resume created successfully: {resume.name}"
        )

    def delete_resume(self):
        """
        Delete a resume.
        """
        self.interactor.writer(MessageType.INFO, "Deleting a resume...")
        self.interactor.writer(
            MessageType.INFO,
            "Please provide the name of the resume",
        )
        name = self.interactor.reader(prompt="Enter the name of the resume")
        try:
            ResumeService.delete_resume(name=name)
            self.interactor.writer(
                MessageType.SUCCESS, f"Resume deleted successfully: {name}"
            )
        except Exception as e:
            logger.error(f"Error deleting resume: {e}")
            self.interactor.writer(MessageType.ERROR, f"Error deleting resume: {e}")

    def list_resumes(self):
        """
        List all resumes.
        """
        resumes = ResumeService.get_resumes()
        self.interactor.writer(MessageType.INFO, "Listing all resumes...")
        resumes_dumped = [resume.json_dump() for resume in resumes]
        tabulated_data = tabulate(resumes_dumped, headers="keys", tablefmt="grid")
        self.interactor.writer(
            MessageType.INFO,
            tabulated_data,
            title=MessageTitle.RESUME_LIST,
            extra_context=resumes_dumped,
        )
