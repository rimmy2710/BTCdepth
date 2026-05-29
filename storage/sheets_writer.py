import os
from dotenv import load_dotenv

import gspread
from oauth2client.service_account import ServiceAccountCredentials


def get_sheet():
    load_dotenv()

    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    credentials_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        credentials_path,
        scope,
    )

    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(sheet_id)

    return spreadsheet


def test_write():
    spreadsheet = get_sheet()

    worksheet = spreadsheet.worksheet("01_raw_market")

    worksheet.append_row(
        [
            "TEST",
            100000,
            999999999,
            50000000,
            40000000,
            1.25,
        ]
    )

    print("Google Sheets write test: SUCCESS")


if __name__ == "__main__":
    test_write()

