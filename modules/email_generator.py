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
You are an AI assistant that extracts email components and generates a professional email from this instruction:

\"\"\"{command}\"\"\"

Follow this exact format:
Recipient: <n>
Subject: <subject>
Body:
<email body>

Always sign the email with "Bansil Khokhar" instead of "[Your Name]" or any other generic signature.
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
