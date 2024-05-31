from .model import (
    TOOL_CALL,
    END_TASK,
    CONTINUE,
)

# use ollma instead of ChatNVIDIA during the development phase
# from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_community.llms.ollama import Ollama as ChatNVIDIA
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLAlchemyCache
from sqlalchemy import create_engine


engine = create_engine("sqlite:///cache.db")
set_llm_cache(SQLAlchemyCache(engine=engine))