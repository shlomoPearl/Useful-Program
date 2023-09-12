from __future__ import print_function

import base64
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
from ElectricBill.bill import read_bill

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
global count
count = 0


def connect_to_gmail():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def search_mail(mail_address):
    query = f"from:{mail_address}"
    creds = connect_to_gmail()
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', q=query).execute()
        if 'messages' in results:
            for message in results['messages']:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                email_subject = ""
                for header in msg['payload']['headers']:
                    if header['name'] == 'Subject':
                        email_subject = header['value']
                        break
                date = ""
                for char in email_subject:
                    if char.isdigit() or char == '/':
                        date += char
                # Check for attachments
                for part in msg['payload']['parts']:
                    if part['filename'] and part['filename'].endswith('.pdf'):
                        attachment_data = part['body']['attachmentId']
                        attachment = service.users().messages().attachments().get(
                            userId='me', messageId=message['id'], id=attachment_data).execute()
                        data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                        # Now you can save or process the PDF file
                        with open('attachment.pdf', 'wb') as f:
                            f.write(data)
                        read_bill('attachment.pdf', date)
                        # You can read the PDF content using a PDF parsing library here
    except HttpError as error:
        print(f'An error occurred: {error}')


def main():
    search_mail("gviyarevava@revava.co.il")


if __name__ == '__main__':
    main()
