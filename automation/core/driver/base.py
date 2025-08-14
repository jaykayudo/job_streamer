from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.options import ArgOptions
from conf.settings import Settings
from typing import Self

SETTINGS = Settings()


class ChromeDriver:
    """
    Base class for all drivers.
    """

    def __init__(self, driver: webdriver.Remote):
        self.driver = driver

    @classmethod
    def get_driver_options_class(cls) -> ArgOptions:
        """
        Get the driver options class.
        """
        return webdriver.ChromeOptions()

    @classmethod
    def get_driver_class(cls) -> webdriver.Remote:
        """
        Get the driver class.
        """
        return webdriver.Remote

    @classmethod
    def _build_driver(cls, options: list[str]) -> webdriver.Remote:
        """
        Build the driver using the options and the driver class.
        """
        logger.info(f"Building driver with options: {options}")
        logger.info("Building the driver options")
        options_class = cls.build_options(options)
        logger.info(f"Driver options: {options_class}")
        logger.info("Building the driver")
        # driver_class = cls.get_driver_class()
        driver = webdriver.Remote(
            command_executor=SETTINGS.SE_REMOTE_URL, options=options_class
        )
        return driver

    @classmethod
    def initailize_driver(cls, options: list[str] = []) -> Self:
        """
        Initialize the driver.
        """
        logger.info("Initializing the driver")
        driver = cls._build_driver(options)
        logger.info("ChromeDriver initialized")
        return cls(driver)

    @classmethod
    def build_options(cls, options: list[str]):
        """
        Build the options for the driver.
        using the options class add arguments method to add the options.
        """
        options_class = cls.get_driver_options_class()
        for option in options:
            options_class.add_argument(option)
        return options_class

    def quit(self) -> None:
        """
        Quit the driver.
        """
        logger.info("Quitting the driver")
        self.driver.quit()
