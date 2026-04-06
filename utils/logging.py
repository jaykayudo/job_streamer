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
        logger.remove()
        self._stdout_sink_id = logger.add(
            sys.stdout,
            level="INFO",
            format="{time}| {level}| {name} - {message}",
            backtrace=False,
            diagnose=False,
            enqueue=True,
        )
        logger.add(
            log_file_path,
            level="INFO",
            rotation="10 MB",
            retention="10 days",
            enqueue=True,
        )
        return logger

    def add_sink(self, sink, **kwargs) -> int:
        """Add a custom sink and return its ID."""
        return self.logger.add(sink, **kwargs)

    def remove_stdout_sink(self):
        """Remove the stdout sink (used when a TUI takes over output)."""
        if hasattr(self, "_stdout_sink_id"):
            self.logger.remove(self._stdout_sink_id)
            self._stdout_sink_id = None

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
