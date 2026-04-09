"""
Debug runner for AutomatorGraph.

Usage:
    poetry run python -m agent.run --resume path/to/resume.pdf
    poetry run python -m agent.run --resume path/to/resume.pdf --bio "I am a Python developer..."
    poetry run python -m agent.run --resume path/to/resume.pdf --platform wellfound --job-count 3
"""
import argparse

from storage.core.models import Bio, Resume
from utils.context import AutomationRequestContext
from agent.automator import AutomatorGraph
from utils.logging import JobStreamerLogger

logger = JobStreamerLogger().get_logger()


def build_context(resume_path: str, bio_text: str, platform: str, job_count: int) -> AutomationRequestContext:
    resume = Resume(name="debug_resume", path=resume_path)
    bio = Bio(name="debug_bio", bio=bio_text)

    return AutomationRequestContext(
        platform=platform,
        bio=bio,
        categories=[],
        locations=[],
        resume=resume,
        job_count=job_count,
    )


def build_initial_state(context: AutomationRequestContext) -> dict:
    return {
        "platform": context.platform,
        "messages": [],
        "resume_object": context.resume,
        "bio_object": context.bio,
        "preferences_object": None,
        "categories": [],
        "job_details": [],
        "job_application_details": None,
        "applied_jobs": None,
        "location": None,
        "skills": None,
        "hiring_types": None,
        "industries": None,
        "work_style": None,
        "salary_range": None,
        "job_count": context.job_count,
        "extra_job_selection_intruction": None,
    }


def main():
    parser = argparse.ArgumentParser(description="Run the AutomatorGraph agent (debug mode)")
    parser.add_argument("--resume", required=True, help="Path to the resume PDF file")
    parser.add_argument(
        "--bio",
        default="Experienced software engineer with expertise in Python, Django, and React.",
        help="Short bio describing the candidate",
    )
    parser.add_argument(
        "--platform",
        default="wellfound",
        choices=["wellfound", "workable", "web3_career"],
        help="Target job platform (default: wellfound)",
    )
    parser.add_argument(
        "--job-count",
        type=int,
        default=5,
        help="Maximum number of jobs to retrieve (default: 5)",
    )
    args = parser.parse_args()

    logger.info(f"Starting debug run | platform={args.platform} | resume={args.resume}")

    context = build_context(
        resume_path=args.resume,
        bio_text=args.bio,
        platform=args.platform,
        job_count=args.job_count,
    )

    graph = AutomatorGraph(configuration=context)

    logger.info("Invoking graph...")
    final_state = graph.run_graph()

    logger.info("=" * 60)
    logger.info("FINAL STATE")
    logger.info("=" * 60)
    logger.info(f"Categories selected : {[c.name for c in final_state.get('categories', [])]}")
    logger.info(f"Jobs retrieved      : {[j.job.title for j in final_state.get('job_details', [])]}")
    logger.info(f"Applied jobs        : {final_state.get('applied_jobs', [])}")
    logger.info("\nMessages:")
    for msg in final_state.get("messages", []):
        logger.info(f"  [{msg.__class__.__name__}] {msg.content[:120]}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()