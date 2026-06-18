from datetime import datetime, timezone
import time

from storage.sheets_writer import get_sheet


SHEET_NAME = "00_system_run_log"

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


def build_run_id():
    return "RUN_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def get_run_log_worksheet():
    spreadsheet = get_sheet()

    return retry_google_sheets_operation(
        lambda: spreadsheet.worksheet(SHEET_NAME),
        f"open worksheet {SHEET_NAME}",
    )


def write_run_log(log):
    worksheet = get_run_log_worksheet()

    row = [
        log.get("run_id") or build_run_id(),
        log.get("run_time") or datetime.now(timezone.utc).isoformat(),
        log.get("status"),
        log.get("raw_written"),
        log.get("exchange_rows_written"),
        log.get("events_written"),
        log.get("alert_sent"),
        log.get("error_type"),
        log.get("error_message"),
        log.get("source"),
    ]

    retry_google_sheets_operation(
        lambda: worksheet.append_row(row),
        f"append run log to {SHEET_NAME}",
    )

    print("System run log written")