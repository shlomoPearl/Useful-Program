import PyPDF2
from io import BytesIO
import base64
import os.path
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
address_search = "gviyarevava@revava.co.il"


def parse_date(date_str, strp, date_format):
    if strp:  # '%d/%m/%Y'
        return datetime.strptime(date_str, date_format)
    else:
        return date_str.strftime(date_format)


def main():
    """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId="me", maxResults=2 if None is None else 4,
                                                  q=f"from:{address_search} "
                                                    f"after:01/04/2024 "
                                                    f"before:30/04/2024"
                                                  ).execute()
        for message in results['messages']:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()

            # get the subject and the date
            # print(msg['payload']['parts'])
            # Check for attachments
            # print(msg['payload']['parts'])
            for part in msg['payload']['parts']:
                if part['filename'] and part['filename'].endswith('.pdf'):
                    attachment_data = part['body']['attachmentId']
                    attachment = service.users().messages().attachments() \
                        .get(userId='me', messageId=message['id'], id=attachment_data).execute()
                    data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                    data = BytesIO(data)
                    pdf_file = PyPDF2.PdfReader(data)

                    # Read each page and extract text line by line
                    for page in pdf_file.pages:
                        text = page.extract_text()
                        lines = text.split('\n')
                        for line in lines:
                            line = line.split(' ')
                            line.reverse()
                            # print(line)
                    for header in msg['payload']['headers']:
                        if header['name'] == 'Subject':
                            email_subject = header['value']
                            if 'מעון' in email_subject:
                                print("&&&&&&&&7")
                                # print("subject: ", email_subject)
                                # with open('attachment2.pdf', 'wb') as f:
                                #     f.write(data)
                        if header['name'] == 'Date':
                            date_time_list = header['value'].split(' ')
                            date_time = f"{date_time_list[1]}/{date_time_list[2]}/{date_time_list[3]}"
                            # print(datetime.strptime(date_time, "%d/%b/%Y").date().strftime("%d/%m/%Y"))
                            date = parse_date(parse_date(date_time, True, "%d/%b/%Y").date(), False, "%m/%Y")
                            print(date)
                            print(type(date))

        # print(results['messages'])


    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()


nis = "\u20AA"


def parse_bill(pageObj, ):
    electric = 0
    water = 0
    # extracting text from page
    bill_list = pageObj.extract_text().splitlines()
    for line in bill_list:
        if 'חשמל' in line.split(' '):
            electric_split = line.split(' ')
            # print(electric_split[0])
            # print(electric_split)
            for i, sign in enumerate(electric_split):
                # print(i, sign)
                if sign == nis and i < len(electric_split) - 1 and electric_split[i + 1].replace('.', '', 1).isdigit():
                    electric += float(electric_split[i + 1])
        if 'מים' in line.split(' '):
            water_split = line.split(' ')
            for i, sign in enumerate(water_split):
                if sign == nis and i < len(electric_split) - 1 and water_split[i + 1].replace('.', '', 1).isnumeric():
                    water += float(water_split[i + 1])
    return electric, water


def read_bill(file_name, date) -> dict:
    # creating a pdf file object
    pdfFileObj = open(file_name, 'rb')

    # creating a pdf reader object
    pdfReader = PyPDF2.PdfReader(pdfFileObj)

    # printing number of pages in pdf file
    tuple_bill = ()
    for i in range(len(pdfReader.pages)):
        pageObj = pdfReader.pages[i]
        tuple_bill = parse_bill(pageObj)
        if parse_bill(pageObj) != (0, 0):
            tuple_bill

    # closing the pdf file object
    pdfFileObj.close()
