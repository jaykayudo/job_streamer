from actions.base import BaseAction
from client.base.interactor import BaseInteractor
from utils.types import MessageType
from utils.logging import JobStreamerLogger
from typing import List


class HelpActions(BaseAction):
    def __init__(self, interactor: BaseInteractor):
        super().__init__(interactor)

    @classmethod
    def get_actions(cls) -> List[str]:
        """
        Get the actions of the help action class.
        """
        return []

    def handle_action_command(self, command: str):
        """
        Handle the action command.
        """
        self.interactor.writer(MessageType.INFO, "Displaying help...")
        self.interactor.writer(MessageType.INFO, "Available actions:")

        message = """
            1. Create a bio: (command: bio create)
            2. List all bios: (command: bio list)
            3. Get a bio: (command: bio get)
            4. Delete a bio: (command: bio delete)
            5. Create a project: (command: project create)
            6. List all projects: (command: project list)
            7. Get a project: (command: project get)
            8. Delete a project: (command: project delete)
            9. Create a resume: (command: resume create)
            10. List all resumes: (command: resume list)
            11. Delete a resume: (command: resume delete)
            12. Create a work experience: (command: work_experience create)
            13. List all work experiences: (command: work_experience list)
            14. Delete a work experience: (command: work_experience delete)
            15. List all preferences: (command: preference list)
            16. Delete a preference: (command: preference delete)
            17. List all applications: (command: application list)
            18. Get an application: (command: application get)
            19. Delete an application: (command: application delete)
            20. Start a job hunt: (command: job_hunt start)
            21. Job Hunt History: (command: job_hunt history)
        """
        self.interactor.writer(MessageType.INFO, message)
