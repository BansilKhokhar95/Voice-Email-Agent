import os

# Define folder and file structure
structure = {
    "app.py": "",
    "requirements.txt": "",
    "contacts.xlsx": "",  # Placeholder Excel file
    "README.md": "# Voice Email Agent\n\nA Streamlit app that sends emails via voice command.",
    "modules": {
        "speech_to_text.py": "",
        "email_generator.py": "",
        "user_confirmation.py": "",
        "send_email.py": "",
        "feedback.py": "",
    },
    "utils": {
        "contact_lookup.py": "",
        "gmail_auth.py": "",
    },
}

def create_structure(base_path, structure_dict):
    for name, content in structure_dict.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            with open(path, "w") as f:
                f.write(content)

# Run this in your project root folder
if __name__ == "__main__":
    base_path = os.getcwd()
    create_structure(base_path, structure)
    print("✅ Project structure created successfully!")
