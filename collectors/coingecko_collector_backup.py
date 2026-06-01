import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone


COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/bitcoin/tickers"


def fetch_btc_tickers():
    load_dotenv()

    api_key = os.getenv("COINGECKO_API_KEY")

    if not api_key:
        raise ValueError("Missing COINGECKO_API_KEY in .env")

    headers = {
        "x-cg-demo-api-key": api_key
    }

    params = {
        "page": 1,
        "order": "volume_desc",
        "depth": "true"
    }

    response = requests.get(
        COINGECKO_URL,
        headers=headers,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def build_market_summary(data):
    tickers = data.get("tickers", [])

    if not tickers:
        raise ValueError("No tickers returned from CoinGecko")

    valid_tickers = []

    for ticker in tickers:
        converted_volume = ticker.get("converted_volume") or {}
        volume_usd = converted_volume.get("usd") or 0

        depth_up = ticker.get("cost_to_move_up_usd") or 0
        depth_down = ticker.get("cost_to_move_down_usd") or 0

        price = ticker.get("converted_last", {}).get("usd") or ticker.get("last") or 0

        market = ticker.get("market") or {}
        exchange_name = market.get("name", "UNKNOWN")

        if volume_usd > 0:
            valid_tickers.append({
                "exchange_name": exchange_name,
                "price": price,
                "volume_usd": volume_usd,
                "depth_up_usd": depth_up,
                "depth_down_usd": depth_down,
                "base": ticker.get("base"),
                "target": ticker.get("target"),
            })

    if not valid_tickers:
        raise ValueError("No valid tickers with volume_usd found")

    total_volume_usd = sum(item["volume_usd"] for item in valid_tickers)
    total_depth_up_usd = sum(item["depth_up_usd"] for item in valid_tickers)
    total_depth_down_usd = sum(item["depth_down_usd"] for item in valid_tickers)

    depth_ratio = (
        total_depth_up_usd / total_depth_down_usd
        if total_depth_down_usd > 0
        else None
    )

    top_exchange = max(valid_tickers, key=lambda item: item["volume_usd"])

    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "btc_price": top_exchange["price"],
        "total_volume_usd": round(total_volume_usd, 2),
        "total_depth_up_usd": round(total_depth_up_usd, 2),
        "total_depth_down_usd": round(total_depth_down_usd, 2),
        "depth_ratio": round(depth_ratio, 4) if depth_ratio is not None else None,
        "top_exchange": top_exchange["exchange_name"],
        "top_exchange_price": top_exchange["price"],
        "top_exchange_volume_usd": round(top_exchange["volume_usd"], 2),
        "top_exchange_depth_up_usd": round(top_exchange["depth_up_usd"], 2),
        "top_exchange_depth_down_usd": round(top_exchange["depth_down_usd"], 2),
        "ticker_count": len(valid_tickers),
        "source": "CoinGecko",
    }

    return summary


def print_summary(summary):
    print("\nBTC MARKET SUMMARY")
    print("------------------")
    print(f"Timestamp: {summary['timestamp']}")
    print(f"BTC Price: {summary['btc_price']}")
    print(f"Total Volume USD: {summary['total_volume_usd']}")
    print(f"Total Depth Up USD: {summary['total_depth_up_usd']}")
    print(f"Total Depth Down USD: {summary['total_depth_down_usd']}")
    print(f"Depth Ratio: {summary['depth_ratio']}")
    print(f"Top Exchange: {summary['top_exchange']}")
    print(f"Top Exchange Volume USD: {summary['top_exchange_volume_usd']}")
    print(f"Top Exchange Depth Up USD: {summary['top_exchange_depth_up_usd']}")
    print(f"Top Exchange Depth Down USD: {summary['top_exchange_depth_down_usd']}")
    print(f"Ticker Count: {summary['ticker_count']}")
    print(f"Source: {summary['source']}")


def main():
    data = fetch_btc_tickers()
    summary = build_market_summary(data)
    print_summary(summary)


if __name__ == "__main__":
    main()
