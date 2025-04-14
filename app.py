from typing import TypedDict
from langgraph.graph import StateGraph, END

from modules.speech_to_text import transcribe_speech
from modules.email_generator import generate_email
from modules.send_email import send_email
from modules.user_confirmation import confirm_email
from utils.contact_lookup import get_email_from_name

# Define the state structure
class GraphState(TypedDict):
    text: str
    recipient_name: str
    recipient_email: str
    email_subject: str
    email_body: str

# Step 1: Record and transcribe speech
def record(state: GraphState) -> dict:
    print("\n🎙️ Speak now! Press Ctrl+C to stop recording.")
    text = transcribe_speech()
    print(f"\n📝 Transcribed Text: {text}")
    return {"text": text}

# Step 2: Extract recipient name from transcribed text
def get_recipient(state: GraphState) -> dict:
    text = state["text"]
    # Simple extraction - assumes format like "Send email to [name]" or similar
    # This can be enhanced with more sophisticated NLP if needed
    words = text.lower().split()
    if "to" in words:
        to_index = words.index("to")
        if to_index + 1 < len(words):
            name = words[to_index + 1]
            # Clean up the name (remove punctuation if present)
            name = name.strip(".,;:")
            
            email = get_email_from_name(name)
            if not email:
                print(f"❌ Recipient '{name}' not found in Google Sheets!")
                # Ask only for the name
                name = input("\n Enter correct recipient name: ").strip()
                email = get_email_from_name(name)
                if not email:
                    print(f"❌ Recipient '{name}' still not found in Google Sheets.")
                    return {"recipient_name": name, "recipient_email": ""}
                print(f"📧 Recipient: {name}, Email: {email}")
                return {"recipient_name": name, "recipient_email": email}
            print(f"📧 Recipient: {name}, Email: {email}")
            return {"recipient_name": name, "recipient_email": email}
    
    # Fallback if name couldn't be extracted
    print("❌ Could not extract recipient name from speech. Please specify recipient.")
    name = input("\n👤 Enter recipient name: ").strip()
    email = get_email_from_name(name)
    if not email:
        print(f"❌ Recipient '{name}' not found in Google Sheets.")
    else:
        print(f"📧 Recipient Email: {email}")
    return {"recipient_name": name, "recipient_email": email or ""}

# Step 3: Generate email
def generate(state: GraphState) -> dict:
    # If no email was found for the recipient
    if not state["recipient_email"]:
        print("\n❌ Cannot generate email: No email address found for recipient.")
        print("Please restart and try again with a different recipient name.")
        return {"email_body": "", "email_subject": ""}
        
    email_address, subject, body = generate_email(
        state["recipient_name"], 
        state["text"],
        state["recipient_email"]
    )
    if not body or not email_address:
        print("\n❌ Failed to generate email content.")
        return {"email_body": "", "email_subject": ""}
    
    print("\n📬 Generated Email:\n")
    print(f"Subject: {subject}\n")
    print(body)
    return {"recipient_email": email_address, "email_subject": subject, "email_body": body}

# Step 4: Confirm sending email
def handle_confirmation(state):
    user_input = input("Do you want to send this email? (yes/no): ").strip().lower()
    print(f"📤 Decision returned: {user_input}")
    if user_input == "yes":
        return {"action": "send"}
    else:
        return {"action": "end"}

# Step 5: Send email
def send(state: GraphState) -> dict:
    success = send_email(
        to=state["recipient_email"],
        subject=state["email_subject"],
        body=state["email_body"]
    )
    if success:
        print("✅ Email sent successfully!")
    else:
        print("❌ Failed to send the email.")
    return {}

# Step 6: Cancel flow
def cancel(state: GraphState) -> dict:
    print("❌ Email was not sent.")
    return {}

# Build the graph
Workflow = StateGraph(GraphState)
Workflow.add_node("record", record)
Workflow.add_node("get_recipient", get_recipient)
Workflow.add_node("generate", generate)
Workflow.add_node("confirm", handle_confirmation)
Workflow.add_node("send", send)
Workflow.add_node("cancel", cancel)

Workflow.set_entry_point("record")
Workflow.add_edge("record", "get_recipient")
Workflow.add_edge("get_recipient", "generate")
Workflow.add_edge("generate", "confirm")

# Conditional function returning the next node name
def route_decision(state: GraphState) -> str:
    confirmation = input("\nDo you want to send this email? (yes/no): ").strip().lower()
    return "send" if confirmation == "yes" else "cancel"

Workflow.add_conditional_edges(
    "confirm",
    lambda x: x["action"],
    {
        "send": "send",       # Matches your existing node
        "end": "cancel"       # This is your "cancel" node
    }
)

# Define end points
Workflow.add_edge("send", END)
Workflow.add_edge("cancel", END)

# Compile and run
app = Workflow.compile()
app.invoke({})