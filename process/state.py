from typing import TypedDict

class AgentState(TypedDict):
        user_input: str
        plan: str
        tool_result: str
        final_output: str