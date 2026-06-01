import os
from dotenv import load_dotenv

import gspread
from oauth2client.service_account import ServiceAccountCredentials


SHEET_NAME = "01_raw_market"


def get_worksheet():
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

    return spreadsheet.worksheet(SHEET_NAME)


def write_market_snapshot(summary):
    worksheet = get_worksheet()

    row = [
        summary["timestamp"],
        summary["btc_price"],
        summary["total_volume_usd"],
        summary["total_depth_up_usd"],
        summary["total_depth_down_usd"],
        summary["depth_ratio"],
        summary["top_exchange"],
    ]

    worksheet.append_row(row)

    print("Market snapshot written to Google Sheets")
