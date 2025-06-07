from __future__ import print_function
import base64
import os.path
from datetime import datetime, timedelta
import calendar
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.


# Convert date from dd/mm/yyyy format to yyyy/mm/dd format with month +1
def increment_date(date_str):
    date_obj = datetime.strptime(date_str, '%d/%m/%Y')
    month = date_obj.month + 1
    year = date_obj.year
    day = date_obj.day
    if month > 12:
        month = 1
        year += 1
    return f"{year:04d}/{month:02d}/{day:02d}"


# Extract date from list format and return as mm/yyyy with month -1
def decrement_date(date_list):
    month_name = date_list[2]  # 'Mar'
    year = date_list[3]  # '2024'
    month_dict = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    month_num = month_dict[month_name] - 1
    year_num = int(year)
    if month_num < 1:
        month_num = 12
        year_num -= 1
    return f"{month_num:02d}/{year_num}"


class Gmail:

    def __init__(self, address=None, subject=None, filename='pdf', key_word=None, result_num=36, date_range=[]):
        self.address = address
        self.subject = subject
        self.filename = filename
        self.key_word = key_word
        self.result_num = result_num
        self.date_range = date_range
        # self.date_range = [parse_date(date_range[0], True, '%d/%m/%Y').isoformat() + 'Z',
        #                    (parse_date(date_range[1], True, '%d/%m/%Y') + timedelta(days=1)).isoformat() + 'Z']
        self.token_file = "token.json"
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        self.credentials = "credentials.json"

    def authenticate(self):
        creds = None
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials, self.SCOPES,
                )
                flow.redirect_uri = 'http://localhost:5000/'
                creds = flow.run_local_server(port=5000)

            with open(self.token_file, "w") as token:
                token.write(creds.to_json())
        print("The authentication was successful")
        return creds

    def search_mail(self, creds):
        query = f"from:{self.address} subject:{self.subject} filename:{self.filename}" \
                f" after:{increment_date(self.date_range[0])} before:{increment_date(self.date_range[1])}"
        print(query)
        try:
            # Call the Gmail API
            service = build("gmail", "v1", credentials=creds)
            results = service.users().messages().list(userId="me", maxResults=self.result_num, q=query).execute()
            # make it dict to take always the update bill
            date_attachment_dict = {}
            for message in results['messages']:

                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                # get the subject and the date
                # Check for attachments pdf files and if it contains the key_word
                for part in msg['payload']['parts']:
                    if part['filename'] and part['filename'].endswith('.pdf'):
                        attachment_data = part['body']['attachmentId']
                        attachment = service.users().messages().attachments() \
                            .get(userId='me', messageId=message['id'], id=attachment_data).execute()
                        data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                        for header in msg['payload']['headers']:
                            if header['name'] == 'Subject':
                                email_subject = header['value']
                                # if self.key_word is None or self.key_word in email_subject:
                                #     continue
                            if header['name'] == 'Date':
                                date_time_list = header['value'].split(' ')
                                date = decrement_date(date_time_list)
                                date_attachment_dict[date] = data
            # print("date attachment dict:", date_attachment_dict)
            return date_attachment_dict
        except HttpError as error:
            print(f"An error occurred: {error}")
