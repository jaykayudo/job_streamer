from conf.settings import Settings, Modules
from typing import Literal
from automation.core.pool import InstancesPool
from utils.logging import JobStreamerLogger
from selenium.webdriver.remote.webdriver import WebElement
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from typing import Optional, Union, Tuple, Any, Dict, List
import random
import math

SETTINGS = Settings()
logger = JobStreamerLogger().get_logger()

JS_COMMANDS = {
    "session": "return window.sessionStorage;",
    "local-storage": "return window.localStorage;",
    "domrect": "return arguments[0].getBoundingClientRect();",
    "new-window": "window.open('', {})"
}


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
        return logger

    @classmethod
    def get_url(cls) -> str:
        """
        Get the base url for the module.
        """
        raise NotImplementedError("This method should be implemented by the subclass")
    
    def is_logged_in(self) -> bool:
        """
        Check if the user is logged in.
        This method should be implemented by the subclass.
        """
        raise NotImplementedError("This method should be implemented by the subclass")

    def get_base_page(self):
        return self.driver.get(self.get_url())

    def _initialize_user_window(self):
        pass

    def _close_user_window(self):
        self.driver.close()

    def _go_to_main_page(self):
        self.driver.get(url=self.get_url())

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

    def _find_elements_by_name(self, name: str) -> Optional[List[WebElement]]:
        try:
            return self.driver.find_elements(By.NAME, name)
        except NoSuchElementException:
            return None

    def _find_elements_by_classname(self, name: str) -> Optional[List[WebElement]]:
        try:
            return self.driver.find_elements(By.CLASS_NAME, name)
        except NoSuchElementException:
            return None

    def _find_elements_by_xpath(self, xpath: str) -> Optional[List[WebElement]]:
        try:
            return self.driver.find_elements(By.XPATH, xpath)
        except NoSuchElementException:
            return None

    # ------------------------------------------------------------------
    # Human-like behaviour helpers
    # ------------------------------------------------------------------

    def _human_pause(self, mean: float = 1.2, sigma: float = 0.4, minimum: float = 0.3) -> None:
        """
        Sleep for a Gaussian-distributed duration centred on *mean* seconds.

        Using a normal distribution produces timing that clusters naturally
        around a human pace rather than the flat uniform spread that bot
        detectors are tuned to flag.  *minimum* prevents the sleep from going
        negative or impossibly short.
        """
        duration = max(minimum, random.gauss(mean, sigma))
        sleep(duration)

    def _human_pause_short(self) -> None:
        """Brief pause between minor interactions (mean ~0.5 s)."""
        self._human_pause(mean=0.5, sigma=0.15, minimum=0.2)

    def _human_pause_medium(self) -> None:
        """Pause between distinct UI actions (mean ~1.2 s)."""
        self._human_pause(mean=1.2, sigma=0.35, minimum=0.5)

    def _human_pause_long(self) -> None:
        """Longer pause simulating reading / thinking (mean ~2.5 s)."""
        self._human_pause(mean=2.5, sigma=0.6, minimum=1.2)

    def _human_pause_page(self) -> None:
        """Pause after a page navigation while the user 'looks around' (mean ~3 s)."""
        self._human_pause(mean=3.0, sigma=0.8, minimum=1.5)

    def _human_move_to_element(self, element: WebElement) -> None:
        """
        Move the mouse cursor to *element* via ActionChains.

        Sites inspect the absence of preceding mouse-move events as a
        strong bot signal.  This makes the interaction look like a real
        pointer travelling across the viewport.
        """
        try:
            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            actions.perform()
            self._human_pause_short()
        except Exception:
            pass  # graceful fallback — never block on cosmetic behaviour

    def _fill_element_with_value(
        self, element: WebElement, value: Union[str, int, float]
    ) -> None:
        """
        Type *value* into *element* character-by-character with Gaussian
        inter-keystroke delays, preceded by a mouse move and click to focus.
        """
        self._human_move_to_element(element)
        element.click()
        self._human_pause_short()

        if isinstance(value, (int, float)):
            element.send_keys(str(value))
            return

        if isinstance(value, str):
            for char in value:
                element.send_keys(char)
                # Keypress cadence: ~120 wpm → ~60 ms/char; Gaussian spread
                sleep(max(0.03, random.gauss(0.08, 0.04)))
            # Brief pause after finishing the field
            self._human_pause_short()

    def _slow_send_keys(self, element: WebElement, string: str):
        """Legacy alias — delegates to _fill_element_with_value."""
        self._fill_element_with_value(element, string)

    def _click_element(self, element: WebElement) -> None:
        """
        Move the mouse to *element*, pause briefly, then click.
        Avoids the instantaneous synthetic click that bot detectors flag.
        """
        self._human_move_to_element(element)
        self._human_pause_short()
        element.click()
        self._human_pause_medium()

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
        
    def _wait_for_element_to_be_visible(
        self, by: By, identifier: str, timeout: int = 900
    ) -> Optional[WebElement]:
        try:
            element = WebDriverWait(driver=self.driver, timeout=timeout).until(
                EC.visibility_of_element_located((by, identifier))
            )
            return element
        except TimeoutException:
            return None
        
    def _element_is_visible(self, element: WebElement) -> bool:
        return element.is_displayed()

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
    
    def _retrieve_session_storage(self) -> Dict[str, Any]:
        return self.driver.execute_script(script=JS_COMMANDS["session"])
    
    def _retrieve_local_storage(self) -> Dict[str, Any]:
        return self.driver.execute_script(script=JS_COMMANDS["local-storage"])
    
    def _implicitly_wait(self, seconds: int):
        WebDriverWait(self.driver, seconds).until(lambda driver: False)
    
    def _wait_until_element_not_visible(self, element: WebElement, timeout: int = 900):
        WebDriverWait(self.driver, timeout).until(
            EC.staleness_of(element)
        )
