from config import client
from agent.planning_agent import planner
from tools.web_search import web_search_SERP
from agent.report_agent import answer_node
from process.state import AgentState
from config import llm_Grock_simple
from langgraph.graph import StateGraph, START, END
import json

def llm_decision(error):

    prompt = f"""
You are a coding agent.

The following error occurred:

{error}

Choose ONE tool that can solve the problem.

Available tools:

1. shell
   Use for installing packages, running commands, testing code.

2. files
   Use for reading or modifying files.

3. web_search
   Use when external/current documentation or information is required.

4. done
   Use when no tool is required.

Return ONLY valid JSON.

Format:

{{
    "tool_name": "shell",
    "tool_input": "pip install requests"
}}
"""

    response = llm_Grock_simple.invoke(prompt)

    content = response.content.strip()

    print("LLM:", content)
    return json.loads(content)


def decision_node(state: AgentState):

    decision = llm_decision(state["error"])

    return {
        "tool_name": decision["tool_name"],
        "tool_input": decision["tool_input"]
    }


llm_decision("no module name 'requests'")
graph = StateGraph(AgentState)

graph.add_node("planner", planner)
graph.add_node("web_search", web_search_SERP)
graph.add_node("answer_node", answer_node)

graph.add_edge(START, "planner")
graph.add_edge("planner", "web_search")

graph.add_edge("web_search", "answer_node")
graph.add_edge("answer_node", END)

app = graph.compile()