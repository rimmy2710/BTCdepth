from typing import Any, Dict, List, Optional


REQUIRED_SNAPSHOT_COUNT = 16


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


def calculate_price_change(open_price: float, close_price: float) -> float:
    return round(close_price - open_price, 4)


def calculate_price_change_pct(open_price: float, close_price: float) -> Optional[float]:
    if open_price == 0:
        return None

    return round(((close_price - open_price) / open_price) * 100, 4)


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


def build_summary_4h(snapshots: List[Dict[str, Any]]) -> Dict[str, Any]:
    if len(snapshots) < REQUIRED_SNAPSHOT_COUNT:
        raise ValueError(
            f"Need at least {REQUIRED_SNAPSHOT_COUNT} snapshots for 4H summary"
        )

    selected_snapshots = snapshots[-REQUIRED_SNAPSHOT_COUNT:]

    first_snapshot = selected_snapshots[0]
    last_snapshot = selected_snapshots[-1]

    prices = [safe_float(item.get("btc_price")) for item in selected_snapshots]
    volumes = [safe_float(item.get("total_volume_usd")) for item in selected_snapshots]
    depth_ratios = [safe_float(item.get("depth_ratio")) for item in selected_snapshots]

    open_price = prices[0]
    close_price = prices[-1]
    high_price = max(prices)
    low_price = min(prices)

    avg_volume_usd = calculate_average(volumes)
    avg_depth_ratio = calculate_average(depth_ratios)

    price_change = calculate_price_change(open_price, close_price)
    price_change_pct = calculate_price_change_pct(open_price, close_price)

    market_bias = classify_market_bias(
        price_change=price_change,
        avg_depth_ratio=avg_depth_ratio,
    )

    return {
        "start_timestamp": first_snapshot.get("timestamp"),
        "end_timestamp": last_snapshot.get("timestamp"),
        "snapshot_count": len(selected_snapshots),
        "open_price": open_price,
        "close_price": close_price,
        "high_price": high_price,
        "low_price": low_price,
        "price_change": price_change,
        "price_change_pct": price_change_pct,
        "avg_volume_usd": avg_volume_usd,
        "avg_depth_ratio": avg_depth_ratio,
        "market_bias": market_bias,
    }


if __name__ == "__main__":
    sample_snapshots = []

    for index in range(16):
        sample_snapshots.append(
            {
                "timestamp": f"2026-06-09T{index:02d}:00:00+00:00",
                "btc_price": 62000 + (index * 100),
                "total_volume_usd": 4800000000 + (index * 10000000),
                "depth_ratio": 0.75 + (index * 0.01),
            }
        )

    summary = build_summary_4h(sample_snapshots)

    assert summary["snapshot_count"] == 16
    assert summary["open_price"] == 62000
    assert summary["close_price"] == 63500
    assert summary["high_price"] == 63500
    assert summary["low_price"] == 62000
    assert summary["price_change"] == 1500
    assert summary["price_change_pct"] == 2.4194
    assert summary["avg_depth_ratio"] == 0.825

    print("Summary 4H engine dry-run OK")
    print(f"Snapshot count: {summary['snapshot_count']}")
    print(f"Market bias: {summary['market_bias']}")
