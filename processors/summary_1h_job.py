from storage.market_writer import get_worksheet
from storage.summary_1h_writer import write_summary_1h
from processors.summary_1h_engine import build_summary_1h


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
            and top_exchange in {"Binance", "Bybit", "Coinbase Exchange", "OKX", "Gate"}
            and btc_price is not None
            and total_volume_usd is not None
            and depth_ratio is not None
        )

    except Exception:
        return False


def read_valid_raw_snapshots():
    worksheet = get_worksheet()
    records = worksheet.get_all_records()

    valid_rows = []

    for row in records:
        if not is_valid_raw_row(row):
            continue

        valid_rows.append(
            {
                "timestamp": row["timestamp"],
                "btc_price": parse_number(row["btc_price"]),
                "total_volume_usd": parse_number(row["total_volume_usd"]),
                "depth_ratio": parse_number(row["depth_ratio"]),
            }
        )

    return valid_rows


def run_summary_1h_job():
    snapshots = read_valid_raw_snapshots()

    print(f"Valid raw snapshots found: {len(snapshots)}")

    if len(snapshots) < 4:
        raise ValueError("Need at least 4 valid raw snapshots to build summary_1h")

    summary = build_summary_1h(snapshots)

    write_summary_1h(summary)

    print("Summary 1H job completed successfully")
    print(f"Snapshot count: {summary['snapshot_count']}")
    print(f"Market bias: {summary['market_bias']}")

    return summary


if __name__ == "__main__":
    run_summary_1h_job()