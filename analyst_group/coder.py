from . import ChatNVIDIA
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from .nvdia_agent import NVDA_MODEL
from .coding.code_extractor import PythonCodeExtractor
from .coding.code_saver import CodeSaver
from langchain_core.runnables import RunnableLambda 


CODER_SYSTEM_MESSAGE_SIDE_NOTES = """Wrap your code in a code block that specifies the script type. 
    The user can't modify your code. So do not suggest incomplete code which requires others to modify. 
    Don't use a code block if it's not intended to be executed by the executor. Don't include multiple code blocks in one response. 
    Suggest the full code instead of partial code or code changes, including the original code. 
"""


def create_coding_agnet(llm: ChatNVIDIA):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                CODER_SYSTEM_MESSAGE_SIDE_NOTES
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    code_extractor = PythonCodeExtractor()
    code_saver = CodeSaver('strategy.py')

    return prompt | llm | RunnableLambda(code_extractor) | RunnableLambda(code_saver)

    # return prompt | llm


coding_agent = create_coding_agnet(ChatNVIDIA(model=NVDA_MODEL))