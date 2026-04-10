import json

import pytest

from automation.core.automator.types import (
    Category,
    HiringType,
    Industry,
    Location,
    Skill,
)
from services.database.job_hunt import JobHuntService
from storage.core.models import Bio, JobHunt, Resume
from utils.context import AutomationRequestContext
from utils.types import SalaryRange, WorkStyle


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def make_resume(db_session) -> Resume:
    resume = Resume(name="Test Resume", path="/tmp/test_resume.pdf")
    resume.save()
    return resume


def make_bio(db_session) -> Bio:
    bio = Bio(name="Test Bio", bio="Python developer with 5 years of experience.")
    bio.save()
    return bio


def make_context(resume: Resume, bio: Bio | None = None, **overrides) -> AutomationRequestContext:
    defaults = dict(
        platform="wellfound",
        bio=bio,
        resume=resume,
        categories=[
            Category(id="cat_1", unique_selector="//li[1]", selector_type="xpath", name="Software Engineering"),
            Category(id="cat_2", unique_selector="//li[2]", selector_type="xpath", name="Data Science"),
        ],
        locations=[
            Location(id="loc_1", unique_selector="//li[1]", selector_type="xpath", name="Remote"),
        ],
        job_count=5,
    )
    defaults.update(overrides)
    return AutomationRequestContext(**defaults)


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class TestJobHuntModel:
    def test_repr(self, db_session):
        resume = make_resume(db_session)
        context = make_context(resume)
        job_hunt = JobHuntService.create_job_hunt(context)
        assert "wellfound" in repr(job_hunt)
        assert "completed=False" in repr(job_hunt)

    def test_json_dump_parses_list_fields(self, db_session):
        resume = make_resume(db_session)
        context = make_context(
            resume,
            skills=[Skill(id="s1", unique_selector="//li[1]", selector_type="xpath", name="Python")],
            hiring_types=[HiringType(id="ht1", unique_selector="//li[1]", selector_type="xpath", name="Full-Time")],
            industries=[Industry(id="i1", unique_selector="//li[1]", selector_type="xpath", name="FinTech")],
        )
        job_hunt = JobHuntService.create_job_hunt(context)
        dumped = job_hunt.json_dump()

        assert isinstance(dumped["categories"], list)
        assert isinstance(dumped["locations"], list)
        assert isinstance(dumped["skills"], list)
        assert isinstance(dumped["hiring_types"], list)
        assert isinstance(dumped["industries"], list)

        assert dumped["categories"][0]["name"] == "Software Engineering"
        assert dumped["locations"][0]["name"] == "Remote"
        assert dumped["skills"][0]["name"] == "Python"
        assert dumped["hiring_types"][0]["name"] == "Full-Time"
        assert dumped["industries"][0]["name"] == "FinTech"

    def test_json_dump_nullable_lists_are_none(self, db_session):
        resume = make_resume(db_session)
        context = make_context(resume)
        job_hunt = JobHuntService.create_job_hunt(context)
        dumped = job_hunt.json_dump()

        assert dumped["skills"] is None
        assert dumped["hiring_types"] is None
        assert dumped["industries"] is None

    def test_json_dump_includes_resume(self, db_session):
        resume = make_resume(db_session)
        context = make_context(resume)
        job_hunt = JobHuntService.create_job_hunt(context)
        dumped = job_hunt.json_dump()

        assert dumped["resume"]["name"] == "Test Resume"
        assert dumped["resume"]["path"] == "/tmp/test_resume.pdf"

    def test_json_dump_includes_bio(self, db_session):
        resume = make_resume(db_session)
        bio = make_bio(db_session)
        context = make_context(resume, bio=bio)
        job_hunt = JobHuntService.create_job_hunt(context)
        dumped = job_hunt.json_dump()

        assert dumped["bio"]["name"] == "Test Bio"

    def test_json_dump_bio_is_none_when_not_set(self, db_session):
        resume = make_resume(db_session)
        context = make_context(resume, bio=None)
        job_hunt = JobHuntService.create_job_hunt(context)
        dumped = job_hunt.json_dump()

        assert dumped["bio"] is None

    def test_json_dump_salary_range(self, db_session):
        resume = make_resume(db_session)
        context = make_context(resume, salary_range=SalaryRange(min=80000, max=120000))
        job_hunt = JobHuntService.create_job_hunt(context)
        dumped = job_hunt.json_dump()

        assert dumped["salary_min"] == "80000"
        assert dumped["salary_max"] == "120000"

    def test_json_dump_work_style(self, db_session):
        resume = make_resume(db_session)
        context = make_context(resume, work_style=WorkStyle.REMOTE)
        job_hunt = JobHuntService.create_job_hunt(context)
        dumped = job_hunt.json_dump()

        assert dumped["work_style"] == "remote"

    def test_json_dump_completed_defaults_false(self, db_session):
        resume = make_resume(db_session)
        context = make_context(resume)
        job_hunt = JobHuntService.create_job_hunt(context)

        assert job_hunt.json_dump()["completed"] is False


