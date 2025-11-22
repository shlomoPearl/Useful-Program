import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

load_dotenv()


class GmailAuth:
    def __init__(self):
        self.credentials_file = "credentials.json"
        self.token_file = "token.json"
        self.scopes = ["https://www.googleapis.com/auth/gmail.readonly",
                       "https://www.googleapis.com/auth/userinfo.profile"]
        self.redirect_uri = os.getenv("REDIRECT_URI")
        self.creds = None
        self.service = None
        self.user_email = None
        self.user_id = None

    def load_token(self):
        if not os.path.exists(self.token_file):
            return None
        creds = Credentials.from_authorized_user_file(
            self.token_file,
            self.scopes
        )
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        self.creds = creds
        self.initialize_service()
        return creds

    def create_flow(self):
        return Flow.from_client_secrets_file(
            self.credentials_file,
            redirect_uri=self.redirect_uri,
            scopes=self.scopes)

    def exchange_code(self, code, state=None):
        flow = self.create_flow()
        flow.fetch_token(code=code)
        self.creds = flow.credentials
        self.save_token()
        self.initialize_service()
        return True

    def save_token(self):
        if self.creds:
            with open(self.token_file, "w") as f:
                f.write(self.creds.to_json())

    def initialize_service(self):
        self.service = build("gmail", "v1", credentials=self.creds)
        profile = self.service.users().getProfile(userId="me").execute()
        self.user_email = profile.get("emailAddress")
        oauth2_service = build('oauth2', 'v2', credentials=self.creds)
        userinfo = oauth2_service.userinfo().get().execute()
        self.user_id = userinfo["id"]

    def get_service(self):
        if not self.service:
            raise Exception("Service not authenticated yet.")
        return self.service
