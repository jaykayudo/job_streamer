from __future__ import annotations

import threading
from typing import List

from tabulate import tabulate

from actions.base import BaseAction
from agent.automator import AutomatorGraph
from automation.core.automator.types import Category, Location
from client.base.interactor import BaseInteractor
from conf.settings import SETTINGS
from services.database.bio import BioService
from services.database.job_hunt import JobHuntService
from services.database.resume import ResumeService
from storage.core.models import Bio, Resume
from utils.context import AutomationRequestContext
from utils.logging import JobStreamerLogger
from utils.types import MessageType, WorkStyle

logger = JobStreamerLogger().get_logger()

PAGE_SIZE = 10
NEXT_PAGE_SENTINEL = "99"


class JobHuntActions(BaseAction):
    def __init__(self, interactor: BaseInteractor):
        super().__init__(interactor)
        self.actions = {
            "start": self.start,
            "history": self.history,
        }

    @classmethod
    def get_actions(cls) -> List[str]:
        return ["start", "history"]

    # ------------------------------------------------------------------
    # Public sub-commands
    # ------------------------------------------------------------------

    def start(self):
        """
        Walk the user through the job hunt setup and launch the automation
        graph on a background thread.
        """
        self.interactor.writer(MessageType.INFO, "Starting job hunt setup...")

        platform = self._prompt_platform()
        if platform is None:
            return

        categories = self._prompt_categories(platform)
        if categories is None:
            return

        bio = self._prompt_bio()

        resume = self._prompt_resume()
        if resume is None:
            return

        location = self._prompt_location()
        salary_range = self._prompt_salary_range()
        work_style = self._prompt_work_style()
        job_count = self._prompt_job_count()
        extra_instruction = self._prompt_extra_instruction()

        context = AutomationRequestContext(
            platform=platform,
            bio=bio,
            categories=categories,
            locations=(
                [Location(id="custom", unique_selector="", selector_type="xpath", name=location)]
                if location else []
            ),
            resume=resume,
            work_style=work_style,
            salary_range=salary_range,
            job_count=job_count,
            extra_job_selection_intruction=extra_instruction or None,
        )

        try:
            JobHuntService.create_job_hunt(context)
        except Exception as e:
            logger.warning(f"[job_hunt] Could not persist job hunt record: {e}")

        self.interactor.writer(
            MessageType.SUCCESS,
            f"Job hunt started for platform '{platform}'. "
            f"Targeting {job_count} job(s). Running in background...",
        )
        thread = threading.Thread(
            target=self._run_graph,
            args=(context,),
            daemon=True,
        )
        thread.start()

    def history(self):
        """
        Display all past job hunt runs.
        """
        records = JobHuntService.get_all_job_hunts()
        if not records:
            self.interactor.writer(MessageType.INFO, "No job hunt history found.")
            return

        rows = [
            {
                "id": r.id[:8] + "...",
                "platform": r.platform,
                "job_count": r.job_count,
                "work_style": r.work_style or "-",
                "completed": r.completed,
                "created_at": str(r.created_at)[:19],
            }
            for r in records
        ]
        self.interactor.writer(
            MessageType.INFO,
            tabulate(rows, headers="keys", tablefmt="grid"),
        )

    # ------------------------------------------------------------------
    # Prompt helpers
    # ------------------------------------------------------------------

    def _prompt_platform(self) -> str | None:
        platforms = SETTINGS.retrieve_all_modules()
        if not platforms:
            self.interactor.writer(MessageType.ERROR, "No platforms configured.")
            return None

        lines = "\n".join(f"  [{i + 1}] {p}" for i, p in enumerate(platforms))
        self.interactor.writer(MessageType.INFO, f"Available platforms:\n{lines}")
        raw = self.interactor.reader(prompt="Select platform (number)").strip()
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(platforms):
                return platforms[idx]
        except ValueError:
            pass
        self.interactor.writer(MessageType.ERROR, "Invalid selection.")
        return None

    def _prompt_categories(self, platform: str) -> List[Category] | None:
        """
        Log in with a no-op reader, fetch categories, and let the user pick
        via index-based paged selection (PAGE_SIZE per page; enter 99 for next page).
        Multiple selection: space-separated numbers. Single selection: one number.
        Press blank to confirm.
        """
        from automation import get_automator_by_name

        self.interactor.writer(
            MessageType.INFO, f"Connecting to {platform} to fetch categories..."
        )
        try:
            automator = get_automator_by_name(platform)()
            automator.start()
            automator.login(reader=lambda _: "")
            all_categories, selection_type = automator.get_categories()
        except Exception as e:
            self.interactor.writer(MessageType.ERROR, f"Could not fetch categories: {e}")
            return None

        if not all_categories:
            self.interactor.writer(MessageType.ERROR, "No categories returned by platform.")
            return None

        selected: List[Category] = []
        page = 0
        total_pages = (len(all_categories) + PAGE_SIZE - 1) // PAGE_SIZE
        is_multiple = selection_type.value == "multiple"

        while True:
            start = page * PAGE_SIZE
            slice_ = all_categories[start: start + PAGE_SIZE]

            lines = [f"  [{start + i + 1}] {c.name}" for i, c in enumerate(slice_)]
            if page + 1 < total_pages:
                lines.append(f"  [{NEXT_PAGE_SENTINEL}] Next page →")

            header = f"Categories (page {page + 1}/{total_pages})"
            if is_multiple:
                header += " — enter numbers separated by spaces"
            if selected:
                header += f"\n  Selected so far: {[c.name for c in selected]}"
            self.interactor.writer(
                MessageType.INFO, header + "\n" + "\n".join(lines)
            )

            prompt = (
                "Enter number(s) (99 = next page, 0 = confirm selection)"
                if is_multiple
                else "Enter number (99 = next page, 0 = confirm selection)"
            )
            raw = self.interactor.reader(prompt=prompt).strip()

            if raw == "0" and is_multiple:
                if not selected:
                    self.interactor.writer(
                        MessageType.WARNING, "Please select at least one category."
                    )
                    continue
                break

            tokens = raw.split() if is_multiple else [raw]

            if NEXT_PAGE_SENTINEL in tokens:
                if page + 1 < total_pages:
                    page += 1
                else:
                    self.interactor.writer(MessageType.WARNING, "Already on last page.")
                continue

            for token in tokens:
                try:
                    num = int(token)
                    cat = all_categories[num - 1]
                    if cat not in selected:
                        selected.append(cat)
                except (ValueError, IndexError):
                    self.interactor.writer(
                        MessageType.WARNING, f"Invalid selection: {token}"
                    )

            if not is_multiple and selected:
                break

        return selected if selected else all_categories

    def _prompt_bio(self) -> Bio | str | None:
        saved_bios = BioService.get_bios()

        if saved_bios:
            lines = "\n".join(f"  [{i + 1}] {b.name}" for i, b in enumerate(saved_bios))
            self.interactor.writer(
                MessageType.INFO,
                f"Saved bios:\n{lines}\n Select a number or type bio manually\n  [0] Skip bio",
            )
            raw = self.interactor.reader(
                prompt="Select bio (number, Type Bio Manually, 0 to skip)"
            ).strip()

            if raw == "0":
                return None
            if not raw.isnumeric():
                return raw or None
            try:
                idx = int(raw) - 1
                if 0 <= idx < len(saved_bios):
                    return saved_bios[idx]
            except ValueError:
                pass
            self.interactor.writer(MessageType.WARNING, "Invalid selection, skipping bio.")
            return None

        self.interactor.writer(
            MessageType.INFO,
            "No saved bios found. Type a short bio or leave blank to skip.",
        )
        text = self.interactor.reader(prompt="Enter your bio (or blank to skip)").strip()
        return text or None

    def _prompt_resume(self) -> Resume | None:
        resumes = ResumeService.get_resumes()
        if not resumes:
            self.interactor.writer(
                MessageType.ERROR,
                "No resumes found. Please add at least one resume before starting a job hunt.",
            )
            return None

        lines = "\n".join(f"  [{i + 1}] {r.name}" for i, r in enumerate(resumes))
        self.interactor.writer(MessageType.INFO, f"Available resumes:\n{lines}")
        raw = self.interactor.reader(prompt="Select resume (number)").strip()
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(resumes):
                return resumes[idx]
        except ValueError:
            pass
        self.interactor.writer(MessageType.ERROR, "Invalid resume selection.")
        return None

    def _prompt_location(self) -> str:
        self.interactor.writer(
            MessageType.INFO,
            "Enter the preferred job location (e.g. 'Remote', 'New York, NY').",
        )
        return self.interactor.reader(prompt="Location").strip()

    def _prompt_salary_range(self):
        from utils.types import SalaryRange

        self.interactor.writer(
            MessageType.INFO,
            "Enter salary range (leave minimum blank to skip).",
        )
        min_raw = self.interactor.reader(prompt="Minimum salary (or blank to skip)").strip()
        if not min_raw:
            return None
        max_raw = self.interactor.reader(prompt="Maximum salary (or blank for same as min)").strip()
        try:
            min_val = int(min_raw)
            max_val = int(max_raw) if max_raw else min_val
            return SalaryRange(min=min_val, max=max_val)
        except ValueError:
            self.interactor.writer(
                MessageType.WARNING, "Invalid salary values, skipping salary range."
            )
            return None

    def _prompt_work_style(self) -> WorkStyle | None:
        styles = list(WorkStyle)
        lines = "\n".join(f"  [{i + 1}] {s.value}" for i, s in enumerate(styles))
        self.interactor.writer(
            MessageType.INFO, f"Work style options:\n{lines}\n  [0] Skip"
        )
        raw = self.interactor.reader(
            prompt="Select work style (number or 0 to skip)"
        ).strip()
        if raw == "0":
            return None
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(styles):
                return styles[idx]
        except ValueError:
            pass
        self.interactor.writer(
            MessageType.WARNING, "Invalid selection, skipping work style."
        )
        return None

    def _prompt_job_count(self) -> int:
        self.interactor.writer(
            MessageType.INFO, "How many jobs do you want to apply for?"
        )
        while True:
            raw = self.interactor.reader(prompt="Job count").strip()
            try:
                count = int(raw)
                if count > 0:
                    return count
            except ValueError:
                pass
            self.interactor.writer(
                MessageType.WARNING, "Please enter a positive whole number."
            )

    def _prompt_extra_instruction(self) -> str:
        self.interactor.writer(
            MessageType.INFO,
            "Any extra instruction for job selection? Max 100 characters. Leave 0 to skip.",
        )
        raw = self.interactor.reader(prompt="Extra instruction (or 0 to skip)").strip()
        if not raw or raw == "0":
            return ""
        if len(raw) > 100:
            self.interactor.writer(
                MessageType.WARNING, "Instruction truncated to 100 characters."
            )
            return raw[:100]
        return raw

    # ------------------------------------------------------------------
    # Background runner
    # ------------------------------------------------------------------

    def _run_graph(self, context: AutomationRequestContext):
        try:
            graph = AutomatorGraph(configuration=context)
            graph.run_graph()
            logger.info("[job_hunt] Automation graph completed successfully.")
        except Exception as e:
            logger.error(f"[job_hunt] Automation graph error: {e}")
