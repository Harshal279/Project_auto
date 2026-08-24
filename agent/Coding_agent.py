from typing import TypedDict

class AgentState(TypedDict):
    error: str
    tool_name: str
    tool_input: str
    tool_result: str