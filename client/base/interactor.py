from abc import ABC, abstractmethod
from utils.types import MessageType


class BaseInteractor(ABC):
    """
    This class represents the functionality needed for the I/O interaction with any client.
    All client should have its own implementation of this class.
    """

    @abstractmethod
    def writer(
        self, message_type: MessageType, message: str, extra_context: dict | None = None
    ):
        """
        Write a message to the client.
        """
        pass

    @abstractmethod
    def reader(
        self,
        prompt: str,
        multiline: bool = False,
        extra_context: dict | None = None,
    ) -> str:
        """
        Read a message from the client.
        """
        pass
