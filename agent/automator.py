import json
import os
import re
from typing import List

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import END, START, StateGraph
from langchain.chat_models import init_chat_model

from agent.tools import get_all_tools_initialized
from agent.types import AgentState
from automation import get_automator_by_name
from automation.core.automator.base import BaseAutomator
from automation.core.automator.types import Category
from conf.settings import SETTINGS
from data_handler.langauge_model.prompt_generator import PromptGenerator
from utils.context import AutomationRequestContext, build_initial_state
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


# ---------------------------------------------------------------------------
# Graph
# ---------------------------------------------------------------------------

class AutomatorGraph:
    """
    LangGraph-based agent that orchestrates job automation across platforms.
    """

    def __init__(self, configuration: AutomationRequestContext):
        self.config = configuration
        self.embeddings = OllamaEmbeddings(model=SETTINGS.LLM_EMBEDDING_MODEL)
        self.automator: BaseAutomator = get_automator_by_name(configuration.platform)()
        self.retriever = self._load_retriever()

        base_model = init_chat_model(SETTINGS.LLM_MODEL_NAME, model_provider=SETTINGS.LLM_MODEL)
        self.tools = get_all_tools_initialized(self.retriever)
        self.model = base_model.bind_tools(self.tools)

        self.graph = StateGraph(AgentState)
        self._graph_layout()
        self.app = self.graph.compile()
        self._display_graph_layout()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _graph_layout(self):
        """Wire up all nodes and edges."""
        self.graph.add_node("start_node",                   self.start_node)
        self.graph.add_node("job_filtering_node",           self.job_filtering_node)
        self.graph.add_node("jobs_retrieval_node",          self.jobs_retrieval_node)
        self.graph.add_node("jobs_questions_retrieval_node",self.jobs_questions_retrieval_node)
        self.graph.add_node("jobs_application_node",        self.jobs_application_node)
        self.graph.add_node("finalization_node",            self.finalization_node)

        self.graph.add_edge(START,                              "start_node")
        self.graph.add_edge("start_node",                       "job_filtering_node")
        self.graph.add_edge("job_filtering_node",               "jobs_retrieval_node")
        self.graph.add_edge("jobs_retrieval_node",              "jobs_questions_retrieval_node")
        self.graph.add_edge("jobs_questions_retrieval_node",    "jobs_application_node")
        self.graph.add_edge("jobs_application_node",            "finalization_node")
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

        persist_dir = SETTINGS.CHROMA_DB_URL
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

    def job_filtering_node(self, state: AgentState) -> dict:
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
        logger.info(f"[job_filtering_node] Filtering {len(all_categories)} categories.")

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
        logger.info(f"[job_filtering_node] Invoking LLM for category filtering...")
        result = self.model.invoke(messages)
        raw_text: str = result if isinstance(result, str) else result.content
        # change to debug after viewing the raw response format
        logger.info(f"[job_filtering_node] LLM raw response: {raw_text[:300]}")

        # 4. Parse IDs and filter categories.
        selected_ids = _parse_json_list(raw_text)
        id_set = set(selected_ids)
        filtered = [c for c in all_categories if c.id in id_set]

        if not filtered:
            logger.warning(
                "[job_filtering_node] LLM returned no matching category IDs. "
                "Falling back to all available categories."
            )
            filtered = all_categories

        logger.info(
            f"[job_filtering_node] {len(all_categories)} → {len(filtered)} categories: "
            f"{[c.name for c in filtered]}"
        )
        
        # Remove after debugging
        print(f"Selected category IDs: {selected_ids}")

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

    # ------------------------------------------------------------------
    # Stub nodes (to be implemented)
    # ------------------------------------------------------------------

    def jobs_retrieval_node(self, state: AgentState) -> dict:
        """Retrieve job listings for the selected categories."""
        return {}

    def jobs_questions_retrieval_node(self, state: AgentState) -> dict:
        """Fetch application-form questions for each job."""
        return {}

    def jobs_application_node(self, state: AgentState) -> dict:
        """Fill and submit job applications via the automator."""
        return {}

    def finalization_node(self, state: AgentState) -> dict:
        """Persist results and clean up the browser session."""
        return {}
    
    #-------------------------------------------------------------------
    # Run Function
    #-------------------------------------------------------------------
    def run_graph(self):
        initial_state = build_initial_state(self.config)
        final_state = self.app.invoke(initial_state)
        return final_state