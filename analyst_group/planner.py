from . import ChatNVIDIA
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from .nvdia_agent import NVDA_MODEL
from enum import Enum
import re
from pydantic import BaseModel


PLANNER_SYSTEM_MESSAGE = """You are a professional coding planner. Given a implementation task, you need to break it down into smaller coding steps.
    Wrap your steps in a markdown bullet list starting with '*'.
    Coding steps should only contain code implementation details, steps like 'create a script file' should be excluded.
    You should focus on planning only, no code implementation should be done here.
"""

TASK_PATTERN = r'\* (.*)'


class StepStatus(Enum):
    PENDING = 1
    COMPLETED = 2
    FAILED = 3


class Step(BaseModel):
    description: str
    status: StepStatus = StepStatus.PENDING


class PlanExtractor():
    def __call__(self, message: str) -> None:
        steps = self.extract_steps(message)

    def extract_steps(self, message: str):
        bullet_list = re.findall(TASK_PATTERN, message)
        
        return bullet_list


def create_planning_agent(llm: ChatNVIDIA):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                PLANNER_SYSTEM_MESSAGE
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    return prompt | llm


planning_agent = create_planning_agent(ChatNVIDIA(model=NVDA_MODEL))