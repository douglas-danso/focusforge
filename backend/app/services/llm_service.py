from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from typing import List
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model_name=settings.OPENAI_MODEL,
            temperature=settings.TEMPERATURE
        )
        self.task_breakdown_template = """Break down the following task into focused blocks of work, each about 25 minutes (a Pomodoro block).
Task: {task}
Total Duration: {duration} minutes

Output a numbered list with concise, actionable goals."""
    
    async def decompose_task(self, task_description: str, duration_minutes: int) -> List[str]:
        """Decompose a task into smaller blocks using LLM"""
        try:
            prompt = PromptTemplate(
                input_variables=["task", "duration"],
                template=self.task_breakdown_template
            )
            
            final_prompt = prompt.format(task=task_description, duration=duration_minutes)
            response = await self.llm.apredict(final_prompt)
            
            # Parse the response into blocks
            blocks = [block.strip() for block in response.split("\n") if block.strip()]
            return blocks
        except Exception as e:
            # Return fallback blocks if LLM fails
            return [f"Work on: {task_description}"]
