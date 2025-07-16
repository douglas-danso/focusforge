from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from src.core.settings import settings
import os

load_dotenv()
llm = ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                model_name=settings.OPENAI_MODEL,
                temperature=settings.TEMPERATURE
            )


def decompose_task(task_description: str, minutes: int):
    prompt = PromptTemplate(
        input_variables=["task", "duration"],
        template=open("prompts/task_breakdown_prompt.txt").read()
    )
    final_prompt = prompt.format(task=task_description, duration=minutes)
    response = llm.predict(final_prompt)
    return response.split("\n")
