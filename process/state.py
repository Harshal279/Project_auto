# from typing import TypedDict

# class AgentState(TypedDict):
#         user_input: str
#         plan: str
#         tool_result: str
#         final_output: str

from typing import TypedDict
class Agentstate(TypedDict):
        user_input: str
        plan: str
        messages : list
        current_task : str
        files_changed : list[str]

        tool_result: str
        error: str
        status: str