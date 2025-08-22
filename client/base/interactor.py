from abc import ABC, abstractmethod
from utils.types import MessageType, MessageTitle


class BaseInteractor(ABC):
    """
    This class represents the functionality needed for the I/O interaction with any client.
    All client should have its own implementation of this class.
    """

    @abstractmethod
    def writer(
        self,
        message_type: MessageType,
        message: str,
        title: MessageTitle | None = None,
        extra_context: dict | list | None = None,
    ):
        """
        Write a message to the client.
        Args:
            message_type: The type of message to write
            message: The message to write
            title: The title of the message
            (this idea behind this title is that other interactors can use
            this title to display the message based on the extra context if provided)
            extra_context: Extra context to write  with the message:
            (this is used to display the message based on the extra context if provided)
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
