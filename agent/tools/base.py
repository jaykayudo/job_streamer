from automation.core.automator.base import BaseAutomator
from langchain_core.tools import tool
from langchain_core.vectorstores import VectorStoreRetriever
from typing import Optional

class BaseTool:
    """
    Base class for LLM tools.
    """

    def __init__(
        self, automator: BaseAutomator,
        retriever: Optional[VectorStoreRetriever] = None
    ):
        self.automator = automator
        self.retriever = retriever
 
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Tool must implement __call__ method")
