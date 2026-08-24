import asyncio
import json
from langgraph.graph import StateGraph, START,END
from typing import TypedDict,Literal
from langchain_openai import ChatOpenAI
import serpapi
from openai import OpenAI
from langchain_openai import ChatOpenAI
from config import llm_nvidia_hardcore, llm_Grock_simple, client
from process.graph import app
from memory.shared_data import user_input

            
def main():
    user_prompt = user_input
    print(f"enhancing the prompt using {llm_nvidia_hardcore.model}")
    prompt = f"""
    You are an expert Prompt Engineering AI and also classify the prompt.

    Your task is to transform the user's request into a clear, self-contained prompt for another LLM.

    The generated prompt must:

    - Start with "You are..." and assign the most appropriate expert role.
    - Explain what the user is asking for by elaborating on their intent.
    - Expand the user's objective so another LLM fully understands the task.
    - Preserve the user's original intent exactly.
    - Do NOT invent new features, requirements, or constraints.
    - Do NOT answer the user's request.
    - Do NOT ask for clarification or make assumptions.

    here is an example of a good generated prompt(the given example is the exact kind of output you should produce):"
    You are a Senior AI Engineer specializing in Agentic AI and LangGraph.

The user wants you to design and develop a chatbot using LangGraph. Your objective is to create a well-structured, scalable, and maintainable conversational AI application that leverages LangGraph effectively. Carefully understand the user's requirements and architecture needs before implementation.

If important implementation details are missing, ask concise clarification questions. If operating autonomously, make reasonable assumptions and explicitly mention them before proceeding.

Focus on producing clean architecture, modular code, clear explanations, and best engineering practices while staying aligned with the user's original request."
    User Request:
    {user_prompt}

    Return only the generated prompt.
    """

    enhanced_prompt = llm_nvidia_hardcore.invoke(prompt)
    print(f"enhanced prompt: {enhanced_prompt.content}")

    state = {
        "user_input": enhanced_prompt.content,
        "plan": "",
        "tool_result": "",
        "final_output": ""
    }

    result = asyncio.run(app.ainvoke(state))

    print(result["final_output"])

if __name__ == "__main__":
    main()
