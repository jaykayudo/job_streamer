from conf.settings import Settings, Modules
from typing import Literal
from automation.core.pool import InstancesPool
from loguru import logger as loguru_logger
from selenium.webdriver.remote.webdriver import WebElement
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from time import sleep
from typing import Optional, Union, Tuple
import random

SETTINGS = Settings()


class BaseDriverService:
    """
    The service represents selenium actions that can be performed on the driver
    by the module.
    """

    def __init__(self, module_name: Modules):
        self.module = module_name
        self.pool_instance = InstancesPool(module_name)
        self.driver: webdriver.Remote = self.pool_instance.driver
        self.logger.info(f"Driver initialized for {self.module}")
        self.logger.info(f"Driver is active")

    @property
    def logger(self):
        """
        Get the logger for the module.
        """
        return loguru_logger

    @classmethod
    def get_url(cls) -> str:
        """
        Get the base url for the module.
        """
        raise NotImplementedError("This method should be implemented by the subclass")

    def get_base_page(self):
        return self.driver.get(self.get_url())

    def _initialize_user_window(self):
        pass

    def _close_user_window(self):
        self.driver.close()

    def _go_to_main_page(self):
        self.driver.get(url=self._get_url())

    def _find_element_by_id(self, id_name: str) -> Optional[WebElement]:
        try:
            return self.driver.find_element(By.ID, id_name)
        except NoSuchElementException:
            return None

    def _find_element_by_name(self, name: str) -> Optional[WebElement]:
        try:
            return self.driver.find_element(By.NAME, name)
        except NoSuchElementException:
            return None

    def _find_element_by_classname(self, name: str) -> Optional[WebElement]:
        try:
            return self.driver.find_element(By.CLASS_NAME, name)
        except NoSuchElementException:
            return None

    def _find_element_by_xpath(self, xpath: str) -> Optional[WebElement]:
        try:
            return self.driver.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return None

    def _fill_element_with_value(
        self, element: WebElement, value: Union[str, int, float]
    ) -> None:
        if isinstance(value, int) or isinstance(value, float):
            element.send_keys(value)

        if isinstance(value, str):
            for char in value:
                element.send_keys(char)
                sleep(random.randint(1, 10) / 10)
        return

    def _slow_send_keys(self, element: WebElement, string: str):
        for char in string:
            element.send_keys(char)
            sleep(random.randint(1, 10) / 10)

    def _click_element(self, element: WebElement) -> None:
        element.click()

    def _wait_for_page_to_load(self, url_to_contain: str, timeout: int = 900) -> None:
        try:
            WebDriverWait(driver=self.driver, timeout=timeout).until(
                EC.url_contains(url_to_contain)
            )
        except TimeoutException:
            return

    def _wait_for_page_to_load_using_script(self, timeout: int = 900) -> None:
        try:
            DOCUMENT_IS_READY_SCRIPT = "return document.readyState === 'complete'"
            WebDriverWait(driver=self.driver, timeout=timeout).until(
                lambda driver: driver.execute_script(script=DOCUMENT_IS_READY_SCRIPT)
            )
        except TimeoutException:
            return

    def _get_browser_window_size(self) -> Tuple[int, int]:
        window_size = self.driver.get_window_size()
        return window_size["width"], window_size["height"]

    def _build_storage_path_of_file(self, filename: str) -> str:
        storage_path = f"{self.media_path}/{filename}.png"
        return storage_path

    def _take_and_save_screenshot(self, filename: str) -> str:
        WINDOW_X, WINDOW_Y = self._get_browser_window_size()
        RESIZE_WINDOW_SCRIPT = f"window.scrollTo({WINDOW_X // 2}, {WINDOW_Y // 2})"
        storage_path = self._build_storage_path_of_file(filename=filename)
        self.driver.execute_script(script=RESIZE_WINDOW_SCRIPT)
        self.driver.save_screenshot(filename=storage_path)
        return storage_path
