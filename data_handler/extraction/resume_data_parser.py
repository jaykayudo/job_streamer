import spacy


class ResumeDataParser:
    """
    Parse the resume data and return the data in a structured format.
    """

    def __init__(self, resume_path: str):
        """
        Initialize the resume data parser.
        """
        self.nlp = spacy.load("en_core_web_sm")
        self.resume_path = resume_path
        
    def _load_resume(self) -> str:
        """
        Load the resume from the path.
        """
        pass

    def extract_data(self) -> dict:
        """
        Extract the data from the resume.
        """
        pass