from langchain_nvidia_ai_endpoints import ChatNVIDIA as nvda
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLAlchemyCache
from sqlalchemy import create_engine
from dotenv import load_dotenv
import functools

ChatNVIDIA = functools.partial(nvda, temperature=0.3)

NVDA_MODEL = "meta/llama3-70b-instruct"
# NVDA_MODEL = "meta/llama3-8b-instruct"


engine = create_engine("sqlite:///cache.db")
set_llm_cache(SQLAlchemyCache(engine=engine))

# to prevent ChatNVIDIA warning
load_dotenv()