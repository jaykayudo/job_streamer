import json
import os
import re
from typing import Dict, List

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import END, START, StateGraph
from langchain.chat_models import init_chat_model
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

from agent.tools import get_all_tools_initialized
from agent.types import AgentState
from automation import get_automator_by_name
from automation.core.automator.base import BaseAutomator
from automation.core.automator.types import (
    Category,
    JobApplicationDetails,
    JobApplicationDetailsAnswer,
    JobDetails,
    JobFilter,
)
from conf.settings import SETTINGS
from data_handler.langauge_model.prompt_generator import PromptGenerator
from services.database.application import ApplicationService
from utils.context import AutomationRequestContext, build_initial_state
from utils.file_helper import save_json_to_files_dir
from utils.logging import JobStreamerLogger


logger = JobStreamerLogger().get_logger()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_json_list(text: str) -> list[str]:
    """
    Extract a JSON list of IDs from an LLM response string.
    Returns an empty list if parsing fails.
    """
    match = re.search(r"\[.*?\]", text, re.DOTALL)
    if not match:
        return []
    try:
        result = json.loads(match.group())
        return [str(item) for item in result if item is not None]
    except json.JSONDecodeError:
        logger.warning(f"Could not parse JSON list from LLM response: {text[:200]}")
        return []


def _parse_answer_list(text: str) -> list[dict]:
    """
    Extract a JSON list of {id, answer} dicts from an LLM response string.
    Returns an empty list if parsing fails.
    """
    match = re.search(r"\[.*?\]", text, re.DOTALL)
    if not match:
        return []
    try:
        result = json.loads(match.group())
        return [item for item in result if isinstance(item, dict) and "id" in item]
    except json.JSONDecodeError:
        logger.warning(f"Could not parse answer list from LLM response: {text[:200]}")
        return []


# ---------------------------------------------------------------------------
# Graph
# ---------------------------------------------------------------------------

