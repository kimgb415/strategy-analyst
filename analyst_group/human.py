from .node import AgentState, StrategyStatus
import os
from langchain_core.messages import HumanMessage
from .model import HUMAN_SENDER, QA_SENDER, TUNING_SENDER



def process_human_in_the_loop(state: AgentState) -> AgentState:
    if state["sender"] == QA_SENDER:
        input("Debug the strategy code...")
        with open(os.path.join('backtesting', 'strategy.py'), 'r') as f:
            result = f.read()
        
        # udpate current strategy
        state["current_strategy"].code = result
        state["current_strategy"].status = StrategyStatus.PENDING_QA
    elif state["sender"] == TUNING_SENDER:
        input("Tune the strategy code...")
        raise NotImplementedError("Human Support for tuning not implemented yet")
    else:
        raise ValueError(f"Invalid sender to human edge: {state['sender']}")    


    return AgentState(
        messages=[HumanMessage(content=result, name="human supervisor")],
        sender=HUMAN_SENDER,
        current_strategy=state["current_strategy"],
        debugging_count=state["debugging_count"]
    )