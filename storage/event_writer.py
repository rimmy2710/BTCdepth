import time

from storage.sheets_writer import get_sheet


SHEET_NAME = "05_event_database"

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


def get_event_worksheet():
    spreadsheet = get_sheet()

    return retry_google_sheets_operation(
        lambda: spreadsheet.worksheet(SHEET_NAME),
        f"open worksheet {SHEET_NAME}",
    )


def write_events(events):
    if not events:
        print("No events detected")
        return

    worksheet = get_event_worksheet()

    rows = []

    for event in events:
        rows.append([
            event["event_id"],
            event["snapshot_bucket"],
            event["event_time"],
            event["event_type"],
            event["event_group"],
            event["btc_price"],
            event["depth_ratio"],
            event["total_volume_usd"],
            event["event_strength"],
            event["event_description"],
            event["status"],
            event["source"],
        ])

    retry_google_sheets_operation(
        lambda: worksheet.append_rows(rows),
        f"append {len(rows)} events to {SHEET_NAME}",
    )

    print(f"Events written to Google Sheets: {len(rows)}")