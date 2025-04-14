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
    You are an AI assistant helping a user compose professional, well-structured emails.
    
    ## CONTEXT
    - Recipient name: {recipient}
    - Sender name: {sender_name}
    - User's voice instruction: {purpose}
    
    ## GUIDELINES
    1. Extract the key points from the user's instruction
    2. Create a clear and concise subject line related to the purpose
    3. Use a professional greeting appropriate for the relationship
    4. Structure the email with clear paragraphs and logical flow
    5. Include a proper closing
    6. Keep the tone professional but friendly
    7. Ensure proper grammar and spelling
    8. Avoid unnecessary jargon
    
    ## OUTPUT FORMAT
    Subject: [Create a concise, relevant subject line]
    
    Dear {recipient},
    
    [Body of the email with clear, well-structured paragraphs]
    
    [Professional closing],
    {sender_name}
    
    ## IMPORTANT
    - If the purpose contains meeting details, include date, time, and location
    - If it's a follow-up email, acknowledge previous communications
    - If it's urgent, make that clear in a respectful way
    
    Create a complete, ready-to-send email that needs no additional editing.
    """,
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
            # If LLM fails, use a fallback template
            print(f"❌ LLM generation failed: {str(e)}")
            print("Using fallback template instead...")
            
            # Default email template
            subject = f"Regarding: {purpose[:50]}"
            body = f"""Dear {recipient_name},

I hope this email finds you well. I wanted to reach out regarding {purpose}.

Please let me know if you're available to discuss this matter further.

Best regards,
{sender_name}
"""
            return email_address, subject, body
            
    except Exception as e:
        print(f"❌ Email generation completely failed: {str(e)}")
        return None, None, None
