from storage.market_writer import get_worksheet
from storage.summary_4h_writer import write_summary_4h
from processors.summary_4h_engine import build_summary_4h


VALID_EXCHANGES = {
    "Binance",
    "Bybit",
    "Coinbase Exchange",
    "OKX",
    "Gate",
}


def parse_number(value):
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    cleaned = str(value).strip()
    cleaned = cleaned.replace("$", "")
    cleaned = cleaned.replace(",", "")

    if cleaned == "":
        return None

    return float(cleaned)


def is_valid_raw_row(row):
    try:
        timestamp = row.get("timestamp")
        btc_price = parse_number(row.get("btc_price"))
        total_volume_usd = parse_number(row.get("total_volume_usd"))
        depth_ratio = parse_number(row.get("depth_ratio"))
        top_exchange = row.get("top_exchange")

        return (
            timestamp
            and timestamp != "TEST"
            and top_exchange in VALID_EXCHANGES
            and btc_price is not None
            and total_volume_usd is not None
            and depth_ratio is not None
        )

    except Exception:
        return False


def read_valid_raw_snapshots():
    worksheet = get_worksheet()

    records = worksheet.get_all_records()

    snapshots = []

    for row in records:
        if not is_valid_raw_row(row):
            continue

        snapshots.append(
            {
                "timestamp": row["timestamp"],
                "btc_price": parse_number(row["btc_price"]),
                "total_volume_usd": parse_number(row["total_volume_usd"]),
                "depth_ratio": parse_number(row["depth_ratio"]),
            }
        )

    return snapshots


def run_summary_4h_job():
    snapshots = read_valid_raw_snapshots()

    print(f"Valid raw snapshots found: {len(snapshots)}")

    if len(snapshots) < 16:
        raise ValueError(
            "Need at least 16 valid raw snapshots to build summary_4h"
        )

    summary = build_summary_4h(snapshots)

    write_summary_4h(summary)

    print("Summary 4H job completed successfully")
    print(f"Snapshot count: {summary['snapshot_count']}")
    print(f"Market bias: {summary['market_bias']}")

    return summary


if __name__ == "__main__":
    run_summary_4h_job()
