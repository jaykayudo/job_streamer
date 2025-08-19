from conf.settings import SETTINGS
import os
import pdfplumber
import re


class ResumeDataParser:
    """
    Parse the resume data and return the data in a structured format.
    """

    def __init__(self, resume_path: str):
        """
        Initialize the resume data parser.
        """
        self.resume_path = os.path.join(SETTINGS.RESUMES_DIR, resume_path)
        self.resume_data = self._load_resume()
        self.resume_data, self.personal_data = self._strip_personal_data(
            self.resume_data
        )

    def _strip_personal_data(self, text: str) -> tuple[str, dict]:
        """
        Strip the personal data from the text.
        """
        email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        phone_regex = r"\+?\d{7,12}"
        github_regex = r"(https?://)?(www\.)?github\.com/[a-zA-Z0-9_-]+"
        # should suport https://www.example.com.site

        website_regex = (
            r"(https?://)?(www\.)?[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+(\.[a-zA-Z]+)?"
        )

        email = re.search(email_regex, text)
        phone = re.search(phone_regex, text)
        github = re.search(github_regex, text)
        personal_website = re.search(website_regex, text)

        # get the personal data first of all
        personal_data = {
            "email": email.group() if email else None,
            "phone": phone.group() if phone else None,
            "github": github.group() if github else None,
            "personal_website": personal_website.group() if personal_website else None,
        }

        # remove the personal data from the text
        text = re.sub(email_regex, "", text)
        text = re.sub(phone_regex, "", text)
        text = re.sub(github_regex, "", text)
        text = re.sub(website_regex, "", text)

        return text, personal_data

    def _load_resume(self) -> dict:
        """
        Load the resume from the path.
        """
        extracted_text = ""
        with pdfplumber.open(self.resume_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                extracted_text += text

        return extracted_text

    def _extract_personal_data(self) -> dict:
        """
        Extract the personal data from the parsed resume data.
        """
        personal_data = {
            "name": self.resume_data.pop("name", None),
            "email": self.resume_data.pop("email", None),
            "mobile_number": self.resume_data.pop("mobile_number", None),
            "github": self.resume_data.pop("github", None),
        }
        return personal_data

    def get_extracted_data(self) -> dict:
        """
        Get the data that can be used in a LLM prompt.
        """
        return self.resume_data

    def get_personal_data(self) -> dict:
        """
        Get the personal data from the parsed resume data.
        """
        return self.personal_data
