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


def parse_date(date_str, strp, date_format):
    if strp:  # '%d/%m/%Y'
        return datetime.strptime(date_str, date_format)
    else:
        return datetime.strftime(date_str, date_format)


def increment_date(date_str):
    date_object = datetime.strptime(date_str, '%d/%m/%Y')
    day_obj = date_object.day
    month_obj = date_object.month
    next_month = (month_obj + 1) % 12 if (month_obj + 1) % 12 > 0 else 12
    year_obj = date_object.year
    num_day_current = calendar.monthrange(year_obj, month_obj)[1]
    num_day_next = calendar.monthrange(year_obj, next_month)[1]
    new_date = date_object + timedelta(days=num_day_next if day_obj == num_day_current else num_day_current)
    new_date_str = new_date.strftime('%d/%m/%Y')
    return new_date_str


def decrement_date(date_str):
    date_object = datetime.strptime(date_str, '%d/%m/%Y')
    day_obj = date_object.day
    month_obj = date_object.month
    before_month = (month_obj - 1) % 12 if (month_obj - 1) % 12 > 0 else 12
    year_obj = date_object.year
    num_day_current = calendar.monthrange(year_obj, month_obj)[1]
    num_day_before = calendar.monthrange(year_obj, before_month)[1]
    new_date = date_object + timedelta(days=-(num_day_current if day_obj == num_day_current else num_day_before))
    new_date_str = new_date.strftime('%d/%m/%Y')
    return new_date_str


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
                                print(email_subject)
                            if header['name'] == 'Date':
                                date_time_list = header['value'].split(' ')
                                date_time = f"{date_time_list[1]}/{date_time_list[2]}/{date_time_list[3]}"
                                d_with_month_n = parse_date(date_time, True, "%d/%b/%Y").date()
                                s_d_with_month_n = parse_date(d_with_month_n, False, "%d/%m/%Y")
                                real_date_bill = decrement_date(s_d_with_month_n)
                                o_real_date_bill = parse_date(real_date_bill,True, "%d/%m/%Y")
                                date = parse_date(o_real_date_bill, False, "%m/%Y")
                                date_attachment_dict[date] = data
            return date_attachment_dict
        except HttpError as error:
            print(f"An error occurred: {error}")
