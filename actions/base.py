from abc import ABC, abstractmethod
from client.base.interactor import BaseInteractor
from typing import List
from utils.logging import JobStreamerLogger
from utils.types import MessageType

logger = JobStreamerLogger().get_logger()


class BaseAction(ABC):
    """
    This class represents the base action (commands) that can be perfomred in the application.
    This includes the actions for starting the job automation process, managing bios, resumes,
    and other related actions.
    All actions in their category should inherit from this class.
    """

    def __init__(self, interactor: BaseInteractor):
        self.interactor = interactor
        self.actions = {}

    @classmethod
    @abstractmethod
    def get_actions(cls) -> List[str]:
        """
        Get the actions of the action class.
        """
        pass

    def handle_action_command(self, command: str):
        """
        The is the main method that is the entry point for all actions.
        It collects the command from the user input and perform an action based on the command.
        """
        if command.lower() in self.actions:
            self.actions[command.lower()]()
        else:
            logger.error(f"Invalid command: {command}")
            self.interactor.writer(MessageType.ERROR, "Invalid command")
