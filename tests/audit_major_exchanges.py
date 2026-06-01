from collectors.coingecko_collector import fetch_btc_tickers


TARGET_EXCHANGES = {
    "Binance",
    "Bybit",
    "Coinbase Exchange",
    "OKX",
    "Gate",
}

TARGET_QUOTES = {
    "USDT",
    "USDC",
    "USD",
}


def main():
    data = fetch_btc_tickers()
    tickers = data.get("tickers", [])

    selected = []

    for ticker in tickers:
        market = ticker.get("market") or {}
        exchange_name = market.get("name")

        base = ticker.get("base")
        target = ticker.get("target")

        if exchange_name not in TARGET_EXCHANGES:
            continue

        if base not in {"BTC", "XBT"}:
            continue

        if target not in TARGET_QUOTES:
            continue

        if ticker.get("is_anomaly") or ticker.get("is_stale"):
            continue

        volume_usd = (ticker.get("converted_volume") or {}).get("usd") or 0
        depth_up = ticker.get("cost_to_move_up_usd") or 0
        depth_down = ticker.get("cost_to_move_down_usd") or 0
        price = (ticker.get("converted_last") or {}).get("usd") or ticker.get("last") or 0

        if volume_usd <= 0:
            continue

        selected.append({
            "exchange": exchange_name,
            "pair": f"{base}/{target}",
            "price": price,
            "volume_usd": volume_usd,
            "depth_up_usd": depth_up,
            "depth_down_usd": depth_down,
            "depth_ratio": depth_up / depth_down if depth_down else None,
        })

    selected = sorted(selected, key=lambda x: x["volume_usd"], reverse=True)

    total_volume = sum(x["volume_usd"] for x in selected)
    total_up = sum(x["depth_up_usd"] for x in selected)
    total_down = sum(x["depth_down_usd"] for x in selected)
    total_ratio = total_up / total_down if total_down else None

    print("\nSELECTED MAJOR EXCHANGES")
    print("------------------------")

    for item in selected:
        print(
            f"{item['exchange']} | {item['pair']} | "
            f"vol={round(item['volume_usd'], 2)} | "
            f"up={round(item['depth_up_usd'], 2)} | "
            f"down={round(item['depth_down_usd'], 2)} | "
            f"ratio={round(item['depth_ratio'], 4) if item['depth_ratio'] else None}"
        )

    print("\nSUMMARY")
    print("-------")
    print(f"selected_count: {len(selected)}")
    print(f"total_volume_usd: {round(total_volume, 2)}")
    print(f"total_depth_up_usd: {round(total_up, 2)}")
    print(f"total_depth_down_usd: {round(total_down, 2)}")
    print(f"depth_ratio: {round(total_ratio, 4) if total_ratio else None}")


if __name__ == "__main__":
    main()
