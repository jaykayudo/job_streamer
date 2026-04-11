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
        Top-level entry point for all actions.

        Any exception raised anywhere below this call (services, automators,
        LLM calls, DB operations, etc.) is caught here so the client is never
        interrupted.  Known project exceptions are reported as errors;
        unexpected exceptions are logged with a full traceback.
        """
        from utils.exception import (
            DriverException,
            InvalidCommandException,
            StopProcessException,
            StopSignalException,
        )

        if command.lower() not in self.actions:
            logger.error(f"Invalid command: {command}")
            self.interactor.writer(MessageType.ERROR, f"Unknown command: '{command}'")
            return

        try:
            self.actions[command.lower()]()

        except StopSignalException as exc:
            # Intentional stop — info level, no user-facing error
            logger.info(f"Stop signal received: {exc.message}")

        except StopProcessException as exc:
            logger.warning(f"Process stopped: {exc.message}")
            self.interactor.writer(MessageType.WARNING, exc.message or "Process stopped.")

        except InvalidCommandException as exc:
            logger.error(f"Invalid command: {exc.message}")
            self.interactor.writer(MessageType.ERROR, exc.message or "Invalid command.")

        except DriverException as exc:
            logger.error(f"Driver error: {exc.message}")
            self.interactor.writer(
                MessageType.ERROR,
                f"Browser driver error: {exc.message or 'unexpected driver failure'}",
            )

        except Exception as exc:
            logger.exception(
                f"Unhandled exception in '{command}' "
                f"({self.__class__.__name__}): {exc}"
            )
            self.interactor.writer(
                MessageType.ERROR,
                f"An unexpected error occurred: {exc}",
            )
