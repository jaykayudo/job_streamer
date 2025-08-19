from loguru import logger
from datetime import datetime
from conf.settings import SETTINGS
import os
import sys


class JobStreamerLogger:
    """
    The logger for the job streamer.
    """

    instance = None
    logger: logger = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(JobStreamerLogger, cls).__new__(cls)
            cls.logger = cls.instance.setup_logger()
        return cls.instance

    def setup_logger(self) -> logger:
        """
        Setup the logger.
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        log_file_path = os.path.join(
            SETTINGS.LOGS_DIR, f"job-streamer-{current_date}.log"
        )
        logger.add(
            log_file_path,
            level="INFO",
            rotation="10 MB",
            retention="10 days",
            enqueue=True,
        )
        return logger

    def get_logger(self) -> logger:
        """
        Get the logger.
        """
        return self.logger

    def handle_exception(self, e: Exception):
        """
        Handle an exception.
        """
        self.logger.error(f"Exception: {e}")
