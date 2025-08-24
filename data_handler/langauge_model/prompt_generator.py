from typing import List
from automation.core.automator.types import Category, JobApplicationDetails, JobDetails
from utils.context import AutomationRequestContext
from data_handler.extraction.resume_data_parser import ResumeDataParser
from storage.core.models import Bio, Resume


class PromptGenerator:
    """
    Generate prompts for the language model.
    """

    @classmethod
    def _get_resume_data(cls, resume: Resume) -> str:
        """
        Get the resume data from the resume file.
        """
        file_path = resume.path
        parsed_resume = ResumeDataParser(file_path)
        return parsed_resume.get_extracted_data()

    @classmethod
    def _convert_questions_to_prompt_format(
        cls, job_application_details: List[JobApplicationDetails]
    ) -> str:
        """
        Convert the job application details to a prompt format.
        """
        questions_jsonified = list(
            map(lambda x: x.model_dump(), job_application_details)
        )
        return_questions = []
        for question in questions_jsonified:
            return_questions.append(
                {
                    "id": question["id"],
                    "question": question["title"],
                    "is_required": question["is_required"],
                    "options": question["options"],
                }
            )
        return return_questions

    @classmethod
    def _get_bio_data(cls, bio: Bio | str | None) -> str:
        """
        Get the bio data from the bio file.
        """
        if isinstance(bio, Bio):
            return bio.bio
        return bio

    @classmethod
    def generate_prompt_for_job_filtering(
        cls,
        job_details: List[JobDetails],
        automation_request_context: AutomationRequestContext,
    ) -> dict:
        """
        Generate prompts for the job filtering.
        """
        job_details_jsonified = list(map(lambda x: x.model_dump(), job_details))
        context_jsonified = automation_request_context.model_dump()
        resume_data = cls._get_resume_data(automation_request_context.resume)
        bio = cls._get_bio_data(automation_request_context.bio)
        work_style = context_jsonified["work_style"]

        prompt = f"""
            This is a prompt to filter jobs based on the user data.
            Here are the jobs in json format:
            {job_details_jsonified}
            
            Here is the resume data of the user 
            (it may contain inconsistencies so smartly analyze it):
            RESUME
            ```
            {resume_data}
            ```
            Here is the users bio to help you understand the user's skill:
            {bio}
        """
        if automation_request_context.extra_job_selection_intruction:
            prompt += f"""

                Here is the extra instruction for job selection from the user:
                {automation_request_context.extra_job_selection_intruction}
            """
        if isinstance(context_jsonified["bio"], dict):
            if "work_experiences" in context_jsonified["bio"]:
                if len(context_jsonified["bio"]["work_experiences"]) > 0:
                    prompt += f"""
                    
                        Here is the work experiences of the user in json format:
                        {context_jsonified["bio"]["work_experiences"]}
                    """
                if "projects" in context_jsonified["bio"]:
                    if len(context_jsonified["bio"]["projects"]) > 0:
                        prompt += f"""

                            Here is the projects of the user in json format:
                            {context_jsonified["bio"]["projects"]}
                            
                        """
        if work_style:
            prompt += f"""
            
                Here is the preferred work style of the user:
                {work_style}
            """
        system_prompt = """
            You are a job filter expert.
            You need to filter the jobs based on the resume, the bio and the extra provided information.
            Score each job within the range of 0 to 10 based on how well it matches the user's resume, bio and extra provided information.
            Only return the jobs that have a score of 7 or more.
            if no job has a score of 7 or more, return an empty list.
            You need to return the jobs that are most likely to be a good fit for the user.
            You need to return the jobs in json format as a list of the job ids.
            You need to return in the format of [job_id1, job_id2, job_id3, ...]
            Return only the job ids as a json list. Do not return any other text.
        """
        return {"system": system_prompt, "user": prompt}

    @classmethod
    def generate_prompt_for_choosing_job_category(
        cls,
        job_categories: List[Category],
        automation_request_context: AutomationRequestContext,
    ) -> dict:
        """
        Generate prompts for the job category selection.
        """
        categories = list(map(lambda x: x.model_dump(), job_categories))
        resume_data = cls._get_resume_data(automation_request_context.resume)
        bio = cls._get_bio_data(automation_request_context.bio)

        prompt = f"""
            This is a prompt to choose the job category for the user based on the user's data.
            Here are the categories in json format:
            {categories}
            
            Here is the resume data of the user 
            (it may contain inconsistencies so smartly analyze it):
            RESUME
            ```
            {resume_data}
            ```
            Here is the users bio to help you understand the user's skill:
            ```
            {bio}
            ```
            
        """
        system_prompt = f"""
            You are a job category expert.
            Based on the provided information, return the most suitable job categories for the user.
            You need to return the job categories as a json list of ids.
            You need to return in the format of [id1, id2, id3, ...]
            Return only the job category ids as a json list. Do not return any other text.
        """

        return {"system": system_prompt, "user": prompt}

    @classmethod
    def generate_prompt_for_answering_job_application_details(
        cls,
        job_application_details: List[JobApplicationDetails],
        automation_request_context: AutomationRequestContext,
    ) -> dict:
        """
        Generate prompts for the job application details.
        """
        details_jsonified = cls._convert_questions_to_prompt_format(
            job_application_details
        )
        context_jsonified = automation_request_context.model_dump()
        resume_data = cls._get_resume_data(automation_request_context.resume)
        bio = cls._get_bio_data(automation_request_context.bio)
        work_style = context_jsonified["work_style"]
        prompt = f"""
            This is a prompt to answer the job application questions for the user based on the user's data.
            The questions are in the following format:
            ```
            [
                {{
                    "id": "question_id",
                    "question": "question_text",
                    "is_required": true/false,
                    "options": ["option1", "option2", "option3", ...] / none
                }},
                ...
            ]
            ```
            Here are the job application questions in json format:
            
            {details_jsonified}
            
            Here is the resume data of the user 
            (it may contain inconsistencies so smartly analyze it):
            RESUME
            ```
            {resume_data}
            ```
            Here is the users bio to help you understand the user's skill:
            ```
            {bio}
            ```
        """
        if isinstance(context_jsonified["bio"], dict):
            if "work_experiences" in context_jsonified["bio"]:
                if len(context_jsonified["bio"]["work_experiences"]) > 0:
                    prompt += f"""
                    
                        Here is the work experiences of the user in json format:
                        ```
                        {context_jsonified["bio"]["work_experiences"]}
                        ```
                    """
                if "projects" in context_jsonified["bio"]:
                    if len(context_jsonified["bio"]["projects"]) > 0:
                        prompt += f"""

                            Here is the projects of the user in json format:
                            ```
                            {context_jsonified["bio"]["projects"]}
                            ```
                        """
        if work_style:
            prompt += f"""
            
                Here is the preferred work style of the user:
                {work_style}
            """
        system_prompt = f"""
            You are a job application expert.
            You need to answer the job application questions based on the user's data.
            Return the answers in the following format:
            ```
            [
                {{
                    "id": "question_id",
                    "answer": "answer_text",
                }},
                ...
            ]
            ```
            If the question is not required, you can return an empty string for the answer.
            If the question has options, smartly analyze the user's data and return the most suitable option.
            If the question has no options, you need to generate the answer based on the user's data.
            If the question is required, you need to return the answer.
            Return only the answers as a json list. Do not return any other text.
        """
        return {"system": system_prompt, "user": prompt}
