from datetime import datetime, timezone


def build_event_id(snapshot_bucket, event_type):
    safe_time = (
        snapshot_bucket
        .replace("-", "")
        .replace(":", "")
        .replace("+00:00", "")
        .replace("T", "_")
    )

    return f"EVT_{safe_time}_{event_type}"


def detect_depth_events(summary):
    events = []

    depth_ratio = summary.get("depth_ratio")

    if depth_ratio is None:
        return events

    snapshot_bucket = summary.get("snapshot_bucket")
    event_time = summary.get("timestamp")

    base_event = {
        "snapshot_bucket": snapshot_bucket,
        "event_time": event_time,
        "event_group": "DEPTH",
        "btc_price": summary.get("btc_price"),
        "depth_ratio": depth_ratio,
        "total_volume_usd": summary.get("total_volume_usd"),
        "status": "OPEN",
        "source": summary.get("source", "CoinGecko"),
    }

    if depth_ratio <= 0.5:
        event_type = "DEPTH_SELL_EXTREME"
        events.append({
            **base_event,
            "event_id": build_event_id(snapshot_bucket, event_type),
            "event_type": event_type,
            "event_strength": "EXTREME",
            "event_description": "Depth ratio <= 0.5. Strong sell-side liquidity imbalance.",
        })

    elif depth_ratio <= 0.7:
        event_type = "DEPTH_SELL_IMBALANCE"
        events.append({
            **base_event,
            "event_id": build_event_id(snapshot_bucket, event_type),
            "event_type": event_type,
            "event_strength": "MEDIUM",
            "event_description": "Depth ratio <= 0.7. Sell-side liquidity pressure is stronger.",
        })

    if depth_ratio >= 1.5:
        event_type = "DEPTH_BUY_EXTREME"
        events.append({
            **base_event,
            "event_id": build_event_id(snapshot_bucket, event_type),
            "event_type": event_type,
            "event_strength": "EXTREME",
            "event_description": "Depth ratio >= 1.5. Strong buy-side liquidity imbalance.",
        })

    elif depth_ratio >= 1.3:
        event_type = "DEPTH_BUY_IMBALANCE"
        events.append({
            **base_event,
            "event_id": build_event_id(snapshot_bucket, event_type),
            "event_type": event_type,
            "event_strength": "MEDIUM",
            "event_description": "Depth ratio >= 1.3. Buy-side liquidity pressure is stronger.",
        })

    return events


def detect_events(summary):
    events = []

    events.extend(detect_depth_events(summary))

    return events