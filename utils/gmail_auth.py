import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scope: send email
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def gmail_authenticate():
    creds = None
    token_path = "token.json"
    creds_path = "credentials.json"

    # Load existing token if available
    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    # If no (valid) token, perform OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for future use
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

    # Return Gmail API service
    return build("gmail", "v1", credentials=creds)
