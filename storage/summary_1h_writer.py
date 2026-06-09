import os

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


def get_spreadsheet():
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

    return client.open_by_key(sheet_id)


def get_or_create_worksheet(spreadsheet):
    try:
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)

    except Exception:
        worksheet = spreadsheet.add_worksheet(
            title=WORKSHEET_NAME,
            rows=1000,
            cols=len(HEADERS),
        )

        worksheet.append_row(HEADERS)

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

    worksheet.append_row(row)

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

    print("Summary 1H writer dry-run OK")
