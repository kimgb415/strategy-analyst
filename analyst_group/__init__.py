from .model import (
    TOOL_CALL,
    END_TASK,
    CONTINUE,
)

# use ollma instead of ChatNVIDIA during the development phase
# from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_community.llms.ollama import Ollama as ChatNVIDIA