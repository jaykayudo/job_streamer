from typing import List

from automation.core.automator.base import BaseAutomator
from automation.core.automator.types import Category, HiringType, InputElementType, JobApplicationDetails, JobApplicationDetailsAnswer, JobDetails, JobFilter , Industry, Location, Job
from automation.core.driver.service import BaseDriverService
from utils.types import Reader, SelectionType, SalaryRange
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebElement
from utils.exception import UserNotLoggedInException

class WellfoundAutomator(BaseAutomator, BaseDriverService):
    URLS = {
        "login": "/login",
        "jobs": "/jobs"
    }
    MODULE_NAME = "wellfound"
    def __init__(self):
        module_name = "wellfound"
        super().__init__(module_name)
    
    @classmethod
    def get_url(self) -> str:
        return "https://www.wellfound.com"
    
    
    def is_logged_in(self):
        avatar_image = self._find_element_by_xpath("//img[contains(@alt, 'Avatar for')]")
        return avatar_image is not None
    
    def get_full_url(self, path: str) -> str:
        if path in self.URLS:
            return f"{self.get_url()}{self.URLS[path]}"
        return f"{self.get_url()}{path}"
    
    def start(self):
        self.get_base_page()
        self._human_pause_page()
    
    def login(self, reader: Reader) -> bool:
        """
        Check if user is logged in first of all, if not 
        Steps: 
        1. Navigate to login pass
        2. Find login elements
        3. Enter login details
        """
        
        if self.is_logged_in():
            self.logger.info("User is already logged in.")
            return True
        try:
            email_id_name = "user_email"
            password_id_name = "user_password"
            self.logger.info("User is not logged in. Navigating to login page.")
            self.driver.get(self.get_full_url("login"))
            # Wait for the login page to load
            self.logger.debug("Waiting for login page to load...")
            self._wait_for_page_to_load(self.URLS["login"])
            self.logger.debug("Login page loaded. Finding login elements.")
            self._human_pause_page()
            email_input = self._find_element_by_id(email_id_name)
            password_input = self._find_element_by_id(password_id_name)
            login_button = self._find_element_by_xpath("//input[@name='commit' and @type='submit']")
            if not email_input or not password_input or not login_button:
                self.logger.error("One or more login elements not found.")
                return False
            self.logger.debug("Login elements found. Entering login details.")
            email_value = reader("Please enter your wellfound login email:")
            password_value = reader("Please enter your wellfound login password:")
            self._fill_element_with_value(email_input, email_value)
            self._human_pause_medium()
            self._fill_element_with_value(password_input, password_value)
            self._human_pause_medium()
            self._click_element(login_button)
            self.logger.debug("Submitting Login Details")
            self._wait_for_page_to_load(self.URLS["jobs"])
            self._human_pause_page()
            # Wait for the login process to complete and check if login was successful
            info_checker = self._find_element_by_xpath("//h2[contains(text(), 'Does this information look correct?')]")
            if info_checker and self._element_is_visible(info_checker):
                self.logger.debug("Found Info Verifier")
                modal = info_checker.find_element(By.XPATH, "ancestor::*[contains(@class, 'styles_modal')]")
                continue_btn = modal.find_element(By.XPATH, ".//button[contains(text(), 'Continue')]")
                self._human_pause_medium()
                self._click_element(continue_btn)
            return True
        except Exception as e:
            self.logger.error(f"An error occurred during login: {e}")
            return False
        
    def get_categories(self) -> tuple[List[Category], SelectionType]:
        """
        Steps:
        1. Navigate to jobs page (if not in jobs page)
        2. Find the Add a job title button
        3. Click the button to convert it to a search dropdown
        4. Click the dropdown to show the categories
        5. Extract the categories and return them
        """
        category_list: List[Category] = []
        selection_type = SelectionType.MULTIPLE
        if not self.is_logged_in():
            self.logger.error("User is not logged in.")
            raise UserNotLoggedInException("User is not logged in.")
        if self.URLS["jobs"] not in self.driver.current_url:
            self.logger.info("Not in jobs page. Navigating to jobs page.")
            self.driver.get(self.get_full_url("jobs"))
            self._wait_for_page_to_load(self.URLS["jobs"])
            self._human_pause_page()

        self.logger.debug("Searching for category button")
        add_jobs_button = self._find_element_by_xpath("//button[@data-test='SearchBar-RoleSelect-FocusButton']")
        if add_jobs_button is not None:
            self.logger.debug("Category button found. Clicking the button.")
        self._click_element(add_jobs_button)
        self._wait_for_element_to_be_visible(By.XPATH, "//input[@id='react-select-26-input']")
        self.logger.debug("Clicked on Add a job title button and waited for dropdown to appear.")
        self._human_pause_medium()
        role_wrapper = self._find_element_by_xpath("//div[@data-test='RoleSelectWrapper']")
        self._click_element(role_wrapper)
        self._wait_for_element_to_be_visible(By.XPATH,"//div[@id='select-menu']")
        self._human_pause_medium()
        self.logger.debug("All Categories Found.")
        select_menu = role_wrapper.find_element(By.XPATH, "//div[contains(@class, 'select__menu')]")
        categories = select_menu.find_elements(By.XPATH, "//div[contains(@class, 'select__option')]")
        for category in categories:
            category_name = category.text.strip()
            category_id = category.get_attribute("id")
            category_list.append(
                Category(
                    id = category_id,
                    unique_selector=f"//div[@id={category_id}]",
                    selector_type="xpath",
                    name = category_name
                )
            )
        self.logger.debug("Categories sucessfully extracted")

        return category_list, selection_type
    
    def get_hiring_types(self) -> List[HiringType]:
        return []
    
    def _apply_categories(self, categories: List[Category]):
        if not self.is_logged_in():
            self.logger.error("User is not logged in.")
            raise UserNotLoggedInException("User is not logged in.")
        if self.URLS["jobs"] not in self.driver.current_url:
            self.logger.info("Not in jobs page. Navigating to jobs page.")
            self.driver.get(self.get_full_url("jobs"))
            self._wait_for_page_to_load(self.URLS["jobs"])
        
        self.logger.debug("Searching for category button")
        add_jobs_button = self._find_element_by_xpath("//button[@data-test='SearchBar-RoleSelect-FocusButton']")
        if add_jobs_button is not None:
            self.logger.debug("Category button found. Clicking the button.")
        add_jobs_button.click()
        self._wait_for_element_to_be_visible(By.XPATH, "//input[@id='react-select-26-input']")
        self.logger.debug("Clicked on Add a job title button and waited for dropdown to appear.")
        role_wrapper = self._find_element_by_xpath("//div[@data-test='RoleSelectWrapper']")
        role_wrapper.click()
        self._wait_for_element_to_be_visible(By.XPATH,"//div[contains(@class, 'select__menu')]")
        self.logger.debug("All Categories Found.")
        select_menu = role_wrapper.find_element(By.XPATH, "//div[contains(@class, 'select__menu')]")
        for category in categories:
            category_element = select_menu.find_element(By.XPATH, f"//div[@id='{category.id}']")
            self._click_element(category_element)
            self._human_pause_short()
            self._click_element(role_wrapper)
            self._wait_for_element_to_be_visible(By.XPATH,"//div[contains(@class, 'select__menu')]")
            self._human_pause_short()
        self.logger.debug("Categories sucessfully Applied")
    
    def _apply_hiring_types(self, hiring_types: List[HiringType]):
        # TODO (v2): Implement this method to apply hiring type filters
        pass
    
    def _apply_industries(self, industries: List[Industry]):
        # TODO (v2): Implement this method to apply industry filters
        pass
    
    def _apply_salary_ranges(self, salary_ranges: List[SalaryRange]):
        # TODO (v2): Implement this method to apply salary range filters

        pass
    
    def _apply_locations(self, locations: List[Location]):
        # TODO (v2): Implement this method to apply location filters
        pass
    
    def get_jobs(self, filters: JobFilter, count: int = None):
        if not self.is_logged_in():
            self.logger.error("User is not logged in.")
            raise UserNotLoggedInException("User is not logged in.")
        if self.URLS["jobs"] not in self.driver.current_url:
            self.logger.info("Not in jobs page. Navigating to jobs page.")
            self.driver.get(self.get_full_url("jobs"))
            self._wait_for_page_to_load(self.URLS["jobs"])
        
        self._apply_categories(filters.categories)
        self.logger.debug("Applied category filters.")
        self._human_pause_medium()

        # Hide jobs that require me to apply to company website
        check_for_hide = self._find_element_by_xpath("//input[@name='showOffPlatformJobs' and @type='checkbox']")
        if check_for_hide:
            self._click_element(check_for_hide)
            self._human_pause_medium()

        all_jobs: List[Job] = []
        # get all jobs wrappers
        self.logger.debug("Retrieving jobs after applying filters.")
        self._human_pause_long()
        job_wrappers = self._find_elements_by_xpath("//div[@data-test='StartupResult']")
        for job_element in job_wrappers:
            job = self._extract_jobs(job_element)
            all_jobs.extend(job)
            if count and len(all_jobs) >= count:
                break
        return all_jobs

    def get_job_details(self, job: Job) -> JobDetails:
        if not self.is_logged_in():
            self.logger.error("User is not logged in.")
            raise UserNotLoggedInException("User is not logged in.")
        self.logger.debug(f"Getting details for job: {job.title} with id: {job.id}")
        self.driver.get(job.url)
        self._wait_for_page_to_load(self.get_full_url(job.url))
        self._human_pause_page()
        description_element = self._find_element_by_xpath("//div[contains(@class, 'styles_description')]")
        description = description_element.text.strip() if description_element else ""
        title_element = self._find_element_by_xpath("//div[contains(@class, 'styles_title')]")
        pay_range_element = title_element.find_element(By.XPATH, ".//div[contains(@class, 'styles_subheader')]")
        pay_range = pay_range_element.text.strip() if pay_range_element else None
        return JobDetails(
            job = job,
            description = description,
            pay_range = pay_range
        )
        
    def get_job_application_details(
        self, job: JobDetails
    ) -> List[JobApplicationDetails]:
        """
        Get the application details of a job
        """
        if not self.is_logged_in():
            self.logger.error("User is not logged in.")
            raise UserNotLoggedInException("User is not logged in.")
        self.logger.debug(f"Getting application details for job: {job.job.title} with id  : {job.job.id}")
        full_url = self.get_full_url(job.job.url)
        if self.driver.current_url != full_url:
            self.driver.get(self.get_full_url(job.job.url))
            self._wait_for_page_to_load(self.get_full_url(job.job.url))
            self._human_pause_page()
        self.logger.debug("Looking for Apply Button")
        self._human_pause_long()
        apply_button = self._find_element_by_xpath("//button[text()='Apply']")
        if apply_button is None:
            self.logger.debug("Apply button not found. This job might not be accepting applications or might require applying on company website.")
            return []
        self._click_element(apply_button)
        self._wait_for_element_to_be_visible(By.XPATH, "//form")
        self._human_pause_medium()
        # The labels are housing the input fields
        form_labels = self._find_elements_by_xpath("//form//label")
        application_details = []
        for label in form_labels:
            try:
                input_element = label.find_element(By.XPATH, ".//input | .//textarea | .//select")
                element_type = input_element.tag_name
                options = None
                id = input_element.get_attribute("id")
                if element_type == "input":
                    input_type = input_element.get_attribute("type")
                    unique_selector = f".//input[id='{id}]"
                    if input_type in ["text", "email", "password"]:
                        element_type = InputElementType.TEXT
                    elif input_type == "checkbox":
                        element_type = InputElementType.CHECKBOX
                    elif input_type == "radio":
                        element_type = InputElementType.RADIO
                    elif input_type == "file":
                        element_type = InputElementType.FILE
                    else:
                        element_type = InputElementType.TEXT
                elif element_type == "textarea":
                    element_type = InputElementType.TEXTAREA
                    unique_selector = f".//textarea[id='{id}]"
                elif element_type == "select":
                    element_type = InputElementType.SELECT
                    unique_selector =  f".//select[id='{id}]"
                    options = input_element.find_elements(By.XPATH, ".//option")
                    options = [option.text.strip() for option in options if option.get_attribute("value")]
                else:
                    element_type = InputElementType.TEXT
                    unique_selector = f".//input[id='{id}]"
                
                job_application_details = JobApplicationDetails(
                    id = input_element.get_attribute("id"),
                    unique_selector=unique_selector,
                    selector_type="xpath",
                    title=label.text.strip(),
                    element_type=element_type,
                    is_required=input_element.get_attribute("required") is not None,
                    options=options
                )
                application_details.append(job_application_details)
            except Exception as e:
                self.logger.error(f"Error extracting application detail for a label: {e}")
                raise e
        return application_details

    def apply_job(self, job: Job, application_details_answers: List[JobApplicationDetailsAnswer]) -> bool:
        if not self.is_logged_in():
            self.logger.error("User is not logged in.")
            raise UserNotLoggedInException("User is not logged in.")
        self.logger.debug(f"Getting application details for job: {job.job.title} with id  : {job.job.id}")
        full_url = self.get_full_url(job.job.url)
        if self.driver.current_url != full_url:
            self.driver.get(self.get_full_url(job.job.url))
            self._wait_for_page_to_load(self.get_full_url(job.job.url))
            self._human_pause_page()

        self._human_pause_long()
        apply_button = self._find_element_by_xpath("//button[text()='Apply']")
        if apply_button is None:
            self.logger.debug("Apply button not found. This job might not be accepting applications or might require applying on company website.")
            return False
        self._click_element(apply_button)
        self._wait_for_element_to_be_visible(By.XPATH, "//form")
        self._human_pause_medium()
        form = self._find_element_by_xpath("//form")
        for application_answer in application_details_answers:
            self.logger.debug(f"[apply_job] filling answer for question '{application_answer.application_details.title}'")
            input_element = form.find_element(By.XPATH, application_answer.application_details.unique_selector)
            self._human_pause_medium()
            self._fill_element_with_value(input_element, application_answer.value)

        self._human_pause_long()
        submit_button = self._find_element_by_xpath("//button[@data-test='JobApplicationModal--SubmitButton' and @type='submit']")
        if submit_button is None:
            return False
        self.logger.debug("[apply_job] Clicking submit button")
        self._click_element(submit_button)
        self._wait_until_element_not_visible(form)
        return True
            
            
        
    def _extract_jobs(self, element: WebElement) -> List[Job]:
        jobs = []   
        jobs_link_wrapper = element.find_elements(By.XPATH, ".//a[contains(@class, 'styles_jobLink')]")
        for job in jobs_link_wrapper:
            job_title = job.find_element(By.XPATH, ".//span[contains(@class, 'styles_title')]").text.strip()
            job_link = job.get_attribute("href")
            job_location = job.find_element(By.XPATH, ".//span[contains(@class, 'styles_locations')]").text.strip()
            jobs.append(
                Job(
                    id = job_link.split("/")[-1],
                    title = job_title,
                    url = job_link,
                    location = job_location,
                    platform = self.MODULE_NAME
                )
            )
        return jobs
    
            
            
        
        