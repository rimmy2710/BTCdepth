from typing import Any, Dict, List, Optional

from alerts.telegram_sender import send_telegram_message


LOW_THRESHOLDS = [
    (0.2, "SELL_DEPTH_EXTREME"),
    (0.5, "SELL_DEPTH_VERY_STRONG"),
    (0.7, "SELL_DEPTH_STRONG"),
]

HIGH_THRESHOLDS = [
    (3.0, "BUY_DEPTH_SUPER_EXTREME"),
    (2.0, "BUY_DEPTH_EXTREME"),
    (1.5, "BUY_DEPTH_VERY_STRONG"),
    (1.3, "BUY_DEPTH_STRONG"),
]


def safe_float(value: Any) -> float:
    if value is None:
        return 0.0

    return float(value)


def format_usd(value: float) -> str:
    abs_value = abs(value)

    if abs_value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B USD"

    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M USD"

    if abs_value >= 1_000:
        return f"{value / 1_000:.2f}K USD"

    return f"{value:.2f} USD"


def get_alert_level(depth_ratio: Optional[float]) -> Optional[str]:
    if depth_ratio is None:
        return None

    for threshold, label in LOW_THRESHOLDS:
        if depth_ratio <= threshold:
            return label

    for threshold, label in HIGH_THRESHOLDS:
        if depth_ratio >= threshold:
            return label

    return None


def get_top_5_markets(selected_tickers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sorted_markets = sorted(
        selected_tickers,
        key=lambda item: safe_float(item.get("volume_usd")),
        reverse=True,
    )

    return sorted_markets[:5]


def build_top_5_market_summary(
    selected_tickers: List[Dict[str, Any]],
) -> Dict[str, Any]:
    top_5 = get_top_5_markets(selected_tickers)

    if not top_5:
        raise ValueError("No markets available for liquidity alert")

    total_volume = sum(safe_float(item.get("volume_usd")) for item in top_5)
    total_depth_up = sum(safe_float(item.get("depth_up_usd")) for item in top_5)
    total_depth_down = sum(safe_float(item.get("depth_down_usd")) for item in top_5)

    depth_ratio = (
        total_depth_up / total_depth_down
        if total_depth_down > 0
        else None
    )

    return {
        "top_5_markets": top_5,
        "total_volume_usd": round(total_volume, 2),
        "total_depth_up_usd": round(total_depth_up, 2),
        "total_depth_down_usd": round(total_depth_down, 2),
        "depth_ratio": round(depth_ratio, 4) if depth_ratio is not None else None,
    }


def format_exchange_details(
    top_5_markets: List[Dict[str, Any]],
    total_volume_usd: float,
) -> str:
    lines = []

    for index, market in enumerate(top_5_markets, start=1):
        exchange_name = market.get("exchange_name", "UNKNOWN")
        pair = market.get("pair", "UNKNOWN")

        volume = safe_float(market.get("volume_usd"))
        depth_up = safe_float(market.get("depth_up_usd"))
        depth_down = safe_float(market.get("depth_down_usd"))

        ratio = depth_up / depth_down if depth_down > 0 else None
        share = (volume / total_volume_usd) * 100 if total_volume_usd > 0 else 0

        lines.append(
            "\n".join(
                [
                    f"{index}. {exchange_name} {pair}",
                    f"Volume: {format_usd(volume)}",
                    f"Share: {share:.2f}%",
                    f"Depth Ratio: {ratio:.4f}" if ratio is not None else "Depth Ratio: N/A",
                    f"Up: {format_usd(depth_up)} | Down: {format_usd(depth_down)}",
                ]
            )
        )

    return "\n\n".join(lines)


def build_liquidity_alert_message(
    summary: Dict[str, Any],
    selected_tickers: List[Dict[str, Any]],
) -> Optional[str]:
    market_summary = build_top_5_market_summary(selected_tickers)

    depth_ratio = market_summary["depth_ratio"]
    alert_level = get_alert_level(depth_ratio)

    if alert_level is None:
        return None

    timestamp = summary.get("timestamp")
    btc_price = safe_float(summary.get("btc_price"))
    source = summary.get("source", "CoinGecko")

    exchange_details = format_exchange_details(
        market_summary["top_5_markets"],
        market_summary["total_volume_usd"],
    )

    return f"""🚨 BTC LIQUIDITY ALERT

Time:
{timestamp}

Source:
{source}

Market Summary
────────────────

Depth Ratio:
{depth_ratio:.4f}

Alert Level:
{alert_level}

BTC Price:
{format_usd(btc_price)}

Total Volume:
{format_usd(market_summary["total_volume_usd"])}

Depth Up (+2%):
{format_usd(market_summary["total_depth_up_usd"])}

Depth Down (-2%):
{format_usd(market_summary["total_depth_down_usd"])}


Exchange Details
────────────────

{exchange_details}
"""


def send_liquidity_alert_if_needed(
    summary: Dict[str, Any],
    selected_tickers: List[Dict[str, Any]],
) -> bool:
    message = build_liquidity_alert_message(
        summary=summary,
        selected_tickers=selected_tickers,
    )

    if message is None:
        print("No liquidity alert triggered")
        return False

    send_telegram_message(message)

    print("Liquidity alert sent to Telegram")

    return True


if __name__ == "__main__":
    sample_summary = {
        "timestamp": "2026-06-09T03:19:27+00:00",
        "btc_price": 62904,
        "source": "CoinGecko",
    }

    sample_tickers = [
        {
            "exchange_name": "Binance",
            "pair": "BTC/USDT",
            "volume_usd": 1_470_000_000,
            "depth_up_usd": 15_000_000,
            "depth_down_usd": 30_000_000,
        },
        {
            "exchange_name": "Bybit",
            "pair": "BTC/USDT",
            "volume_usd": 820_000_000,
            "depth_up_usd": 12_000_000,
            "depth_down_usd": 20_000_000,
        },
        {
            "exchange_name": "Coinbase Exchange",
            "pair": "BTC/USD",
            "volume_usd": 590_000_000,
            "depth_up_usd": 10_000_000,
            "depth_down_usd": 18_000_000,
        },
        {
            "exchange_name": "OKX",
            "pair": "BTC/USDT",
            "volume_usd": 480_000_000,
            "depth_up_usd": 8_000_000,
            "depth_down_usd": 16_000_000,
        },
        {
            "exchange_name": "Gate",
            "pair": "BTC/USDT",
            "volume_usd": 330_000_000,
            "depth_up_usd": 5_000_000,
            "depth_down_usd": 10_000_000,
        },
    ]

    message = build_liquidity_alert_message(
        summary=sample_summary,
        selected_tickers=sample_tickers,
    )

    assert message is not None
    assert "SELL_DEPTH_STRONG" in message
    assert "Total Volume:" in message
    assert "Exchange Details" in message
    assert "Share:" in message

    print("Liquidity alert formatter dry-run OK")
