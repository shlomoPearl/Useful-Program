from __future__ import print_function

import base64
import os.path
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

address_search = "gviyarevava@revava.co.il"


# If modifying these scopes, delete the file token.json.


def parse_date(date_str, strp, date_format):
    if strp:  # '%d/%m/%Y'
        return datetime.strptime(date_str, date_format)
    else:
        return date_str.strftime(date_format)


class Gmail:

    def __init__(self, address="", key_word=None, result_num=None, date_range=[]):
        self.address = address
        self.key_word = key_word
        self.result_num = result_num
        self.date_range = [parse_date(date_range[0], True, '%d/%m/%Y').isoformat() + 'Z',
                           (parse_date(date_range[1], True, '%d/%m/%Y') + timedelta(days=1)).isoformat() + 'Z']
        self.token_file = "token.json"
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        self.credentials_file = "credentials.json"

    def authenticate(self):
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        creds = None
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials, self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.token_file, "w") as token:
                token.write(creds.to_json())
        return creds

    def search_mail(self, creds):

        try:
            # Call the Gmail API
            service = build("gmail", "v1", credentials=creds)
            results = service.users().messages().list(userId="me",
                                                      maxResults=36 if self.result_num is None else self.result_num,
                                                      q=f"from:{self.address} "
                                                        f"after:{self.date_range[0]} "
                                                        f"before:{self.date_range[1]}").execute()
            # make it dict to take always the update bill
            date_attachment_dict = {}
            for message in results['messages']:

                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                # get the subject and the date
                # print(msg['payload']['parts'])

                # Check for attachments pdf files and if it contains the key_word
                for part in msg['payload']['parts']:
                    if part['filename'] and part['filename'].endswith('.pdf'):
                        for header in msg['payload']['headers']:
                            if header['name'] == 'Subject':
                                email_subject = header['value']
                                if self.key_word is None or self.key_word in email_subject:
                                    attachment_data = part['body']['attachmentId']
                                    attachment = service.users().messages().attachments() \
                                        .get(userId='me', messageId=message['id'], id=attachment_data).execute()
                                    data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                                    if header['name'] == 'Date':
                                        date_time_list = header['value'].split(' ')
                                        date_time = f"{date_time_list[1]}/{date_time_list[2]}/{date_time_list[3]}"
                                        # print(datetime.strptime(date_time, "%d/%b/%Y").date().strftime("%d/%m/%Y"))
                                        date = parse_date(parse_date(date_time, True, "%d/%b/%Y").date(), False,
                                                          "%d/%m/%Y")
                                        print(date)
                                        date_attachment_dict[date] = data
            return date_attachment_dict
        except HttpError as error:
            print(f"An error occurred: {error}")
