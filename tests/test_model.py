from storage.core.models import Application, Resume, Bio, SavedPreference, Category


def test_application(db_session):
    application = Application(
        job_title="Test Job Title",
        platform="wellfound",
        job_description="Test Job Description",
        job_url="https://www.google.com",
        job_location="Test Job Location",
        job_salary="Test Job Salary",
        job_company="Test Job Company",
        job_company_url="https://www.google.com",
        application_detail_file_path="test.pdf",
    )
    db_session.add(application)
    db_session.commit()
    db_session.refresh(application)
    assert application.job_title == "Test Job Title"
    assert application.job_description == "Test Job Description"
    assert application.job_url == "https://www.google.com"
    assert application.job_location == "Test Job Location"
    assert application.job_salary == "Test Job Salary"


def test_resume(db_session):
    resume = Resume(name="Test Resume", path="test.pdf")
    db_session.add(resume)
    db_session.commit()
    db_session.refresh(resume)
    assert resume.name == "Test Resume"
    assert resume.path == "test.pdf"


def test_bio(db_session):
    bio = Bio(name="Test Bio", bio="Test Bio")
    db_session.add(bio)
    db_session.commit()
    db_session.refresh(bio)
    assert bio.name == "Test Bio"
    assert bio.bio == "Test Bio"


def test_category(db_session):
    category = Category(name="Test Category")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    assert category.name == "Test Category"


def test_saved_preference(db_session):
    category = Category(name="Test Category 1")
    saved_preference = SavedPreference(
        name="Test Saved Preference", module_name="Test Module"
    )
    saved_preference.preferences.append(category)
    db_session.add(category)
    db_session.add(saved_preference)
    db_session.commit()
    db_session.refresh(saved_preference)
    assert saved_preference.name == "Test Saved Preference"
    assert saved_preference.module_name == "Test Module"
    assert category in saved_preference.preferences
