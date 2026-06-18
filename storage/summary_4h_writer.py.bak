import os

import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials


WORKSHEET_NAME = "summary_4h"

HEADERS = [
    "start_timestamp",
    "end_timestamp",
    "snapshot_count",
    "open_price",
    "close_price",
    "high_price",
    "low_price",
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


def write_summary_4h(summary):
    spreadsheet = get_spreadsheet()

    worksheet = get_or_create_worksheet(spreadsheet)

    row = [
        summary["start_timestamp"],
        summary["end_timestamp"],
        summary["snapshot_count"],
        summary["open_price"],
        summary["close_price"],
        summary["high_price"],
        summary["low_price"],
        summary["price_change"],
        summary["price_change_pct"],
        summary["avg_volume_usd"],
        summary["avg_depth_ratio"],
        summary["market_bias"],
    ]

    worksheet.append_row(row)

    print("Summary 4H written to Google Sheets")


if __name__ == "__main__":
    sample_summary = {
        "start_timestamp": "2026-06-09T00:00:00+00:00",
        "end_timestamp": "2026-06-09T04:00:00+00:00",
        "snapshot_count": 16,
        "open_price": 62000,
        "close_price": 63500,
        "high_price": 63500,
        "low_price": 62000,
        "price_change": 1500,
        "price_change_pct": 2.4194,
        "avg_volume_usd": 4875000000,
        "avg_depth_ratio": 0.825,
        "market_bias": "NEUTRAL",
    }

    print("Summary 4H writer dry-run OK")
