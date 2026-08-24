# from config import llm_Grock_simple
def answer_node(state):
    prompt = f"""
    User Question:
    {state['user_input']}

    Plan:
    {state['plan']}

    Tool Result:
    {state['tool_result']}

    Generate the final answer.
    """

    response = llm.invoke(prompt)
    state["final_output"] = response.content
    return state
