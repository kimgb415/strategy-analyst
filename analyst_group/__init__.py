from langchain_openai import ChatOpenAI
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLAlchemyCache
from sqlalchemy import create_engine
from dotenv import load_dotenv
import functools

ChatModel = functools.partial(ChatOpenAI, temperature=0.3)

CHAT_MODEL_NAME = "gpt-4-turbo"


engine = create_engine("sqlite:///cache.db")
set_llm_cache(SQLAlchemyCache(engine=engine))

load_dotenv()