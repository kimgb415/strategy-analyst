from langchain_openai import ChatOpenAI
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLAlchemyCache
from sqlalchemy import create_engine
from dotenv import load_dotenv
import functools

ChatModel = functools.partial(ChatNVIDIA, temperature=0.3)

CHAT_MODEL_NAME = "meta/llama-3.1-70b-instruct"


engine = create_engine("sqlite:///cache.db")
set_llm_cache(SQLAlchemyCache(engine=engine))

load_dotenv()