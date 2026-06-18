from datetime import datetime, timezone, timedelta

from storage.sheets_writer import get_sheet
from processors.outcome_engine import build_outcome_from_event
from storage.outcome_writer import write_outcomes


EVENT_SHEET = "05_event_database"
RAW_SHEET = "01_raw_market"
OUTCOME_SHEET = "06_outcome_database"

HORIZONS = {
    "1H": timedelta(hours=1),
    "4H": timedelta(hours=4),
    "24H": timedelta(hours=24),
}


def parse_dt(value):
    return datetime.fromisoformat(value)


def get_records(sheet_name):
    spreadsheet = get_sheet()
    worksheet = spreadsheet.worksheet(sheet_name)
    return worksheet.get_all_records()


def build_existing_outcome_keys(outcome_records):
    keys = set()

    for record in outcome_records:
        event_id = record.get("event_id")
        horizon = record.get("horizon")

        if event_id and horizon:
            keys.add((event_id, horizon))

    return keys


def find_nearest_raw_snapshot(raw_records, target_time):
    best_record = None
    best_diff = None

    for record in raw_records:
        snapshot_time = parse_dt(record["timestamp"])
        diff = abs((snapshot_time - target_time).total_seconds())

        if best_diff is None or diff < best_diff:
            best_diff = diff
            best_record = record

    return best_record


def build_summary_from_raw(raw_record):
    return {
        "timestamp": raw_record["timestamp"],
        "btc_price": raw_record["btc_price"],
        "source": raw_record.get("source") or "CoinGecko",
    }


def main():
    event_records = get_records(EVENT_SHEET)
    raw_records = get_records(RAW_SHEET)
    outcome_records = get_records(OUTCOME_SHEET)

    existing_outcome_keys = build_existing_outcome_keys(outcome_records)

    outcomes = []

    for event in event_records:
        if event.get("status") != "OPEN":
            continue

        event_time = parse_dt(event["event_time"])

        for horizon, delta in HORIZONS.items():
            outcome_key = (event["event_id"], horizon)

            if outcome_key in existing_outcome_keys:
                continue

            target_time = event_time + delta

            if datetime.now(timezone.utc) < target_time:
                continue

            raw_record = find_nearest_raw_snapshot(raw_records, target_time)

            if not raw_record:
                continue

            current_summary = build_summary_from_raw(raw_record)

            outcome = build_outcome_from_event(
                event=event,
                current_summary=current_summary,
                horizon=horizon,
            )

            outcomes.append(outcome)
            existing_outcome_keys.add(outcome_key)

    write_outcomes(outcomes)


if __name__ == "__main__":
    main()