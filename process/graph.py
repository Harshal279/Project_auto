from config import client
from agent.planning_agent import planner
from tools.web_search import web_search_SERP
from agent.report_agent import answer_node
from process.state import AgentState
from langgraph.graph import StateGraph, START, END

graph = StateGraph(AgentState)

graph.add_node("planner", planner)
graph.add_node("web_search", web_search_SERP)
graph.add_node("answer_node", answer_node)

graph.add_edge(START, "planner")
graph.add_edge("planner", "web_search")
graph.add_edge("web_search", "answer_node")
graph.add_edge("answer_node", END)

app = graph.compile()