# ---------------------------------------------------------------------------
# Service tests
# ---------------------------------------------------------------------------

class TestJobHuntService:
    def test_create_job_hunt_minimal(self, db_session):
        resume = make_resume(db_session)
        context = make_context(resume)

        job_hunt = JobHuntService.create_job_hunt(context)

        assert job_hunt.id is not None
        assert job_hunt.platform == "wellfound"
        assert job_hunt.resume_id == resume.id
        assert job_hunt.bio_id is None
        assert job_hunt.completed is False
        assert job_hunt.job_count == "5"

    def test_create_job_hunt_with_bio(self, db_session):
        resume = make_resume(db_session)
        bio = make_bio(db_session)
        context = make_context(resume, bio=bio)

        job_hunt = JobHuntService.create_job_hunt(context)

        assert job_hunt.bio_id == bio.id

    def test_create_job_hunt_categories_stored_as_json(self, db_session):
        resume = make_resume(db_session)
        context = make_context(resume)

        job_hunt = JobHuntService.create_job_hunt(context)
        stored = json.loads(job_hunt.categories)

        assert len(stored) == 2
        assert stored[0]["name"] == "Software Engineering"
        assert stored[1]["name"] == "Data Science"

    def test_create_job_hunt_locations_stored_as_json(self, db_session):
        resume = make_resume(db_session)
        context = make_context(resume)

        job_hunt = JobHuntService.create_job_hunt(context)
        stored = json.loads(job_hunt.locations)

        assert len(stored) == 1
        assert stored[0]["name"] == "Remote"

    def test_create_job_hunt_optional_lists_are_none(self, db_session):
        resume = make_resume(db_session)
        context = make_context(resume)

        job_hunt = JobHuntService.create_job_hunt(context)

        assert job_hunt.skills is None
        assert job_hunt.hiring_types is None
        assert job_hunt.industries is None

    def test_create_job_hunt_with_all_optional_fields(self, db_session):
        resume = make_resume(db_session)
        context = make_context(
            resume,
            skills=[Skill(id="s1", unique_selector="//li[1]", selector_type="xpath", name="Python")],
            hiring_types=[HiringType(id="ht1", unique_selector="//li[1]", selector_type="xpath", name="Full-Time")],
            industries=[Industry(id="i1", unique_selector="//li[1]", selector_type="xpath", name="FinTech")],
            work_style=WorkStyle.REMOTE,
            salary_range=SalaryRange(min=80000, max=120000),
            extra_job_selection_intruction="Prefer startups.",
        )

        job_hunt = JobHuntService.create_job_hunt(context)

        assert json.loads(job_hunt.skills)[0]["name"] == "Python"
        assert json.loads(job_hunt.hiring_types)[0]["name"] == "Full-Time"
        assert json.loads(job_hunt.industries)[0]["name"] == "FinTech"
        assert job_hunt.work_style == "remote"
        assert job_hunt.salary_min == "80000"
        assert job_hunt.salary_max == "120000"
        assert job_hunt.extra_job_selection_intruction == "Prefer startups."

    def test_create_job_hunt_persisted_to_db(self, db_session):
        resume = make_resume(db_session)
        context = make_context(resume)

        JobHuntService.create_job_hunt(context)

        records = db_session.query(JobHunt).all()
        assert len(records) == 1

    def test_get_all_job_hunts_empty(self, db_session):
        results = JobHuntService.get_all_job_hunts()
        assert results == []

    def test_get_all_job_hunts_returns_all(self, db_session):
        resume = make_resume(db_session)
        JobHuntService.create_job_hunt(make_context(resume, platform="wellfound"))
        JobHuntService.create_job_hunt(make_context(resume, platform="workable"))

        results = JobHuntService.get_all_job_hunts()
        assert len(results) == 2

    def test_get_all_job_hunts_ordered_newest_first(self, db_session):
        resume = make_resume(db_session)
        first = JobHuntService.create_job_hunt(make_context(resume, platform="wellfound"))
        second = JobHuntService.create_job_hunt(make_context(resume, platform="workable"))

        results = JobHuntService.get_all_job_hunts()
        assert results[0].id == second.id
        assert results[1].id == first.id

    def test_mark_completed(self, db_session):
        resume = make_resume(db_session)
        job_hunt = JobHuntService.create_job_hunt(make_context(resume))
        assert job_hunt.completed is False

        updated = JobHuntService.mark_completed(job_hunt.id)

        assert updated.completed is True
        assert db_session.query(JobHunt).filter_by(id=job_hunt.id).first().completed is True

    def test_mark_completed_nonexistent_returns_none(self, db_session):
        result = JobHuntService.mark_completed("nonexistent-id")
        assert result is None
