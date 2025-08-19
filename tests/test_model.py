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

    dict_data = application.json_dump()
    keys = dict_data.keys()
    assert "id" in keys
    assert "job_title" in keys
    assert "job_description" in keys
    assert "job_url" in keys
    assert "job_location" in keys
    assert "job_salary" in keys
    assert "created_at" in keys
    assert "updated_at" in keys

    assert dict_data["job_title"] == "Test Job Title"
    assert dict_data["job_description"] == "Test Job Description"
    assert dict_data["job_url"] == "https://www.google.com"
    assert dict_data["job_location"] == "Test Job Location"
    assert dict_data["job_salary"] == "Test Job Salary"

    assert dict_data["id"] == application.id
    assert dict_data["created_at"] == application.created_at
    assert dict_data["updated_at"] == application.updated_at


def test_resume(db_session):
    resume = Resume(name="Test Resume", path="test.pdf")
    db_session.add(resume)
    db_session.commit()
    db_session.refresh(resume)
    assert resume.name == "Test Resume"
    assert resume.path == "test.pdf"

    dict_data = resume.json_dump()
    keys = dict_data.keys()
    assert "id" in keys
    assert "name" in keys
    assert "path" in keys
    assert "created_at" in keys
    assert "updated_at" in keys

    assert dict_data["name"] == "Test Resume"
    assert dict_data["path"] == "test.pdf"

    assert dict_data["id"] == resume.id
    assert dict_data["created_at"] == resume.created_at
    assert dict_data["updated_at"] == resume.updated_at


def test_bio(db_session):
    bio = Bio(name="Test Bio", bio="Test Bio")
    db_session.add(bio)
    db_session.commit()
    db_session.refresh(bio)
    assert bio.name == "Test Bio"
    assert bio.bio == "Test Bio"

    dict_data = bio.json_dump()
    keys = dict_data.keys()
    assert "id" in keys
    assert "name" in keys
    assert "bio" in keys
    assert "projects" in keys
    assert "work_experiences" in keys
    assert "created_at" in keys
    assert "updated_at" in keys

    assert dict_data["name"] == "Test Bio"
    assert dict_data["bio"] == "Test Bio"
    assert dict_data["projects"] == []
    assert dict_data["work_experiences"] == []

    assert dict_data["id"] == bio.id
    assert dict_data["created_at"] == bio.created_at
    assert dict_data["updated_at"] == bio.updated_at


def test_category(db_session):
    category = Category(name="Test Category")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    assert category.name == "Test Category"

    dict_data = category.json_dump()
    keys = dict_data.keys()
    assert "id" in keys
    assert "name" in keys
    assert "created_at" in keys
    assert "updated_at" in keys

    assert dict_data["name"] == "Test Category"
    assert dict_data["id"] == category.id
    assert dict_data["created_at"] == category.created_at
    assert dict_data["updated_at"] == category.updated_at


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

    dict_data = saved_preference.json_dump()
    keys = dict_data.keys()
    assert "id" in keys
    assert "name" in keys
    assert "module_name" in keys
    assert "preferences" in keys
    assert "created_at" in keys
    assert "updated_at" in keys

    assert dict_data["name"] == "Test Saved Preference"
    assert dict_data["module_name"] == "Test Module"
    assert dict_data["preferences"] == [category.json_dump()]

    assert dict_data["id"] == saved_preference.id
    assert dict_data["created_at"] == saved_preference.created_at
    assert dict_data["updated_at"] == saved_preference.updated_at
