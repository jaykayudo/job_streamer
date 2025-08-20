from typing import List
from automation.core.automator.types import JobDetails
from utils.context import AutomationRequestContext
from data_handler.extraction.resume_data_parser import ResumeDataParser


class PromptGenerator:
    """
    Generate prompts for the language model.
    """

    @classmethod
    def generate_prompt_for_job_filtering(
        cls,
        job_details: List[JobDetails],
        automation_request_context: AutomationRequestContext,
    ) -> str:
        """
        Generate prompts for the job filtering.
        """
        job_details_jsonified = list(map(lambda x: x.model_dump(), job_details))
        context_jsonified = automation_request_context.model_dump()
        resume = context_jsonified["resume"]["file_path"]
        parsed_resume = ResumeDataParser(resume)
        resume_data = parsed_resume.get_extracted_data()
        bio = context_jsonified["bio"]
        if isinstance(bio, dict):
            bio = bio["bio"]
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
                    prompt += """
                    
                        Here is the work experiences of the user in json format:
                        {context_jsonified["bio"]["work_experiences"]}
                    """
                if "projects" in context_jsonified["bio"]:
                    if len(context_jsonified["bio"]["projects"]) > 0:
                        prompt += """

                            Here is the projects of the user in json format:
                            {context_jsonified["bio"]["projects"]}
                            
                        """
        if work_style:
            prompt += f"""
            
                Here is the preferred work style of the user:
                {work_style}
            """
        prompt += """
        
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
        return prompt
