from conf.settings import Settings
from typing import Literal

SETTINGS = Settings()

MODULES = SETTINGS.retrieve_all_modules()

ModuleName = Literal[tuple(MODULES)]


class BaseDriverService:
    """
    The service represents selenium actions that can be performed on the driver
    by the module.
    """

    def __init__(self, module_name: ModuleName):
        self.module = module_name
        
