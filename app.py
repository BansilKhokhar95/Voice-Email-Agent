from typing import TypedDict, Optional, Literal
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

from modules.speech_to_text import transcribe_speech
from modules.email_generator import generate_email
from modules.send_email import send_email
from utils.contact_lookup import get_email_from_name

# Load environment variables
load_dotenv()

# Define the state structure
class GraphState(TypedDict):
    text: str
    recipient_name: str
    recipient_email: str
    email_subject: str
    email_body: str
    status: Optional[Literal["success", "error"]]
    error_message: Optional[str]

# Step 1: Record and transcribe speech
def record_speech(state: GraphState) -> dict:
    try:
        print("\n🎙️ Speak now! Press Ctrl+C to stop recording.")
        text = transcribe_speech()
        if not text:
            print("❌ No speech detected or transcription failed.")
            return {"status": "error", "error_message": "Speech transcription failed"}
            
        print(f"\n📝 Transcribed Text: {text}")
        return {"text": text, "status": "success"}
    except Exception as e:
        print(f"❌ Recording error: {str(e)}")
        return {"status": "error", "error_message": f"Recording error: {str(e)}"}

# Step 2: Generate email content and extract recipient from AI response
def generate_email_content(state: GraphState) -> dict:
    if state.get("status") == "error":
        return state
        
    try:
        text = state["text"]
        print(f"\n🤖 Generating email from: \"{text}\"")
        
        # Generate email using the LLM
        recipient_name, _, subject, body = generate_email(text)
        
        if not recipient_name:
            print("❌ Could not extract recipient from generated email.")
            return {
                "status": "error", 
                "error_message": "Failed to extract recipient from generated email"
            }
            
        print(f"\n👤 Extracted recipient: {recipient_name}")
        
        return {
            "recipient_name": recipient_name,
            "email_subject": subject, 
            "email_body": body,
            "status": "success"
        }
    except Exception as e:
        print(f"❌ Email generation error: {str(e)}")
        return {"status": "error", "error_message": f"Email generation error: {str(e)}"}

# Step 3: Look up email address from recipient name
def lookup_email(state: GraphState) -> dict:
    if state.get("status") == "error":
        return state
        
    try:
        recipient_name = state["recipient_name"]
        print(f"\n🔍 Looking up email for: {recipient_name}")
        
        email = get_email_from_name(recipient_name)
        if not email:
            print(f"❌ No email found for '{recipient_name}' in Google Sheets.")
            
            # Ask for correction
            new_name = input("\n👤 Enter correct recipient name (or press Enter to retry): ").strip()
            if new_name:
                print(f"🔄 Trying with recipient: {new_name}")
                email = get_email_from_name(new_name)
                if email:
                    print(f"✅ Email found: {email}")
                    return {
                        "recipient_name": new_name,
                        "recipient_email": email,
                        "status": "success"
                    }
            
            return {
                "status": "error",
                "error_message": f"No email found for recipient '{recipient_name}'"
            }
            
        print(f"✅ Email found: {email}")
        return {
            "recipient_email": email,
            "status": "success"
        }
    except Exception as e:
        print(f"❌ Email lookup error: {str(e)}")
        return {"status": "error", "error_message": f"Email lookup error: {str(e)}"}

# Step 4: Preview email and confirm sending
def preview_and_confirm(state: GraphState) -> dict:
    if state.get("status") == "error":
        return state
        
    try:
        # Format the email body
        email_body = state["email_body"]
        
        # Make sure your name is included
        if "[Your Name]" in email_body:
            email_body = email_body.replace("[Your Name]", "Bansil Khokhar")
        
        # Display the email for confirmation
        print("\n" + "="*50)
        print("📬 EMAIL PREVIEW")
        print("="*50)
        print(f"To: {state['recipient_name']} ({state['recipient_email']})")
        print(f"Subject: {state['email_subject']}")
        print("-"*50)
        print(f"{email_body}")
        print("="*50)
        
        # Update state with formatted body
        state_update = {"email_body": email_body}
        
        # Get user confirmation
        user_input = input("\n❓ Send this email? (yes/no): ").strip().lower()
        
        if user_input == "yes":
            print("🔄 Proceeding to send email...")
            return {**state_update, "action": "send", "status": "success"}
        else:
            print("❌ Email sending cancelled by user.")
            return {**state_update, "action": "cancel", "status": "success"}
    except Exception as e:
        print(f"❌ Confirmation error: {str(e)}")
        return {"action": "cancel", "status": "error", "error_message": f"Confirmation error: {str(e)}"}

# Step 5: Send email
def send_email_step(state: GraphState) -> dict:
    if state.get("status") == "error":
        return state
        
    try:
        print(f"\n📤 Sending email to {state['recipient_email']}...")
        
        success = send_email(
            to=state["recipient_email"],
            subject=state["email_subject"],
            body=state["email_body"]
        )
        
        if success:
            print("✅ Email sent successfully!")
            return {"status": "success"}
        else:
            print("❌ Failed to send the email.")
            return {"status": "error", "error_message": "Failed to send the email"}
    except Exception as e:
        print(f"❌ Email sending error: {str(e)}")
        return {"status": "error", "error_message": f"Email sending error: {str(e)}"}

# Step 6: Handle cancellation
def handle_cancellation(state: GraphState) -> dict:
    print("📝 Email was not sent. Process completed.")
    return {"status": "success"}

def main():
    # Build the workflow graph
    workflow = StateGraph(GraphState)
    
    # Add nodes to the graph
    workflow.add_node("record_speech", record_speech)
    workflow.add_node("generate_email", generate_email_content)
    workflow.add_node("lookup_email", lookup_email)
    workflow.add_node("preview_confirm", preview_and_confirm)
    workflow.add_node("send_email", send_email_step)
    workflow.add_node("cancel", handle_cancellation)
    
    # Set entry point
    workflow.set_entry_point("record_speech")
    
    # Add edges
    workflow.add_edge("record_speech", "generate_email")
    workflow.add_edge("generate_email", "lookup_email")
    workflow.add_edge("lookup_email", "preview_confirm")
    
    # Conditional edge based on user confirmation
    workflow.add_conditional_edges(
        "preview_confirm",
        lambda x: x.get("action", "cancel"),
        {
            "send": "send_email",
            "cancel": "cancel"
        }
    )
    
    # Define end points
    workflow.add_edge("send_email", END)
    workflow.add_edge("cancel", END)
    
    # Compile and execute the workflow
    app = workflow.compile()
    app.invoke({})

if __name__ == "__main__":
    print("🚀 Voice Email Agent")
    print("="*50)
    print("Speak your email request, and I'll help you send it.")
    print("For example: \"Send an email to Rakesh to reschedule our meeting to tomorrow at 8pm.\"")
    print("="*50)
    main()
    print("\n✨ Process completed. Thank you for using Voice Email Agent!")
