# modules/email_generator.py

from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from utils.contact_lookup import get_email_from_name

import os
from dotenv import load_dotenv
load_dotenv()

# Get Groq API key from .env
groq_api_key = os.getenv("GROQ_API_KEY")

# Load Groq LLM
llm = ChatGroq(api_key=groq_api_key, model_name="gemma2-9b-it")

# Prompt Template
prompt_template = PromptTemplate(
    input_variables=["recipient", "purpose", "sender_name"],
    template="""
    You are a highly skilled AI assistant specialized in drafting professional, polished, and context-aware emails.

    ## CONTEXT
    - Recipient Name: {recipient}
    - Sender Name: {sender_name}
    - User's Voice Instruction: {purpose}

    ## OBJECTIVE
    Write a complete, ready-to-send email that fully addresses the user's purpose while maintaining a professional and friendly tone.

    ## INSTRUCTIONS
    1. Carefully extract key details, intentions, and emotional tone from the user's voice instruction.
    2. Write a clear, concise, and relevant subject line that accurately reflects the email's purpose.
    3. Start with an appropriate professional greeting, considering the sender's relationship with the recipient.
    4. Structure the body of the email into logically ordered, well-organized paragraphs.
    5. Make the email sound thoughtful, warm, and human — not robotic or overly formal.
    6. Use polite and direct language that is easy to understand, avoiding jargon and fluff.
    7. Ensure proper grammar, correct spelling, and clear sentence construction.
    8. Close the email with a courteous and fitting sign-off.

    ## SPECIAL CONSIDERATIONS
    - If the purpose includes meeting details, clearly mention the date, time, and location.
    - If the email is a follow-up, acknowledge any prior conversation or email thread.
    - If the message is urgent, communicate that politely and respectfully.
    - If the email contains a request, be clear and specific about the desired action or response.

    ## OUTPUT FORMAT
    Subject: [Concise and relevant subject line]

    Dear {recipient},

    [Well-structured, clear, and naturally flowing email body.]

    [Professional and courteous closing],
    {sender_name}
    """
)

# Chain
chain = prompt_template | llm

# Main function to generate email
def generate_email(recipient_name: str, purpose: str, recipient_email: str = None):
    # Get email from name via Google Sheets if not provided
    try:
        sender_name = "Bansil Khokhar"
        
        if not recipient_email:
            email_address = get_email_from_name(recipient_name)
            if not email_address:
                print(f"❌ Warning: Email not found for '{recipient_name}' in Google Sheet.")
                # Try one more lookup with lower case
                email_address = get_email_from_name(recipient_name.lower())
                if not email_address:
                    return None, None, None
        else:
            email_address = recipient_email
        
        try:
            # Try using the LLM first
            full_response = chain.invoke({
                "recipient": recipient_name, 
                "purpose": purpose,
                "sender_name": sender_name
            })
            email_content = str(full_response.content)
            
            # Extract subject line
            subject = "Voice-generated Email"  # Default fallback
            cleaned_content = email_content
            
            if "Subject:" in email_content:
                content_parts = email_content.split("Subject:", 1)
                if len(content_parts) > 1:
                    second_part = content_parts[1].strip()
                    subject_line = second_part.split("\n", 1)[0].strip()
                    subject = subject_line
                    
                    # Remove the subject line from the email body
                    if len(second_part.split("\n", 1)) > 1:
                        # Keep everything after the subject line
                        body_content = second_part.split("\n", 1)[1].strip()
                        cleaned_content = body_content
            
            return email_address, subject, cleaned_content
            
        except Exception as e:
            # If LLM generation fails, notify and return a clear message
            print(f"❌ LLM generation failed: {str(e)}")
            return email_address, None, "Email is not generated. Please try again."
            
    except Exception as e:
        print(f"❌ Email generation completely failed: {str(e)}")
        return None, None, None
    