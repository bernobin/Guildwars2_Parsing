from __future__ import print_function

import os.path
import csv
import pathlib

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
# https://developers.google.com/identity/protocols/oauth2/scopes?hl=de
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
# https://docs.google.com/spreadsheets/d/1Eexwq48s_lpd88N0puwF0vUyF_RCmZQbZzU7wWiTP1c/edit?usp=sharing
CND_SPREADSHEET_ID = '1Eexwq48s_lpd88N0puwF0vUyF_RCmZQbZzU7wWiTP1c'
AVES_SPREADSHEET_ID = '1UkGLkimQY_csoNbdBtmfGlcyEdtrpHX286_5YVLdRxI'
path_creds = pathlib.Path("C:/Users/berno/Documents/Python Scripts/Guildwars_2_Parsing/credentials.json")
path_token = pathlib.Path('C:/Users/berno/Documents/Python Scripts/Guildwars_2_Parsing/token.json')


def get_creds():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(path_token):
        creds = Credentials.from_authorized_user_file(str(path_token), SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(path_creds), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(path_token, 'w') as token:
            token.write(creds.to_json())
    return creds


def update_sheet(creds, spreadsheet_id, spreadsheet_range, values):
    try:
        service = build('sheets', 'v4', credentials=creds)

        value_range = {
            'range': spreadsheet_range,
            'majorDimension': 'ROWS',
            'values': values,
        }

        # update the entries
        sheet = service.spreadsheets()
        sheet.values().update(spreadsheetId=spreadsheet_id,
                              range=spreadsheet_range,
                              valueInputOption='RAW',
                              body=value_range).execute()

    except HttpError as err:
        print(err)

    pass


def csv_to_googlesheet(boss_name, SPREADSHEET_ID=CND_SPREADSHEET_ID):
    values = []
    with open(boss_name + '.csv', 'r') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if len(row) > 0:
                values.append(row)

    #range can be larger than data
    sheet_range = boss_name + '!A:XX'

    creds = get_creds()
    update_sheet(creds, SPREADSHEET_ID, sheet_range, values)
    pass


if __name__ == '__main__':
    csv_to_googlesheet('Samarog/Samarog.csv', CND_SPREADSHEET_ID)

