from typing import List, Optional

from automation.core.automator.base import BaseAutomator
from automation.core.automator.types import (
    Category,
    HiringType,
    Industry,
    InputElementType,
    Job,
    JobApplicationDetails,
    JobApplicationDetailsAnswer,
    JobDetails,
    JobFilter,
    Location,
    Skill,
)
from conf.settings import Modules
from utils.types import Reader, SelectionType


class MockAutomator(BaseAutomator):
    """
    Mock automator for testing and development.
    Returns realistic-looking stub data without launching a real browser.
    """

    PLATFORM: Modules = "wellfound"

    def start(self):
        pass

    def login(self, reader: Reader):
        pass

    def logout(self):
        pass

    def get_categories(self) -> tuple[List[Category], SelectionType]:
        categories = [
            Category(id="cat_1", unique_selector="//li[@data-id='cat_1']", selector_type="xpath", name="Software Engineering"),
            Category(id="cat_2", unique_selector="//li[@data-id='cat_2']", selector_type="xpath", name="Data Science"),
            Category(id="cat_3", unique_selector="//li[@data-id='cat_3']", selector_type="xpath", name="Product Management"),
            Category(id="cat_4", unique_selector="//li[@data-id='cat_4']", selector_type="xpath", name="Design"),
            Category(id="cat_5", unique_selector="//li[@data-id='cat_5']", selector_type="xpath", name="Marketing"),
        ]
        return categories, SelectionType.MULTIPLE

    def get_locations(self) -> tuple[List[Location], SelectionType]:
        locations = [
            Location(id="loc_1", unique_selector="//li[@data-id='loc_1']", selector_type="xpath", name="Remote"),
            Location(id="loc_2", unique_selector="//li[@data-id='loc_2']", selector_type="xpath", name="San Francisco, CA"),
            Location(id="loc_3", unique_selector="//li[@data-id='loc_3']", selector_type="xpath", name="New York, NY"),
            Location(id="loc_4", unique_selector="//li[@data-id='loc_4']", selector_type="xpath", name="London, UK"),
        ]
        return locations, SelectionType.SINGLE

    def get_skills(self) -> tuple[List[Skill], SelectionType] | None:
        skills = [
            Skill(id="skill_1", unique_selector="//li[@data-id='skill_1']", selector_type="xpath", name="Python"),
            Skill(id="skill_2", unique_selector="//li[@data-id='skill_2']", selector_type="xpath", name="JavaScript"),
            Skill(id="skill_3", unique_selector="//li[@data-id='skill_3']", selector_type="xpath", name="React"),
            Skill(id="skill_4", unique_selector="//li[@data-id='skill_4']", selector_type="xpath", name="Django"),
            Skill(id="skill_5", unique_selector="//li[@data-id='skill_5']", selector_type="xpath", name="Machine Learning"),
        ]
        return skills, SelectionType.MULTIPLE

    def get_hiring_types(self) -> tuple[List[HiringType], SelectionType] | None:
        hiring_types = [
            HiringType(id="ht_1", unique_selector="//li[@data-id='ht_1']", selector_type="xpath", name="Full-Time"),
            HiringType(id="ht_2", unique_selector="//li[@data-id='ht_2']", selector_type="xpath", name="Part-Time"),
            HiringType(id="ht_3", unique_selector="//li[@data-id='ht_3']", selector_type="xpath", name="Contract"),
            HiringType(id="ht_4", unique_selector="//li[@data-id='ht_4']", selector_type="xpath", name="Internship"),
        ]
        return hiring_types, SelectionType.MULTIPLE

    def get_industries(self) -> tuple[List[Industry], SelectionType] | None:
        industries = [
            Industry(id="ind_1", unique_selector="//li[@data-id='ind_1']", selector_type="xpath", name="FinTech"),
            Industry(id="ind_2", unique_selector="//li[@data-id='ind_2']", selector_type="xpath", name="HealthTech"),
            Industry(id="ind_3", unique_selector="//li[@data-id='ind_3']", selector_type="xpath", name="EdTech"),
            Industry(id="ind_4", unique_selector="//li[@data-id='ind_4']", selector_type="xpath", name="E-Commerce"),
        ]
        return industries, SelectionType.MULTIPLE

    def get_jobs(
        self, filters: JobFilter, count: Optional[int] = None
    ) -> List[Job]:
        jobs = [
            Job(id="job_1", title="Senior Backend Engineer", url="https://mock.example.com/jobs/1", location="Remote", platform=self.PLATFORM),
            Job(id="job_2", title="Full-Stack Developer", url="https://mock.example.com/jobs/2", location="San Francisco, CA", platform=self.PLATFORM),
            Job(id="job_3", title="ML Engineer", url="https://mock.example.com/jobs/3", location="Remote", platform=self.PLATFORM),
            Job(id="job_4", title="Frontend Engineer", url="https://mock.example.com/jobs/4", location="New York, NY", platform=self.PLATFORM),
            Job(id="job_5", title="DevOps Engineer", url="https://mock.example.com/jobs/5", location="Remote", platform=self.PLATFORM),
        ]
        if count is not None:
            jobs = jobs[:count]
        return jobs

    def get_job_details(self, job: Job) -> JobDetails:
        descriptions = {
            "job_1": (
                "We are looking for a Senior Backend Engineer to join our platform team. "
                "You will design and build scalable APIs, lead architecture discussions, "
                "and mentor junior engineers. Required: 5+ years Python, strong SQL skills, "
                "experience with distributed systems."
            ),
            "job_2": (
                "Full-Stack Developer to work across our React frontend and Django backend. "
                "You will own features end-to-end, from DB schema to pixel-perfect UI. "
                "Required: React, Django/DRF, PostgreSQL, 3+ years experience."
            ),
            "job_3": (
                "ML Engineer to productionise machine learning models and build data pipelines. "
                "Work with the research team to deploy and monitor models at scale. "
                "Required: Python, PyTorch or TensorFlow, MLOps experience."
            ),
            "job_4": (
                "Frontend Engineer to build intuitive, performant web applications. "
                "You'll collaborate closely with designers and backend engineers. "
                "Required: React, TypeScript, CSS, accessibility experience a plus."
            ),
            "job_5": (
                "DevOps Engineer to maintain and improve our cloud infrastructure. "
                "Own CI/CD pipelines, Kubernetes clusters, and observability stack. "
                "Required: AWS/GCP, Terraform, Kubernetes, Python scripting."
            ),
        }
        companies = {
            "job_1": ("Acme Corp", "$120k – $160k"),
            "job_2": ("Buildly Inc", "$100k – $140k"),
            "job_3": ("DataDriven Co", "$130k – $170k"),
            "job_4": ("PixelPerfect Ltd", "$90k – $120k"),
            "job_5": ("CloudBase Systems", "$110k – $150k"),
        }
        desc = descriptions.get(job.id, "Job description not available.")
        company, pay = companies.get(job.id, ("Unknown Company", None))
        return JobDetails(
            job=job,
            description=desc,
            pay_range=pay,
            company=company,
            company_description=f"{company} is a fast-growing startup building innovative products.",
            posted_date="2026-04-01",
        )

    def get_job_application_details(
        self, job: JobDetails
    ) -> List[JobApplicationDetails]:
        return [
            JobApplicationDetails(
                id="q_1",
                unique_selector="//input[@name='full_name']",
                selector_type="xpath",
                title="Full Name",
                element_type=InputElementType.TEXT,
                is_required=True,
            ),
            JobApplicationDetails(
                id="q_2",
                unique_selector="//input[@name='email']",
                selector_type="xpath",
                title="Email Address",
                element_type=InputElementType.TEXT,
                is_required=True,
            ),
            JobApplicationDetails(
                id="q_3",
                unique_selector="//textarea[@name='cover_letter']",
                selector_type="xpath",
                title="Why do you want to work here?",
                element_type=InputElementType.TEXTAREA,
                is_required=True,
            ),
            JobApplicationDetails(
                id="q_4",
                unique_selector="//select[@name='experience_years']",
                selector_type="xpath",
                title="Years of relevant experience",
                element_type=InputElementType.SELECT,
                is_required=True,
                options=["0-1", "1-3", "3-5", "5-10", "10+"],
            ),
            JobApplicationDetails(
                id="q_5",
                unique_selector="//input[@name='work_authorization']",
                selector_type="xpath",
                title="Are you authorized to work in this country?",
                element_type=InputElementType.RADIO,
                is_required=True,
                options=["Yes", "No"],
            ),
            JobApplicationDetails(
                id="q_6",
                unique_selector="//input[@name='linkedin']",
                selector_type="xpath",
                title="LinkedIn Profile URL",
                element_type=InputElementType.TEXT,
                is_required=False,
            ),
        ]

    def search_jobs(self, query: str) -> List[Job]:
        all_jobs = self.get_jobs()
        query_lower = query.lower()
        return [j for j in all_jobs if query_lower in j.title.lower()]

    def apply_job(
        self, job: JobDetails, application_details: List[JobApplicationDetailsAnswer]
    ) -> bool:
        return True