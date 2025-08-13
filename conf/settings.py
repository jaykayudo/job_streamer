import os
from typing import Literal

LoginModule = Literal["workable", "wellfound", "web3_career"]


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
        return cls.instance

    def __load_settings_from_env(self):
        """
        Load settings from environment variables.
        """
        self.SE_NODE_OVERRIDE_MAX_SESSIONS = os.getenv(
            "SE_NODE_OVERRIDE_MAX_SESSIONS", "true"
        )
        self.SE_NODE_MAX_SESSIONS = os.getenv("SE_NODE_MAX_SESSIONS", 10)
        self.SE_NODE_SESSION_TIMEOUT = os.getenv("SE_NODE_SESSION_TIMEOUT", 300)
        self.REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
        self.REDIS_PORT = os.getenv("REDIS_PORT", 6379)
        self.REDIS_DB = os.getenv("REDIS_DB", 0)
        self.REDIS_URL = os.getenv(
            "REDIS_URL", f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        )

    def get_login_data(self, module: LoginModule):
        """
        Get login data for a given module.
        """
        settings_key_username = f"{module.upper()}_USERNAME"
        settings_key_password = f"{module.upper()}_PASSWORD"
        return {
            "username": os.getenv(settings_key_username),
            "password": os.getenv(settings_key_password),
        }
