from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# Replace with your actual Sheet ID
SHEET_ID = "18fIkLydmEA2xS2mh37LfKnyMVJjCUjOdVLq442UpyRU"
RANGE = "Contacts!A2:B"  # Assuming headers are in row 1 (Name, Email)

def sheets_authenticate():
    creds = None
    if os.path.exists("token_sheets.json"):
        creds = Credentials.from_authorized_user_file("token_sheets.json", SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token_sheets.json", "w") as token:
            token.write(creds.to_json())
    return creds

def get_contacts():
    creds = sheets_authenticate()
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE).execute()
    values = result.get("values", [])

    contacts = {}
    for row in values:
        if len(row) >= 2:
            name, email = row[0].strip().lower(), row[1].strip()
            contacts[name] = email
    return contacts

def get_email_from_name(name):
    contacts = get_contacts()
    return contacts.get(name.lower())
