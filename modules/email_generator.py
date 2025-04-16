from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
from utils import contact_lookup

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(api_key=groq_api_key, model_name="gemma2-9b-it")

prompt_template = PromptTemplate(
    input_variables=["command"],
    template="""
You are a highly skilled AI email assistant tasked with drafting clear, polite, and situationally appropriate emails based on the following instruction:

Instruction:
\"\"\"{command}\"\"\"

Your response must strictly follow this structure:
Recipient: <recipient name or placeholder>
Subject: <email subject>
Body:
<well-structured email body>

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
    
Bansil Khokhar
- Do not include placeholders like "[Your Name]" or extra explanations.

Your output should only be the completed email in the specified format.
"""
)

chain = prompt_template | llm

def generate_email(command: str):
    try:
        response = chain.invoke({"command": command})
        content = str(response.content).strip()
        print("Content:", content)

        lines = content.splitlines()
        recipient_name = ""
        subject = ""
        body = ""

        # Extract recipient name
        for i, line in enumerate(lines):
            if line.lower().startswith("recipient:"):
                recipient_name = line.split(":", 1)[1].strip()
                recipient_line_idx = i
                break

        # Extract email address from the sheet
        recipient_email = contact_lookup.get_email_from_name(recipient_name)

        # Extract subject
        for i, line in enumerate(lines):
            if line.lower().startswith("subject:"):
                subject = line.split(":", 1)[1].strip()
                subject_line_idx = i
                break

        # Extract body
        body_start_index = subject_line_idx + 1
        body = "\n".join(lines[body_start_index:]).strip()

        # Clean the body text
        # Remove "Body:" prefix if it exists
        if body.lower().startswith("body:"):
            body = body[5:].strip()
            
        # Replace [Your Name] with Bansil Khokhar if it exists
        body = body.replace("[Your Name]", "Bansil Khokhar")
        
        print(f"\nRecipient Name: {recipient_name}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")

        return recipient_name, recipient_email, subject, body

    except Exception as e:
        print(f"❌ Email generation failed: {str(e)}")
        return None, None, None, None
