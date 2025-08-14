import os
from typing import Literal

Modules = Literal["workable", "wellfound", "web3_career"]


class Settings:
    """
    Singleton class for loading settings from environment variables
    and updating in program settings.
    """

    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(Settings, cls).__new__(cls)
            cls.instance.__load_settings_from_env()
            cls.instance._variable_settings()
            cls.instance._create_logs_dir()
        return cls.instance

    def __load_settings_from_env(self):
        """
        Load settings from environment variables.
        """
        self.DEBUG = bool(os.getenv("DEBUG", 1))
        self.SE_NODE_MAX_SESSIONS = os.getenv("SE_NODE_MAX_SESSIONS", 10)
        self.SE_NODE_SESSION_TIMEOUT = os.getenv("SE_NODE_SESSION_TIMEOUT", 300)
        self.REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
        self.REDIS_PORT = os.getenv("REDIS_PORT", 6379)
        self.REDIS_DB = os.getenv("REDIS_DB", 0)
        self.REDIS_URL = os.getenv(
            "REDIS_URL", f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        )
        self.SE_REMOTE_URL = os.getenv("SE_REMOTE_URL", "http://localhost:4444/wd/hub")
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///example.db")

    def _variable_settings(self):
        """
        Set the variables for the settings.
        """
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.MEDIA_DIR = os.path.join(self.BASE_DIR, "storage/media/")
        self.LOGS_DIR = os.path.join(self.BASE_DIR, "logs/")
        self.MODULES_DIR = os.path.join(self.BASE_DIR, "automation")

    def _create_logs_dir(self):
        """
        Create the logs directory if it does not exist.
        """
        if not os.path.exists(self.LOGS_DIR):
            os.makedirs(self.LOGS_DIR)

    def get_login_data(self, module: Modules):
        """
        Get login data for a given module.
        """
        settings_key_username = f"{module.upper()}_USERNAME"
        settings_key_password = f"{module.upper()}_PASSWORD"
        return {
            "username": os.getenv(settings_key_username),
            "password": os.getenv(settings_key_password),
        }

    def retrieve_all_modules(self) -> list[str]:
        """
        Retrieve all modules using os to list the directories in the automation directory.
        """
        modules = [
            f
            for f in os.listdir(self.MODULES_DIR)
            if os.path.isdir(os.path.join(self.MODULES_DIR, f))
        ]
        modules.remove("core")  # remove the core module as it is not a module
        return modules
