from typing import List, TypeVar
import os
from datetime import datetime

from conf.settings import SETTINGS
from selenium.webdriver.common.by import By


SELECTOR_TYPE_TO_BY = {
    "xpath": By.XPATH,
    "css": By.CSS_SELECTOR,
    "id": By.ID,
    "class": By.CLASS_NAME,
    "name": By.NAME,
}

T = TypeVar("T")


def get_value_from_options(option: str, options: List[T]) -> T:
    """
    Get the value from the option
    """
    options_str = [str(option).lower() for option in options]
    option_str = str(option).lower()
    option_index = options_str.index(option_str)
    return options[option_index]


def handle_application_file_path_generation(platform: str, job_title: str) -> str:
    """
    Handle the application file path generation
    """
    files_platform_dir = os.path.join(SETTINGS.FILES_DIR, platform)
    if not os.path.exists(files_platform_dir):
        os.makedirs(files_platform_dir)
    current_date_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = os.path.join(
        files_platform_dir, f"{job_title}.{current_date_time}.json"
    )
    return file_name


def filter_model_with_unique_selector(unique_selector: str, models: List[T]) -> T:
    """
    Filter the model with the unique selector
    """
    for model in models:
        if model.unique_selector == unique_selector:
            return model
    return None


def filter_models_with_unique_selector(
    unique_selectors: List[str], models: List[T]
) -> List[T]:
    """
    Filter the models with the unique selectors
    """
    return [model for model in models if model.unique_selector in unique_selectors]


def get_by_for_selection_type(selection_type: str) -> By:
    """
    Get the by for the selection type
    """
    if selection_type == "" or selection_type not in SELECTOR_TYPE_TO_BY.keys():
        return By.XPATH
    return SELECTOR_TYPE_TO_BY[selection_type]
