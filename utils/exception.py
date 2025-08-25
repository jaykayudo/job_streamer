from utils.logging import JobStreamerLogger

logger = JobStreamerLogger().get_logger()


class BaseException(Exception):
    """
    Base exception class for all exceptions.
    """

    def __init__(self, message: str | None = None, *, extra_info: dict | None = None):
        self.message = message
        logger.error(f"{self.__class__.__name__}: {self.message}")
        super().__init__(self.message)


class DriverException(BaseException):
    """
    Exception raised when there is an error in the driver.
    """

    pass


class StopProcessException(BaseException):
    """
    Exception raised when a process should be stopped.
    """

    pass


class StopSignalException(BaseException):
    """
    Exception raised when a stop signal is received.
    """

    pass


class InvalidCommandException(BaseException):
    """
    Exception raised when an invalid command is received.
    """

    pass
