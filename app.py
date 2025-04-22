import streamlit as st
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, Literal

from modules.speech_to_text import transcribe_speech
from modules.email_generator import generate_email
from modules.send_email import send_email
from utils.contact_lookup import get_email_from_name

class GraphState(TypedDict):
    text: str
    recipient_name: str
    recipient_email: str
    email_subject: str
    email_body: str
    status: Optional[Literal["success", "error"]]
    error_message: Optional[str]

# LangGraph node functions
def record_speech(state: GraphState) -> dict:
    try:
        text = st.session_state.get("voice_text")
        if not text:
            return {"status": "error", "error_message": "No input text provided."}
        return {"text": text, "status": "success"}
    except Exception as e:
        return {"status": "error", "error_message": f"Recording error: {str(e)}"}

def generate_email_content(state: GraphState) -> dict:
    if state.get("status") == "error":
        return state
    try:
        recipient_name, recipient_email, subject, body = generate_email(state["text"])
        if not recipient_name:
            return {"status": "error", "error_message": "Failed to extract recipient"}
        return {
            "recipient_name": recipient_name,
            "email_subject": subject,
            "email_body": body,
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "error_message": f"Email generation error: {str(e)}"}

def lookup_email(state: GraphState) -> dict:
    if state.get("status") == "error":
        return state
    try:
        name = state["recipient_name"]
        email = get_email_from_name(name)
        if not email:
            name = st.session_state.get("manual_name", name)
            email = get_email_from_name(name)
            if not email:
                return {"status": "error", "error_message": f"No email found for {name}"}
        return {"recipient_name": name, "recipient_email": email, "status": "success"}
    except Exception as e:
        return {"status": "error", "error_message": f"Email lookup error: {str(e)}"}

def preview_and_confirm(state: GraphState) -> dict:
    if state.get("status") == "error":
        return state
    try:
        body = state["email_body"].replace("[Your Name]", "Bansil Khokhar")
        st.session_state["preview"] = {
            "to": f"{state['recipient_name']} ({state['recipient_email']})",
            "subject": state["email_subject"],
            "body": body
        }
        if st.session_state.get("confirm_send"):
            return {"action": "send", "email_body": body, "status": "success"}
        else:
            return {"action": "cancel", "status": "success"}
    except Exception as e:
        return {"action": "cancel", "status": "error", "error_message": f"Confirmation error: {str(e)}"}

def send_email_step(state: GraphState) -> dict:
    if state.get("status") == "error":
        return state
    try:
        success = send_email(
            to=state["recipient_email"],
            subject=state["email_subject"],
            body=state["email_body"]
        )
        if success:
            return {"status": "success"}
        else:
            return {"status": "error", "error_message": "Failed to send email"}
    except Exception as e:
        return {"status": "error", "error_message": f"Email sending error: {str(e)}"}

def handle_cancellation(state: GraphState) -> dict:
    return {"status": "success"}

# Build LangGraph
def build_app():
    workflow = StateGraph(GraphState)
    workflow.add_node("record_speech", record_speech)
    workflow.add_node("generate_email", generate_email_content)
    workflow.add_node("lookup_email", lookup_email)
    workflow.add_node("preview_confirm", preview_and_confirm)
    workflow.add_node("send_email", send_email_step)
    workflow.add_node("cancel", handle_cancellation)

    workflow.set_entry_point("record_speech")
    workflow.add_edge("record_speech", "generate_email")
    workflow.add_edge("generate_email", "lookup_email")
    workflow.add_edge("lookup_email", "preview_confirm")
    workflow.add_conditional_edges(
        "preview_confirm",
        lambda x: x.get("action", "cancel"),
        {"send": "send_email", "cancel": "cancel"}
    )
    workflow.add_edge("send_email", END)
    workflow.add_edge("cancel", END)

    return workflow.compile()

app = build_app()

st.title("🎙️ Voice Email Assistant")

# Step 1: Capture voice and store it
if st.button("Activate Assistant"):
    try:
        text = transcribe_speech()
        st.session_state["voice_text"] = text
        st.success("✅ Voice captured!")
    except Exception as e:
        st.error(f"❌ Recording error: {str(e)}")

# Step 2: Run workflow
if "voice_text" in st.session_state:
    st.write("### 📝 Transcribed Text")
    st.write(st.session_state["voice_text"])

    if st.button("Run Email Workflow"):
        output = app.invoke({"text": st.session_state["voice_text"]})
        st.session_state["workflow_output"] = output

# Step 3: Display result (once)
if "workflow_output" in st.session_state:
    output = st.session_state["workflow_output"]
    st.write("### ✅ Workflow Result")
    st.json(output)

    if st.session_state.get("preview"):
        preview = st.session_state["preview"]
        st.write("### 📬 Email Preview")
        st.text(f"To: {preview['to']}")
        st.text(f"Subject: {preview['subject']}")
        st.text(preview["body"])

        confirm = st.radio("Send this email?", ["Yes", "No"])
        st.session_state["confirm_send"] = confirm == "Yes"

        if st.button("Confirm Send"):
            f_output = app.invoke({"confirm_send": st.session_state["confirm_send"]})
            final_output = dict(f_output)
            st.write("### 📤 Final Output")
            if final_output.get("status") == "success":
                st.success("✅ Email sent successfully!")
            else:
                st.error("❌ Email failed to send.")