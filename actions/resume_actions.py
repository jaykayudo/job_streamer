from actions.base import BaseAction
from client.base.interactor import BaseInteractor
from utils.types import MessageType
from services.database.resume import ResumeService


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
            MessageType.INFO, "Please provide the path of the resume"
        )
        file_path = self.interactor.reader(prompt="Enter the path of the resume")
        resume = ResumeService.create_resume(name=name, file_path=file_path)
        self.interactor.writer(
            MessageType.SUCCESS, f"Resume created successfully: {resume.name}"
        )

    def delete_resume(self):
        """
        Delete a resume.
        """
        self.interactor.writer(MessageType.INFO, "Deleting a resume...")
        self.interactor.writer(
            MessageType.INFO, "Please provide the name of the resume"
        )
        name = self.interactor.reader(prompt="Enter the name of the resume")
        try:
            ResumeService.delete_resume(name=name)
            self.interactor.writer(
                MessageType.SUCCESS, f"Resume deleted successfully: {name}"
            )
        except Exception as e:
            self.interactor.writer(MessageType.ERROR, f"Error deleting resume: {e}")

    def list_resumes(self):
        """
        List all resumes.
        """
        resumes = ResumeService.get_resumes()
        self.interactor.writer(MessageType.INFO, "Listing all resumes...")
        for resume in resumes:
            self.interactor.writer(
                MessageType.INFO, f"Resume: {resume.name} - {resume.path}"
            )
