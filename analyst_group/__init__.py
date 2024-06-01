from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLAlchemyCache
from sqlalchemy import create_engine
from dotenv import load_dotenv


engine = create_engine("sqlite:///cache.db")
set_llm_cache(SQLAlchemyCache(engine=engine))

# to prevent ChatNVIDIA warning
load_dotenv()