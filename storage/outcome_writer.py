import time

from storage.sheets_writer import get_sheet


SHEET_NAME = "06_outcome_database"

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


def get_outcome_worksheet():
    spreadsheet = get_sheet()

    return retry_google_sheets_operation(
        lambda: spreadsheet.worksheet(SHEET_NAME),
        f"open worksheet {SHEET_NAME}",
    )


def write_outcomes(outcomes):
    if not outcomes:
        print("No outcomes to write")
        return

    worksheet = get_outcome_worksheet()

    rows = []

    for outcome in outcomes:
        rows.append([
            outcome["outcome_id"],
            outcome["event_id"],
            outcome["event_type"],
            outcome["snapshot_bucket"],
            outcome["event_time"],
            outcome["price_at_event"],
            outcome["check_time"],
            outcome["horizon"],
            outcome["price_after"],
            outcome["price_change_pct"],
            outcome["outcome_status"],
            outcome["source"],
        ])

    retry_google_sheets_operation(
        lambda: worksheet.append_rows(rows),
        f"append {len(rows)} outcomes to {SHEET_NAME}",
    )

    print(f"Outcomes written to Google Sheets: {len(rows)}")