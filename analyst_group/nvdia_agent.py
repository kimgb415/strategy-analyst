from . import ChatNVIDIA
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from actions import ActionRegister
from .model import TOOL_CALL, END_TASK
from actions.search import search
from langchain.pydantic_v1 import root_validator


# NVDA_MODEL = "meta/llama3-8b-instruct"
NVDA_MODEL = "llama3"


class ToolCallingNVDA(ChatNVIDIA):
    actions: ActionRegister = None
    tool_name: str
    model: str

    @root_validator(pre=True)
    def initialize_actions(cls, values):
        # TODO: validateing is reuqired upon using ChatNVIDIA
        # values = ChatNVIDIA.validate_client(values)
        tool_name = values.get('tool_name')
        if tool_name:
            # tool_name should be the name of the target python script in the `actions` folder
            values['actions'] = ActionRegister(cls, tool_name)
        return values


def create_router_agent(llm: ChatNVIDIA):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a router, you have to decide the next action based on the last message."
                "If the last message is a tool call, you should call the tool."
                "If the last message is an end task, you should end the conversation."
                "If the last message is neither, you should continue the conversation."
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    return prompt | llm


def create_search_agent(llm: ToolCallingNVDA):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful AI assistant, collaborating with other assistants."
                " Use the provided tools to progress towards answering the question."
                " If you are unable to fully answer, that's OK, another assistant with different tools "
                " will help where you left off. Execute what you can to make progress."
                " If you or any of the other assistants have the final answer or deliverable,"
                f" prefix your response with {END_TASK} so the team knows to stop."
                " If you need to call a tool to help you,"
                f" prefix your response with {TOOL_CALL} to use a tool."
                " ## Avaiable tools: ##"
                f" {llm.actions.list_abilities_for_prompt()}"
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    return prompt | llm


def create_search_executor(llm: ToolCallingNVDA):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system", 
                """
                    Convert the provided message into an tool call.
                    Reply only in json with the following format:

                    {
                        \"tool\": {
                            \"name\": \"tool name\",
                            \"args\": {
                                \"arg1\": \"value1", etc...
                            }
                        }
                    }
                """
                " ## Reference for tools: ##"
                f" {llm.actions.list_abilities_for_prompt()}"
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    # chain the serach action
    return prompt | llm | search



llm = ToolCallingNVDA(tool_name="search", model=NVDA_MODEL)
research_agent = create_search_agent(llm)
research_executor = create_search_executor(llm)
router_agent = create_router_agent(ChatNVIDIA(model=NVDA_MODEL))