import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class GmailAuth:
    def __init__(self):
        self.token_file = "token.json"
        self.credentials_file = "credentials.json"
        self.scopes = ['https://www.googleapis.com/auth/gmail.readonly']
        self.service = None
        self.profile = None

        creds = self._load_or_get_credentials()
        print("The authentication was successful")

        self.service = build("gmail", "v1", credentials=creds)
        self.profile = self.service.users().getProfile(userId='me').execute()

    def _load_or_get_credentials(self):
        creds = None
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
        if not creds or not creds.valid:
            creds = self._get_new_credentials(creds)
        return creds

    def _get_new_credentials(self, creds):
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, self.scopes,
            )
            flow.redirect_uri = 'http://localhost:5000/'
            creds = flow.run_local_server(port=5000)
        with open(self.token_file, "w") as token:
            token.write(creds.to_json())
        return creds

    
    def get_service(self):
        return self.service

    def get_user_email(self):
        return self.profile['emailAddress']