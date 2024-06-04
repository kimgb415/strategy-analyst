from .node import AgentState, StrategyStatus, session_config
from .coding.code_saver import CodeSaver
from .coding.code_extractor import PythonCodeExtractor
from langchain_core.runnables import RunnableLambda
import os
from langchain_core.messages import HumanMessage




def human_code_chain():
    extractor = RunnableLambda(PythonCodeExtractor())
    saver = RunnableLambda(CodeSaver(os.path.join('backtesting', 'strategy.py')))

    return extractor | saver


def process_human_in_the_loop(state: AgentState) -> AgentState:
    input("Debug the strategy code...")

    with open(os.path.join('backtesting', 'strategy.py'), 'r') as f:
        result = f.read()
    
    # udpate current strategy
    state["current_strategy"].code = result
    state["current_strategy"].status = StrategyStatus.PENDING_QA
    

    return AgentState(
        messages=[HumanMessage(content=result, name="human supervisor")],
        sender="coder",
        current_strategy=state["current_strategy"],
        debugging_count=state["debugging_count"]
    )