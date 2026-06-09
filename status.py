from datetime import datetime, timezone

from gspread.exceptions import WorksheetNotFound

from storage.sheets_writer import get_sheet


RAW_SHEET = "01_raw_market"
EXCHANGE_DEPTH_SHEET = "02_exchange_depth"
SUMMARY_1H_SHEET = "summary_1h"
SUMMARY_4H_SHEET = "summary_4h"


def get_worksheet_safe(spreadsheet, worksheet_name):
    try:
        return spreadsheet.worksheet(worksheet_name)
    except WorksheetNotFound:
        return None


def get_records_safe(worksheet):
    if worksheet is None:
        return []

    return worksheet.get_all_records()


def get_last_record(records):
    if not records:
        return None

    return records[-1]


def calculate_age_minutes(timestamp_str):
    timestamp = datetime.fromisoformat(timestamp_str)

    now = datetime.now(timezone.utc)

    delta = now - timestamp

    return round(delta.total_seconds() / 60, 2)


def get_system_health(age_minutes):
    if age_minutes is None:
        return "UNKNOWN"

    if age_minutes < 20:
        return "HEALTHY"

    if age_minutes < 45:
        return "WARNING"

    return "CRITICAL"


def print_sheet_status(name, worksheet, records):
    if worksheet is None:
        print(f"{name}: MISSING")
    else:
        print(f"{name}: OK ({len(records)} rows)")


def main():
    spreadsheet = get_sheet()

    raw_ws = get_worksheet_safe(spreadsheet, RAW_SHEET)
    exchange_depth_ws = get_worksheet_safe(spreadsheet, EXCHANGE_DEPTH_SHEET)
    summary_1h_ws = get_worksheet_safe(spreadsheet, SUMMARY_1H_SHEET)
    summary_4h_ws = get_worksheet_safe(spreadsheet, SUMMARY_4H_SHEET)

    raw_records = get_records_safe(raw_ws)
    exchange_depth_records = get_records_safe(exchange_depth_ws)
    summary_1h_records = get_records_safe(summary_1h_ws)
    summary_4h_records = get_records_safe(summary_4h_ws)

    last_raw = get_last_record(raw_records)

    age_minutes = None
    health = "UNKNOWN"

    latest_price = None
    latest_depth_ratio = None
    latest_total_volume = None

    if last_raw:
        age_minutes = calculate_age_minutes(last_raw["timestamp"])
        health = get_system_health(age_minutes)

        latest_price = last_raw.get("btc_price")
        latest_depth_ratio = last_raw.get("depth_ratio")
        latest_total_volume = last_raw.get("total_volume_usd")

    print()
    print("====================================")
    print("BTC LIQUIDITY SYSTEM STATUS")
    print("====================================")
    print()

    print("Google Sheets")
    print("-------------")
    print_sheet_status(RAW_SHEET, raw_ws, raw_records)
    print_sheet_status(EXCHANGE_DEPTH_SHEET, exchange_depth_ws, exchange_depth_records)
    print_sheet_status(SUMMARY_1H_SHEET, summary_1h_ws, summary_1h_records)
    print_sheet_status(SUMMARY_4H_SHEET, summary_4h_ws, summary_4h_records)

    print()

    print("Data Freshness")
    print("--------------")

    if last_raw:
        print(f"Last Raw Snapshot: {last_raw['timestamp']}")
        print(f"Minutes Ago:       {age_minutes}")
    else:
        print("Last Raw Snapshot: NONE")
        print("Minutes Ago:       N/A")

    print()

    print("Latest Market")
    print("-------------")
    print(f"BTC Price:          {latest_price}")
    print(f"Depth Ratio:        {latest_depth_ratio}")
    print(f"Total Volume:       {latest_total_volume}")

    print()

    print("System Status")
    print("-------------")
    print(health)

    print()
    print("====================================")


if __name__ == "__main__":
    main()