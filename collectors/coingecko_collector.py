import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone
def get_15m_snapshot_bucket(dt=None):
    if dt is None:
        dt = datetime.now(timezone.utc)

    minute_bucket = (dt.minute // 15) * 15

    return dt.replace(
        minute=minute_bucket,
        second=0,
        microsecond=0,
    ).isoformat()


COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/bitcoin/tickers"

MAJOR_EXCHANGES = {
    "Binance",
    "Bybit",
    "Coinbase Exchange",
    "OKX",
    "Gate",
}

VALID_BASES = {"BTC", "XBT"}
VALID_QUOTES = {"USDT", "USDC", "USD"}


def fetch_btc_tickers():
    load_dotenv()

    api_key = os.getenv("COINGECKO_API_KEY")

    if not api_key:
        raise ValueError("Missing COINGECKO_API_KEY in .env")

    headers = {
        "x-cg-demo-api-key": api_key,
    }

    params = {
        "page": 1,
        "order": "volume_desc",
        "depth": "true",
    }

    response = requests.get(
        COINGECKO_URL,
        headers=headers,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def build_market_summary(data):
    tickers = data.get("tickers", [])

    if not tickers:
        raise ValueError("No tickers returned from CoinGecko")

    selected_tickers = []

    for ticker in tickers:
        market = ticker.get("market") or {}
        exchange_name = market.get("name", "UNKNOWN")

        base = ticker.get("base")
        target = ticker.get("target")

        if exchange_name not in MAJOR_EXCHANGES:
            continue

        if base not in VALID_BASES:
            continue

        if target not in VALID_QUOTES:
            continue

        if ticker.get("is_anomaly") or ticker.get("is_stale"):
            continue

        volume_usd = (ticker.get("converted_volume") or {}).get("usd") or 0
        depth_up = ticker.get("cost_to_move_up_usd") or 0
        depth_down = ticker.get("cost_to_move_down_usd") or 0
        price = (ticker.get("converted_last") or {}).get("usd") or ticker.get("last") or 0

        if volume_usd <= 0:
            continue

        selected_tickers.append({
            "exchange_name": exchange_name,
            "pair": f"{base}/{target}",
            "price": price,
            "volume_usd": volume_usd,
            "depth_up_usd": depth_up,
            "depth_down_usd": depth_down,
            "depth_ratio": depth_up / depth_down if depth_down else None,
        })

    if not selected_tickers:
        raise ValueError("No valid major exchange tickers found")

    selected_tickers = sorted(
        selected_tickers,
        key=lambda item: item["volume_usd"],
        reverse=True,
    )

    total_volume_usd = sum(item["volume_usd"] for item in selected_tickers)
    total_depth_up_usd = sum(item["depth_up_usd"] for item in selected_tickers)
    total_depth_down_usd = sum(item["depth_down_usd"] for item in selected_tickers)

    depth_ratio = (
        total_depth_up_usd / total_depth_down_usd
        if total_depth_down_usd > 0
        else None
    )

    top_exchange = selected_tickers[0]

    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "snapshot_bucket": get_15m_snapshot_bucket(),
        "btc_price": top_exchange["price"],
        "total_volume_usd": round(total_volume_usd, 2),
        "total_depth_up_usd": round(total_depth_up_usd, 2),
        "total_depth_down_usd": round(total_depth_down_usd, 2),
        "depth_ratio": round(depth_ratio, 4) if depth_ratio is not None else None,
        "top_exchange": top_exchange["exchange_name"],
        "top_exchange_pair": top_exchange["pair"],
        "top_exchange_price": top_exchange["price"],
        "top_exchange_volume_usd": round(top_exchange["volume_usd"], 2),
        "top_exchange_depth_up_usd": round(top_exchange["depth_up_usd"], 2),
        "top_exchange_depth_down_usd": round(top_exchange["depth_down_usd"], 2),
        "selected_exchange_count": len(selected_tickers),
        "selected_exchanges": ", ".join(sorted({item["exchange_name"] for item in selected_tickers})),
        "selected_tickers": selected_tickers,
        "source": "CoinGecko",
    }

    return summary


def print_summary(summary):
    print("\nBTC MAJOR EXCHANGES DEPTH SUMMARY")
    print("---------------------------------")
    print(f"Timestamp: {summary['timestamp']}")
    print(f"BTC Price: {summary['btc_price']}")
    print(f"Total Volume USD: {summary['total_volume_usd']}")
    print(f"Total Depth Up USD: {summary['total_depth_up_usd']}")
    print(f"Total Depth Down USD: {summary['total_depth_down_usd']}")
    print(f"Depth Ratio: {summary['depth_ratio']}")
    print(f"Top Exchange: {summary['top_exchange']}")
    print(f"Top Exchange Pair: {summary['top_exchange_pair']}")
    print(f"Top Exchange Volume USD: {summary['top_exchange_volume_usd']}")
    print(f"Selected Exchange Count: {summary['selected_exchange_count']}")
    print(f"Selected Exchanges: {summary['selected_exchanges']}")
    print(f"Source: {summary['source']}")


def main():
    data = fetch_btc_tickers()
    summary = build_market_summary(data)
    print_summary(summary)


if __name__ == "__main__":
    main()