class AutomatorGraph:
    """
    LangGraph-based agent that orchestrates job automation across platforms.
    """

    def __init__(self, configuration: AutomationRequestContext):
        # Our Embedding model - converts our text to vector embedding
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001",
            api_key=SETTINGS.GOOGLE_API_KEY
        )
        self.config = configuration
        # self.embeddings = OllamaEmbeddings(model=SETTINGS.LLM_EMBEDDING_MODEL)
        self.automator: BaseAutomator = get_automator_by_name(configuration.platform)()
        self.retriever = self._load_retriever()
        base_model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            api_key=SETTINGS.GOOGLE_API_KEY
        )
        # base_model = OllamaLLM(model=SETTINGS.LLM_MODEL_NAME)
        self.tools = get_all_tools_initialized(self.retriever)
        self.model = base_model

        self.graph = StateGraph(AgentState)
        self._graph_layout()
        self.app = self.graph.compile()
        self._display_graph_layout()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _has_jobs(self, state: AgentState) -> str:
        """
        Shared conditional router: continue if job_details is non-empty, else end.
        Used after both jobs_retrieval_node and job_filtering_node.
        """
        if state.get("job_details"):
            return "continue"
        logger.warning("[_has_jobs] No jobs in state — ending graph early.")
        return "end"

    def _graph_layout(self):
        """Wire up all nodes and edges."""
        self.graph.add_node("start_node",                   self.start_node)
        self.graph.add_node("job_category_filtering_node",  self.job_category_filtering_node)
        self.graph.add_node("jobs_retrieval_node",          self.jobs_retrieval_node)
        self.graph.add_node("job_filtering_node",           self.job_filtering_node)
        self.graph.add_node("job_questions_retrieval_node",  self.job_questions_retrieval_node)
        self.graph.add_node("job_questions_answering_node",   self.job_questions_answering_node)
        self.graph.add_node("jobs_application_submission_node", self.jobs_application_submission_node)
        self.graph.add_node("finalization_node",              self.finalization_node)

        self.graph.add_edge(START,                              "start_node")
        self.graph.add_edge("start_node",                       "job_category_filtering_node")
        self.graph.add_edge("job_category_filtering_node",      "jobs_retrieval_node")
        self.graph.add_conditional_edges(
            "jobs_retrieval_node",
            self._has_jobs,
            {"continue": "job_filtering_node", "end": END},
        )
        self.graph.add_conditional_edges(
            "job_filtering_node",
            self._has_jobs,
            {"continue": "job_questions_retrieval_node", "end": END},
        )
        self.graph.add_edge("job_questions_retrieval_node",     "job_questions_answering_node")
        self.graph.add_edge("job_questions_answering_node",     "jobs_application_submission_node")
        self.graph.add_edge("jobs_application_submission_node", "finalization_node")
        self.graph.add_edge("finalization_node",                END)

    def _display_graph_layout(self):
        """Optional: render a PNG of the compiled graph for debugging."""
        pass

    def _load_retriever(self):
        """Build a Chroma vector store from the resume PDF and return a retriever."""
        resume_path = self.config.resume.path

        if not os.path.exists(resume_path):
            raise FileNotFoundError(f"Resume not found: {resume_path}")

        pages = PyPDFLoader(resume_path).load()
        logger.info(f"Loaded {len(pages)} pages from resume PDF.")

        chunks = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        ).split_documents(pages)

        persist_dir = f"{SETTINGS.CHROMA_DB_URL}/{SETTINGS.LLM_MODEL}"
        os.makedirs(persist_dir, exist_ok=True)

        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=persist_dir,
            collection_name="resumes",
        )
        logger.info("Chroma vector store ready.")
        return vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5},
        )

    def _retrieve_resume_context(self) -> str:
        """
        Run a fixed set of queries against the resume vector store and return
        de-duplicated chunks as a single string.  Used to supply concise,
        relevant resume context to the LLM instead of embedding the full PDF.
        """
        queries = [
            "technical skills and programming languages",
            "work experience and job titles",
            "education and certifications",
            "projects and key achievements",
        ]
        seen: set[str] = set()
        chunks: list[str] = []
        for query in queries:
            for doc in self.retriever.invoke(query):
                if doc.page_content not in seen:
                    seen.add(doc.page_content)
                    chunks.append(doc.page_content)
        return "\n\n---\n\n".join(chunks)

    # ------------------------------------------------------------------
    # Node functions
    # ------------------------------------------------------------------

    def start_node(self, state: AgentState) -> dict:
        """
        Launch the automator, log in, and fetch all available job categories
        from the platform.  The categories list is written to state for the
        next node to filter.
        """
        logger.info(f"[start_node] Starting automator for platform: {self.config.platform}")
        self.automator.start()
        # Credentials are read from environment variables inside the automator.
        # A no-op reader is passed; interactive login is not needed in agent mode.
        self.automator.login(reader=lambda _: "")

        categories, selection_type = self.automator.get_categories()
        logger.info(
            f"[start_node] Fetched {len(categories)} categories "
            f"(selection_type={selection_type})"
        )
        
        # Remove after debugging
        print(f"Categories retrieved: {[c.name for c in categories]}")

        return {
            "categories": categories,
            "messages": [
                SystemMessage(
                    content=(
                        f"Platform started. Retrieved {len(categories)} job categories: "
                        f"{[c.name for c in categories]}"
                    )
                )
            ],
        }

    def job_category_filtering_node(self, state: AgentState) -> dict:
        """
        Use the LLM to select the most relevant job categories for this user.

        Flow:
          1. Pre-retrieve resume context from the vector store (avoids embedding
             the full PDF in the prompt).
          2. Build the category-selection prompt via PromptGenerator.
          3. Invoke the LLM — response is expected to be a JSON list of IDs.
          4. Parse the IDs, filter the available categories, and update state.
        """
        all_categories: List[Category] = state["categories"]
        logger.info(f"[job_category_filtering_node] Filtering {len(all_categories)} categories.")

        # 1. Retrieve focused resume excerpts instead of embedding the full PDF.
        resume_context = self._retrieve_resume_context()

        # 2. Build prompt.
        prompt = PromptGenerator.generate_prompt_for_choosing_job_category(
            all_categories,
            self.config,
            resume_context=resume_context,
        )

        messages = [
            SystemMessage(content=prompt["system"]),
            HumanMessage(content=prompt["user"]),
        ]

        # 3. Invoke LLM.
        logger.info(f"[job_category_filtering_node] Invoking LLM for category filtering...")
        result = self.model.invoke(messages)
        raw_text: str = result if isinstance(result, str) else result.content
        logger.debug(f"[job_category_filtering_node] LLM raw response: {raw_text[:300]}")

        # 4. Parse IDs and filter categories.
        selected_ids = _parse_json_list(raw_text)
        id_set = set(selected_ids)
        filtered = [c for c in all_categories if c.id in id_set]

        if not filtered:
            logger.warning(
                "[job_category_filtering_node] LLM returned no matching category IDs. "
            )
            return {}

        logger.info(
            f"[job_category_filtering_node] {len(all_categories)} → {len(filtered)} categories: "
            f"{[c.name for c in filtered]}"
        )
        
        
        logger.debug(f"[job_category_filtering_node] Selected category IDs: {selected_ids}")

        return {
            "categories": filtered,
            "messages": [
                SystemMessage(
                    content=(
                        f"Job category filtering complete. "
                        f"Selected {len(filtered)} categories: {[c.name for c in filtered]}"
                    )
                )
            ],
        }
        

    def jobs_retrieval_node(self, state: AgentState) -> dict:
        """
        Retrieve job listings for the selected categories.
        Flow:
        1. Get the category from the state which was selected by the LLM in the previous node.
        2. Use the automator to retrieve jobs for each category, and aggregate them in
        3. Save the retrieved jobs to the state to be filtered in the next node.
        """
        categories = state["categories"]
        job_count = state["job_count"]
        logger.info(f"[jobs_retrieval_node] Retrieving jobs for {len(categories)} categories.")

        seen_ids: set[str] = set()
        all_jobs = []

        
        filter = JobFilter(categories=categories)
        jobs = self.automator.get_jobs(count=job_count, filter=filter)
        for job in jobs:
            if job.id not in seen_ids:
                seen_ids.add(job.id)
                all_jobs.append(job)

        logger.info(f"[jobs_retrieval_node] Retrieved {len(all_jobs)} unique jobs across all categories.")

        logger.info("[jobs_retrieval_node] Fetching job details for each listing...")
        job_details: List[JobDetails] = []
        for job in all_jobs:
            try:
                details = self.automator.get_job_details(job)
                job_details.append(details)
            except Exception as e:
                logger.warning(f"[jobs_retrieval_node] Could not fetch details for job {job.id}: {e}")

        logger.info(f"[jobs_retrieval_node] Fetched details for {len(job_details)} jobs.")

        return {
            "job_details": job_details,
            "messages": [
                SystemMessage(
                    content=(
                        f"Jobs retrieved. {len(job_details)} job listings fetched across "
                        f"{len(categories)} categories."
                    )
                )
            ],
        }

    def job_filtering_node(self, state: AgentState) -> dict:
        """
        Use the LLM to further filter retrieved jobs to best fit the user's preferences,
        request, and skillset.
        Flow:
        1. The resume context is retrieved from the vector store.
        2. The prompt is built via PromptGenerator, incorporating user preferences and resume context.
        3. Extra context gotten from the user is passed to the prompt
        4. The job count is passed to ensure the LLM only selects a certain number of jobs.
        5. Criterias like location and skillset will be considered when filtering the jobs.
        For example, if the user prefers remote jobs and has strong Python skills, the LLM will prioritize jobs that are remote and require Python.
        6. Jobs are selected and filtered based on which offers the best benefits and compensation package, and which ones the user is most qualified for based on their resume.
        7. The LLM response is expected to be a JSON list of job IDs.

        """
        all_job_details: List[JobDetails] = state["job_details"]
        job_count: int = state["job_count"]
        logger.info(f"[job_filtering_node] Filtering {len(all_job_details)} jobs (target: {job_count}).")

        if not all_job_details:
            logger.warning("[job_filtering_node] No jobs to filter, skipping.")
            return {}

        # 1. Retrieve focused resume excerpts.
        resume_context = self._retrieve_resume_context()

        # 2. Build prompt with full context (resume, bio, work style, extra instruction).
        prompt = PromptGenerator.generate_prompt_for_job_filtering(
            all_job_details,
            self.config,
            resume_context=resume_context,
        )

        # 3. Append job count constraint to user prompt.
        user_prompt = prompt["user"]
        messages = [
            SystemMessage(content=prompt["system"]),
            HumanMessage(content=user_prompt),
        ]

        # 4. Invoke LLM.
        logger.info("[job_filtering_node] Invoking LLM for job filtering...")
        result = self.model.invoke(messages)
        raw_text: str = result if isinstance(result, str) else result.content
        logger.debug(f"[job_filtering_node] LLM raw response: {raw_text[:300]}")

        # 5. Parse IDs, filter job_details, and cap at job_count.
        selected_ids = _parse_json_list(raw_text)
        id_set = set(selected_ids)
        filtered = [j for j in all_job_details if j.job.id in id_set]

        if not filtered:
            logger.warning(
                "[job_filtering_node] LLM returned no matching job IDs. "
                "Ending Job Filtering."
            )
            return {}

        filtered = filtered[:job_count]

        logger.info(
            f"[job_filtering_node] {len(all_job_details)} → {len(filtered)} jobs: "
            f"{[j.job.title for j in filtered]}"
        )

        return {
            "job_details": filtered,
            "messages": [
                SystemMessage(
                    content=(
                        f"Job filtering complete. "
                        f"Selected {len(filtered)} jobs: {[j.job.title for j in filtered]}"
                    )
                )
            ],
        }
    

    def job_questions_retrieval_node(self, state: AgentState) -> dict:
        """
        Fetch application-form questions for each job.
        Flow:
        1. For each job in state, use the automator to retrieve the application questions.
        2. Store the questions in state, keyed by job URL for easy retrieval in the next node.
        """
        job_details: List[JobDetails] = state["job_details"]
        logger.info(f"[job_questions_retrieval_node] Fetching questions for {len(job_details)} jobs.")

        job_application_details: dict[str, list[JobApplicationDetails]] = {}
        for job in job_details:
            try:
                questions = self.automator.get_job_application_details(job)
                job_application_details[job.job.url] = questions
                logger.info(
                    f"[job_questions_retrieval_node] {job.job.title}: {len(questions)} questions."
                )
            except Exception as e:
                logger.warning(
                    f"[job_questions_retrieval_node] Could not fetch questions for "
                    f"'{job.job.title}': {e}"
                )

        logger.info(
            f"[job_questions_retrieval_node] Questions fetched for "
            f"{len(job_application_details)}/{len(job_details)} jobs."
        )

        return {
            "job_application_details": job_application_details,
            "messages": [
                SystemMessage(
                    content=(
                        f"Application questions retrieved for {len(job_application_details)} jobs."
                    )
                )
            ],
        }

    def job_questions_answering_node(self, state: AgentState) -> dict:
        """
        Use the LLM to answer application questions for each job based on the user's resume, bio, and preferences.
        Flow:
        1. For each job, retrieve the application questions via the automator.
        2. Build a prompt for each application question using PromptGenerator, incorporating resume context and any relevant user preferences.
        3. Invoke the LLM to generate answers for each question.
        4. Store the answers in state to be used in the application submission node.
        """
        job_details: List[JobDetails] = state["job_details"]
        job_application_details: dict = state.get("job_application_details") or {}
        logger.info(f"[job_questions_answering_node] Generating answers for {len(job_details)} jobs.")

        # Retrieve resume context once and reuse across all jobs.
        resume_context = self._retrieve_resume_context()

        job_application_answers: dict[str, list[JobApplicationDetailsAnswer]] = {}
        messages = []
        for idx, job in enumerate(job_details):
            questions = job_application_details.get(job.job.url)
            if not questions:
                logger.warning(
                    f"[job_questions_answering_node] No questions for '{job.job.title}', skipping."
                )
                continue

            # Build per-job prompt with job context + resume excerpts.
            prompt = PromptGenerator.generate_prompt_for_answering_job_application_details(
                questions,
                self.config,
                job_details=job,
                resume_context=resume_context,
            )
            if idx == 0:
                messages.append(SystemMessage(content=prompt["system"]))
            messages.append(HumanMessage(content=prompt["user"]))
        

            logger.info(
                f"[job_questions_answering_node] Invoking LLM for '{job.job.title}'..."
            )
            result = self.model.invoke(messages)
            raw_text: str = result if isinstance(result, str) else result.content
            logger.debug(
                f"[job_questions_answering_node] LLM raw response for "
                f"'{job.job.title}': {raw_text[:300]}"
            )
            messages.append(AIMessage(content=raw_text))

            # Parse answers and map back to JobApplicationDetailsAnswer objects.
            parsed = _parse_answer_list(raw_text)
            answer_map = {item["id"]: item.get("answer", "") for item in parsed}

            answers: list[JobApplicationDetailsAnswer] = []
            for question in questions:
                answers.append(
                    JobApplicationDetailsAnswer(
                        id=question.id,
                        unique_selector=question.unique_selector,
                        selector_type=question.selector_type,
                        application_details=question,
                        value=answer_map.get(question.id, ""),
                    )
                )

            job_application_answers[job.job.url] = answers
            logger.info(
                f"[job_questions_answering_node] Generated {len(answers)} answers "
                f"for '{job.job.title}'."
            )

        return {
            "job_application_answers": job_application_answers,
            "messages": [
                SystemMessage(
                    content=(
                        f"Application answers generated for "
                        f"{len(job_application_answers)} jobs."
                    )
                )
            ],
        }

    def jobs_application_submission_node(self, state: AgentState) -> dict:
        """
        Submit job applications via the automator using the LLM-generated answers.
        Flow:
        1. For each job, retrieve the pre-generated answers from job_application_answers.
        2. Call automator.apply_job(job, answers) to submit the application.
        3. On success:
           a. Serialise job details, application questions, and answers to a JSON file
              in SETTINGS.FILES_DIR using save_json_to_files_dir.
           b. Persist the application record to the database via ApplicationService,
              storing the saved file path in application_detail_file_path.
        4. Track URLs of successfully applied jobs and write them to state.
        """
        job_details: List[JobDetails] = state["job_details"]
        job_application_details: Dict[str, list] = state.get("job_application_details") or {}
        job_application_answers: Dict[str, List[JobApplicationDetailsAnswer]] = state.get("job_application_answers") or {}
        logger.info(
            f"[jobs_application_submission_node] Submitting applications for "
            f"{len(job_details)} jobs."
        )

        applied_jobs: list[str] = []

        for job in job_details:
            answers = job_application_answers.get(job.job.url)
            if not answers:
                logger.warning(
                    f"[jobs_application_submission_node] No answers for "
                    f"'{job.job.title}', skipping submission."
                )
                continue

            try:
                success = self.automator.apply_job(job, answers)
            except Exception as e:
                logger.error(
                    f"[jobs_application_submission_node] Error applying to "
                    f"'{job.job.title}': {e}"
                )
                continue

            if not success:
                logger.warning(
                    f"[jobs_application_submission_node] Automator returned False "
                    f"for '{job.job.title}'."
                )
                continue

            applied_jobs.append(job.job.url)
            logger.info(
                f"[jobs_application_submission_node] Successfully applied to "
                f"'{job.job.title}'."
            )

            # Serialise full application record to a JSON file.
            questions = job_application_details.get(job.job.url, [])
            file_data = {
                "job": job.model_dump(),
                "questions": [q.model_dump() for q in questions],
                "answers": [a.model_dump() for a in answers],
            }
            safe_id = re.sub(r"[^\w\-]", "_", job.job.id or job.job.title)
            filename = f"{safe_id}_{self.config.platform}_application.json"
            try:
                file_path = save_json_to_files_dir(filename, file_data)
                logger.info(
                    f"[jobs_application_submission_node] Saved application file: {file_path}"
                )
            except Exception as e:
                logger.error(
                    f"[jobs_application_submission_node] Could not save file for "
                    f"'{job.job.title}': {e}"
                )
                file_path = filename  # fall back to relative name

            # Persist to database.
            try:
                ApplicationService.create_application(
                    platform=self.config.platform,
                    job_title=job.job.title,
                    job_description=job.description,
                    job_url=job.job.url,
                    job_location=job.job.location or "",
                    application_detail_file_path=file_path,
                    job_salary=job.pay_range,
                    job_company=job.company,
                )
                logger.info(
                    f"[jobs_application_submission_node] Persisted DB record for "
                    f"'{job.job.title}'."
                )
            except Exception as e:
                logger.error(
                    f"[jobs_application_submission_node] DB persist failed for "
                    f"'{job.job.title}': {e}"
                )

        logger.info(
            f"[jobs_application_submission_node] Applied to "
            f"{len(applied_jobs)}/{len(job_details)} jobs."
        )

        return {
            "applied_jobs": applied_jobs,
            "messages": [
                SystemMessage(
                    content=(
                        f"Application submission complete. "
                        f"Applied to {len(applied_jobs)} jobs."
                    )
                )
            ],
        }

    def finalization_node(self, state: AgentState) -> dict:
        """
        Log a run summary and clean up the browser session.
        Database persistence has already been handled per-job in
        jobs_application_submission_node.
        """
        applied_jobs: list[str] = state.get("applied_jobs") or []
        logger.info(
            f"[finalization_node] Run complete. "
            f"{len(applied_jobs)} job(s) applied and persisted."
        )

        try:
            self.automator.logout()
        except Exception as e:
            logger.warning(f"[finalization_node] Automator logout error: {e}")

        return {
            "messages": [
                SystemMessage(
                    content=(
                        f"Finalization complete. "
                        f"Persisted {len(applied_jobs)} application(s) to database."
                    )
                )
            ],
        }
    
    #-------------------------------------------------------------------
    # Run Function
    #-------------------------------------------------------------------
    def run_graph(self):
        initial_state = build_initial_state(self.config)
        final_state = self.app.invoke(initial_state)
        return final_state