# workflow_graph.py

from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda

from modules.speech_to_text import transcribe_speech
from modules.email_generator import generate_email
from modules.user_confirmation import confirm_email
from modules.send_email import send_email
from modules.feedback import get_feedback

# 1. Define state schema
class State(dict):
    pass

# 2. Define nodes
def speech_node(state):
    text = transcribe_speech()
    return {"input_text": text, **state}

def generate_email_node(state):
    input_text = state.get("input_text", "")
    if "to" in input_text and "about" in input_text:
        try:
            name = input_text.split("to")[1].split("about")[0].strip()
            purpose = input_text.split("about")[1].strip()
        except:
            return {"error": "Couldn't extract name/purpose"}
    else:
        return {"error": "Please mention the recipient and purpose clearly."}

    email, content = generate_email(name, purpose)
    return {
        "name": name,
        "purpose": purpose,
        "email": email,
        "email_content": content,
        **state
    }

def confirmation_node(state):
    email_content = state.get("email_content", "")
    confirmation = confirm_email(email_content)
    return {"confirmation": confirmation, **state}

def send_email_node(state):
    to = state.get("email")
    purpose = state.get("purpose")
    body = state.get("email_content")
    result = send_email(to, f"Regarding: {purpose}", body)
    return {"email_status": result, **state}

def feedback_node(state):
    get_feedback("👍")  # Placeholder
    return state

# 3. Build the LangGraph workflow
def get_workflow():
    builder = StateGraph(State)

    builder.add_node("speech_to_text", RunnableLambda(speech_node))
    builder.add_node("generate_email", RunnableLambda(generate_email_node))
    builder.add_node("confirm", RunnableLambda(confirmation_node))
    builder.add_node("send", RunnableLambda(send_email_node))
    builder.add_node("feedback", RunnableLambda(feedback_node))

    builder.set_entry_point("speech_to_text")
    builder.add_edge("speech_to_text", "generate_email")
    builder.add_edge("generate_email", "confirm")

    builder.add_conditional_edges(
        "confirm",
        lambda state: "send" if state["confirmation"] else END,
        {
            "send": "send",
            END: END,
        }
    )

    builder.add_edge("send", "feedback")
    builder.add_edge("feedback", END)

    return builder.compile()
