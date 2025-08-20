import json
import openai
import os


class LanguageModelClient:
    def __init__(self, model: str):
        self.model = model
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_response_json(self, prompt: dict) -> dict:
        messages = [{"role": k, "content": v} for k, v in prompt.items()]
        response = self.client.chat.completions.create(
            messages=messages, model=self.model
        )
        json_response = response.choices[0].message.content
        return json.loads(json_response)

    def generate_response_text(self, prompt: dict) -> str:
        messages = [{"role": k, "content": v} for k, v in prompt.items()]
        response = self.client.chat.completions.create(
            messages=messages, model=self.model
        )
        return response.choices[0].message.content
