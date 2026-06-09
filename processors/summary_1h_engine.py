from typing import Any, Dict, List, Optional


REQUIRED_SNAPSHOT_COUNT = 4


def safe_float(value: Any) -> float:
    if value is None:
        return 0.0

    if value == "":
        return 0.0

    return float(value)


def calculate_average(values: List[float]) -> Optional[float]:
    if not values:
        return None

    return round(sum(values) / len(values), 4)


def calculate_price_change(first_price: float, last_price: float) -> float:
    return round(last_price - first_price, 4)


def calculate_price_change_pct(first_price: float, last_price: float) -> Optional[float]:
    if first_price == 0:
        return None

    return round(((last_price - first_price) / first_price) * 100, 4)


def classify_market_bias(
    price_change: float,
    avg_depth_ratio: Optional[float],
) -> str:
    if avg_depth_ratio is None:
        return "UNKNOWN"

    if price_change > 0 and avg_depth_ratio >= 1.2:
        return "BULLISH_LIQUIDITY"

    if price_change < 0 and avg_depth_ratio <= 0.8:
        return "BEARISH_LIQUIDITY"

    if avg_depth_ratio > 1.2:
        return "BUY_DEPTH_STRONG"

    if avg_depth_ratio < 0.8:
        return "SELL_DEPTH_STRONG"

    return "NEUTRAL"


def build_summary_1h(snapshots: List[Dict[str, Any]]) -> Dict[str, Any]:
    if len(snapshots) < REQUIRED_SNAPSHOT_COUNT:
        raise ValueError(
            f"Need at least {REQUIRED_SNAPSHOT_COUNT} snapshots for 1H summary"
        )

    selected_snapshots = snapshots[-REQUIRED_SNAPSHOT_COUNT:]

    first_snapshot = selected_snapshots[0]
    last_snapshot = selected_snapshots[-1]

    prices = [safe_float(item.get("btc_price")) for item in selected_snapshots]
    volumes = [safe_float(item.get("total_volume_usd")) for item in selected_snapshots]
    depth_ratios = [safe_float(item.get("depth_ratio")) for item in selected_snapshots]

    first_price = prices[0]
    last_price = prices[-1]

    avg_price = calculate_average(prices)
    avg_volume_usd = calculate_average(volumes)
    avg_depth_ratio = calculate_average(depth_ratios)

    price_change = calculate_price_change(first_price, last_price)
    price_change_pct = calculate_price_change_pct(first_price, last_price)

    market_bias = classify_market_bias(
        price_change=price_change,
        avg_depth_ratio=avg_depth_ratio,
    )

    return {
        "start_timestamp": first_snapshot.get("timestamp"),
        "end_timestamp": last_snapshot.get("timestamp"),
        "snapshot_count": len(selected_snapshots),
        "avg_price": avg_price,
        "price_change": price_change,
        "price_change_pct": price_change_pct,
        "avg_volume_usd": avg_volume_usd,
        "avg_depth_ratio": avg_depth_ratio,
        "market_bias": market_bias,
    }


if __name__ == "__main__":
    sample_snapshots = [
        {
            "timestamp": "2026-06-09T00:00:00+00:00",
            "btc_price": 62000,
            "total_volume_usd": 4800000000,
            "depth_ratio": 0.75,
        },
        {
            "timestamp": "2026-06-09T00:15:00+00:00",
            "btc_price": 62200,
            "total_volume_usd": 4850000000,
            "depth_ratio": 0.80,
        },
        {
            "timestamp": "2026-06-09T00:30:00+00:00",
            "btc_price": 62400,
            "total_volume_usd": 4900000000,
            "depth_ratio": 0.85,
        },
        {
            "timestamp": "2026-06-09T00:45:00+00:00",
            "btc_price": 62600,
            "total_volume_usd": 4950000000,
            "depth_ratio": 0.90,
        },
    ]

    summary = build_summary_1h(sample_snapshots)

    assert summary["snapshot_count"] == 4
    assert summary["avg_price"] == 62300
    assert summary["price_change"] == 600
    assert summary["price_change_pct"] == 0.9677
    assert summary["avg_volume_usd"] == 4875000000
    assert summary["avg_depth_ratio"] == 0.825

    print("Summary 1H engine dry-run OK")
    print(f"Snapshot count: {summary['snapshot_count']}")
    print(f"Market bias: {summary['market_bias']}")
