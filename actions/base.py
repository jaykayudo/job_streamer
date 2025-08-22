from abc import ABC, abstractmethod
from client.base.interactor import BaseInteractor


class BaseAction(ABC):
    """
    This class represents the base action (commands) that can be perfomred in the application.
    This includes the actions for starting the job automation process, managing bios, resumes,
    and other related actions.
    All actions in their category should inherit from this class.
    """

    def __init__(self, interactor: BaseInteractor):
        self.interactor = interactor

    @abstractmethod
    def handle_action_command(self, command: str):
        """
        The is the main methos that all action class should implement.
        it collects the command from the user input and perform an action based on the command.
        """
        pass
