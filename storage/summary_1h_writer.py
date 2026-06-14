import os
import time

import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials


WORKSHEET_NAME = "summary_1h"

HEADERS = [
    "start_timestamp",
    "end_timestamp",
    "snapshot_count",
    "avg_price",
    "price_change",
    "price_change_pct",
    "avg_volume_usd",
    "avg_depth_ratio",
    "market_bias",
]

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


def get_spreadsheet():
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

    return retry_google_sheets_operation(
        lambda: client.open_by_key(sheet_id),
        "open spreadsheet",
    )


def get_or_create_worksheet(spreadsheet):
    try:
        return retry_google_sheets_operation(
            lambda: spreadsheet.worksheet(WORKSHEET_NAME),
            f"open worksheet {WORKSHEET_NAME}",
        )

    except Exception:
        worksheet = retry_google_sheets_operation(
            lambda: spreadsheet.add_worksheet(
                title=WORKSHEET_NAME,
                rows=1000,
                cols=len(HEADERS),
            ),
            f"create worksheet {WORKSHEET_NAME}",
        )

        retry_google_sheets_operation(
            lambda: worksheet.append_row(HEADERS),
            f"write headers to {WORKSHEET_NAME}",
        )

        return worksheet


def write_summary_1h(summary):
    spreadsheet = get_spreadsheet()
    worksheet = get_or_create_worksheet(spreadsheet)

    row = [
        summary["start_timestamp"],
        summary["end_timestamp"],
        summary["snapshot_count"],
        summary["avg_price"],
        summary["price_change"],
        summary["price_change_pct"],
        summary["avg_volume_usd"],
        summary["avg_depth_ratio"],
        summary["market_bias"],
    ]

    retry_google_sheets_operation(
        lambda: worksheet.append_row(row),
        f"append summary row to {WORKSHEET_NAME}",
    )

    print("Summary 1H written to Google Sheets")


if __name__ == "__main__":
    sample_summary = {
        "start_timestamp": "2026-06-09T00:00:00+00:00",
        "end_timestamp": "2026-06-09T01:00:00+00:00",
        "snapshot_count": 4,
        "avg_price": 62300,
        "price_change": 600,
        "price_change_pct": 0.9677,
        "avg_volume_usd": 4875000000,
        "avg_depth_ratio": 0.825,
        "market_bias": "NEUTRAL",
    }

    write_summary_1h(sample_summary)