import os
from typing import Literal
import toml
from conf.configuration import FULL_CONFIG
from loguru import logger

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
            cls.instance._create_missings_dir()
            cls.instance._load_automation_config()
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
        self.FILES_DIR = os.path.join(self.BASE_DIR, "storage/files/")
        self.STATIC_DIR = os.path.join(self.BASE_DIR, "storage/static")
        self.RESUMES_DIR = os.path.join(self.FILES_DIR, "storage/resumes")

    def _create_missings_dir(self):
        """
        Create the missing directories if they do not exist.
        """
        os.makedirs(self.MEDIA_DIR, exist_ok=True)
        os.makedirs(self.LOGS_DIR, exist_ok=True)
        os.makedirs(self.MODULES_DIR, exist_ok=True)
        os.makedirs(self.FILES_DIR, exist_ok=True)
        os.makedirs(self.STATIC_DIR, exist_ok=True)
        os.makedirs(self.RESUMES_DIR, exist_ok=True)

    def _load_automation_config(self):
        """
        Load the automation config from the configuration file.
        if the config file does not exist, create it from the FULL_CONFIG.
        and load the config from the file.
        """
        config_file_path = os.path.join(self.BASE_DIR, "conf/config.toml")

        try:
            # check if file exists
            if not os.path.exists(config_file_path):
                # create the file
                with open(config_file_path, "w") as f:
                    toml.dump(FULL_CONFIG, f)
                self.PLATFORM_CONFIG = FULL_CONFIG
            else:
                # load the config from the file
                with open(config_file_path, "r") as f:
                    self.PLATFORM_CONFIG = toml.load(f)
        except Exception as err:
            logger.error(f"Could not load platform config: {err}")
            self.PLATFORM_CONFIG = FULL_CONFIG

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


SETTINGS = Settings()
