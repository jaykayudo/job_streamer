from langchain_core.tools import tool
from langchain_core.vectorstores import VectorStoreRetriever


def make_resume_retriever_tool(retriever: VectorStoreRetriever):
    """
    Return a LangChain tool that retrieves relevant chunks from the user's resume.

    Using a closure keeps the retriever out of the function signature so the
    LLM only sees the `query` parameter.
    """

    @tool
    def retrieve_resume_info(query: str) -> str:
        """
        Retrieve relevant sections from the user's resume that match the query.
        Use this tool to look up skills, job titles, experience, education,
        or any other detail about the candidate before making decisions.

        Args:
            query: A natural-language question or topic about the candidate's
                   background (e.g. "programming languages", "years of experience").

        Returns:
            Relevant resume text chunks that answer the query.
        """
        docs = retriever.invoke(query)
        if not docs:
            return "No relevant information found in the resume."
        return "\n\n---\n\n".join(doc.page_content for doc in docs)

    return retrieve_resume_info