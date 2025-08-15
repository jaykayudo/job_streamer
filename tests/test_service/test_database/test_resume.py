from services.database.resume import ResumeService
from storage.core.models import Resume
from conf.settings import SETTINGS
import os


def test_create_resume(db_session):
    resume = ResumeService.create_resume(
        name="Test Resume",
        file_path="path.pdf",
    )
    resumes = db_session.query(Resume).all()
    assert len(resumes) == 1
    assert resumes[0].name == "Test Resume"
    assert resumes[0].path == os.path.join(SETTINGS.RESUMES_DIR, "path.pdf")


def test_get_resume(db_session):
    resume = Resume(
        name="Test Resume",
        path=os.path.join(SETTINGS.RESUMES_DIR, "path.pdf"),
    )
    resume.save()
    resume = ResumeService.get_resume("Test Resume")
    assert resume.name == "Test Resume"
    assert resume.path == os.path.join(SETTINGS.RESUMES_DIR, "path.pdf")


# def test_delete_resume(db_session):
#     resume = Resume(
#         name="Test Resume",
#         path="path.pdf",
#     )
#     resume.save()
#     resumes = db_session.query(Resume).all()
#     assert len(resumes) == 1
#     ResumeService.delete_resume("Test Resume")
#     resumes = db_session.query(Resume).all()
#     assert len(resumes) == 0
