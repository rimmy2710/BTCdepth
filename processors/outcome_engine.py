from datetime import datetime, timezone


def build_outcome_id(event_id, horizon):
    return f"OUT_{event_id}_{horizon}"


def calculate_price_change_pct(price_at_event, price_after):
    if not price_at_event:
        return None

    return round(((price_after - price_at_event) / price_at_event) * 100, 4)


def build_outcome_from_event(event, current_summary, horizon):
    price_at_event = event.get("btc_price")
    price_after = current_summary.get("btc_price")

    return {
        "outcome_id": build_outcome_id(event["event_id"], horizon),
        "event_id": event["event_id"],
        "event_type": event["event_type"],
        "snapshot_bucket": event["snapshot_bucket"],
        "event_time": event["event_time"],
        "price_at_event": price_at_event,
        "check_time": current_summary.get("timestamp"),
        "horizon": horizon,
        "price_after": price_after,
        "price_change_pct": calculate_price_change_pct(price_at_event, price_after),
        "outcome_status": "CHECKED",
        "source": current_summary.get("source", "CoinGecko"),
    }