from services.database.application import ApplicationService
from storage.core.models import Application
from conf.settings import SETTINGS
import os


def test_get_applications_by_platform(db_session):
    application = Application(
        job_title="Test Job Title",
        platform="wellfound",
        job_description="Test Job Description",
        job_url="https://www.test-url.com",
        job_location="Test Job Location",
        job_salary="Test Job Salary",
        job_company="Test Job Company",
        application_detail_file_path="path.json",
    )
    application.save()
    applications = ApplicationService.get_applications()
    assert len(applications) == 1
    assert applications[0].job_title == "Test Job Title"
    assert applications[0].platform == "wellfound"
    assert applications[0].job_description == "Test Job Description"
    assert applications[0].job_url == "https://www.test-url.com"
    assert applications[0].job_location == "Test Job Location"
    assert applications[0].job_salary == "Test Job Salary"
    assert applications[0].job_company == "Test Job Company"
    assert applications[0].application_detail_file_path == "path.json"


def test_create_application(db_session):
    application = ApplicationService.create_application(
        job_title="Test Job Title",
        platform="wellfound",
        job_description="Test Job Description",
        job_url="https://www.test-url.com",
        job_location="Test Job Location",
        job_salary="Test Job Salary",
        job_company="Test Job Company",
        job_company_url="https://www.test-company-url.com",
        application_detail_file_path="path.json",
    )
    assert application.job_title == "Test Job Title"
    assert application.platform == "wellfound"
    assert application.job_description == "Test Job Description"
    assert application.job_url == "https://www.test-url.com"
    assert application.job_location == "Test Job Location"
    assert application.job_salary == "Test Job Salary"
    assert application.job_company == "Test Job Company"
    assert application.job_company_url == "https://www.test-company-url.com"
    assert application.application_detail_file_path == os.path.join(
        SETTINGS.FILES_DIR, "path.json"
    )
