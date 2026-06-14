import os
import time

import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials


SHEET_NAME = "01_raw_market"

MAX_RETRIES = 5
RETRY_DELAY_SECONDS = 5


def retry_google_sheets_operation(operation, action_name):
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return operation()

        except Exception as error:
            last_error = error
            print(
                f"[Google Sheets Retry] {action_name} failed "
                f"(attempt {attempt}/{MAX_RETRIES}): {error}"
            )

            if attempt < MAX_RETRIES:
                sleep_seconds = RETRY_DELAY_SECONDS * attempt
                print(f"Retrying in {sleep_seconds} seconds...")
                time.sleep(sleep_seconds)

    raise RuntimeError(
        f"Google Sheets operation failed after {MAX_RETRIES} retries: {action_name}"
    ) from last_error


def get_worksheet():
    load_dotenv()

    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    credentials_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

    if not sheet_id:
        raise ValueError("Missing GOOGLE_SHEET_ID")

    if not credentials_path:
        raise ValueError("Missing GOOGLE_SERVICE_ACCOUNT_JSON")

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        credentials_path,
        scope,
    )

    client = gspread.authorize(creds)

    spreadsheet = retry_google_sheets_operation(
        lambda: client.open_by_key(sheet_id),
        "open spreadsheet",
    )

    return retry_google_sheets_operation(
        lambda: spreadsheet.worksheet(SHEET_NAME),
        f"open worksheet {SHEET_NAME}",
    )


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

    retry_google_sheets_operation(
        lambda: worksheet.append_row(row),
        f"append market snapshot to {SHEET_NAME}",
    )

    print("Market snapshot written to Google Sheets")