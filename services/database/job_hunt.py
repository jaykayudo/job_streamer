import json
from typing import List, Optional

import storage.core.engine as _db
from storage.core.models import Bio, JobHunt, Resume
from utils.context import AutomationRequestContext


class JobHuntService:
    @classmethod
    def create_job_hunt(cls, context: AutomationRequestContext) -> JobHunt:
        """
        Create a JobHunt record from an AutomationRequestContext.

        Complex list fields are JSON-serialised. Bio and Resume are linked by
        their database IDs (both must already be persisted).
        """
        bio_id = context.bio.id if isinstance(context.bio, Bio) else None
        salary_min = str(context.salary_range.min) if context.salary_range else None
        salary_max = str(context.salary_range.max) if context.salary_range else None

        job_hunt = JobHunt(
            platform=context.platform,
            bio_id=bio_id,
            resume_id=context.resume.id,
            categories=json.dumps([c.model_dump() for c in context.categories]),
            locations=json.dumps([l.model_dump() for l in context.locations]),
            skills=json.dumps([s.model_dump() for s in context.skills]) if context.skills else None,
            hiring_types=json.dumps([h.model_dump() for h in context.hiring_types]) if context.hiring_types else None,
            industries=json.dumps([i.model_dump() for i in context.industries]) if context.industries else None,
            work_style=context.work_style.value if context.work_style else None,
            salary_min=salary_min,
            salary_max=salary_max,
            job_count=str(context.job_count),
            extra_job_selection_intruction=context.extra_job_selection_intruction,
            completed=False,
        )
        job_hunt.save()
        return job_hunt

    @classmethod
    def get_job_hunt_by_id(cls, job_hunt_id: str) -> Optional[JobHunt]:
        """
        Get a job hunt from the database by id
        """
        return _db.session.query(JobHunt).filter_by(id=job_hunt_id).first()

    @classmethod
    def get_all_job_hunts(cls) -> List[JobHunt]:
        """
        Return all JobHunt records ordered by creation date descending.
        """
        return (
            _db.session.query(JobHunt)
            .order_by(JobHunt.created_at.desc())
            .all()
        )

    @classmethod
    def mark_completed(cls, job_hunt_id: str) -> Optional[JobHunt]:
        """
        Mark a JobHunt as completed.
        """
        job_hunt = _db.session.query(JobHunt).filter_by(id=job_hunt_id).first()
        if job_hunt:
            job_hunt.completed = True
            _db.session.commit()
        return job_hunt