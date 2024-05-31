from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.messages import BaseMessage, AIMessage
from typing import List
from langchain_community.chat_message_histories import SQLChatMessageHistory

# class InMemoryHistory(BaseChatMessageHistory, BaseModel):
#     messages: List[BaseMessage] = Field(default_factory=list)

#     def add_messages(self, messages: List[BaseMessage]) -> None:
#         self.messages.extend(messages)

#     def clear(self) -> None:
#         self.messages = []

# message_store = {}

# def get_by_session_id(session_id: str) -> BaseChatMessageHistory:
#     if session_id not in message_store:
#         message_store[session_id] = InMemoryHistory()
#     return message_store[session_id]

def get_sql_session_id(session_id: str) -> BaseChatMessageHistory:
    return SQLChatMessageHistory(
        session_id=session_id,
        connection_string="sqlite:///chat_history.db", 
    )