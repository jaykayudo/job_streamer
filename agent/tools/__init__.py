from .resume_tool import make_resume_retriever_tool
from langchain_core.vectorstores import VectorStoreRetriever
from typing import Optional


def get_all_tools_initialized(
    retriever: Optional[VectorStoreRetriever] = None,
) -> list:
    """
    Return all LangChain tools, initialised with the given retriever.
    More tools (e.g. automator-backed ones) will be added here as they are implemented.
    """
    tools = []
    if retriever is not None:
        tools.append(make_resume_retriever_tool(retriever))
    return tools