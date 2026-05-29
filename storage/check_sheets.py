import os
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials


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


def main():
    spreadsheet = get_spreadsheet()

    existing_titles = [ws.title for ws in spreadsheet.worksheets()]

    print("Existing sheets:")
    for title in existing_titles:
        print(f"- {title}")

    target_sheet = "01_raw_market"

    if target_sheet not in existing_titles:
        worksheet = spreadsheet.add_worksheet(
            title=target_sheet,
            rows=1000,
            cols=20,
        )

        headers = [
            "timestamp",
            "btc_price",
            "total_volume_usd",
            "total_depth_up_usd",
            "total_depth_down_usd",
            "depth_ratio",
            "top_exchange",
            "source",
        ]

        worksheet.append_row(headers)

        print(f"Created sheet: {target_sheet}")
        print("Headers added.")
    else:
        print(f"Sheet already exists: {target_sheet}")


if __name__ == "__main__":
    main()
