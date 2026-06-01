from collectors.coingecko_collector import fetch_btc_tickers


def calc_ratio(items):
    up = sum(x.get("cost_to_move_up_usd") or 0 for x in items)
    down = sum(x.get("cost_to_move_down_usd") or 0 for x in items)
    ratio = up / down if down else None
    volume = sum((x.get("converted_volume") or {}).get("usd") or 0 for x in items)
    return volume, up, down, ratio, len(items)


def print_result(name, items):
    volume, up, down, ratio, count = calc_ratio(items)
    print(f"\n{name}")
    print("-" * len(name))
    print(f"count: {count}")
    print(f"volume_usd: {round(volume, 2)}")
    print(f"depth_up_usd: {round(up, 2)}")
    print(f"depth_down_usd: {round(down, 2)}")
    print(f"depth_ratio: {round(ratio, 4) if ratio else None}")


data = fetch_btc_tickers()
tickers = data.get("tickers", [])

all_volume = [
    t for t in tickers
    if ((t.get("converted_volume") or {}).get("usd") or 0) > 0
]

clean = [
    t for t in all_volume
    if not t.get("is_anomaly") and not t.get("is_stale")
]

btc_base = [
    t for t in clean
    if t.get("base") in ["BTC", "XBT"]
]

btc_usd_stable = [
    t for t in btc_base
    if t.get("target") in ["USDT", "USDC", "USD", "FDUSD"]
]

btc_usdt_only = [
    t for t in btc_base
    if t.get("target") == "USDT"
]

print_result("ALL VOLUME TICKERS", all_volume)
print_result("CLEAN ONLY", clean)
print_result("BTC/XBT BASE ONLY", btc_base)
print_result("BTC USD/STABLE ONLY", btc_usd_stable)
print_result("BTC/USDT ONLY", btc_usdt_only)

print("\nTOP 20 BY VOLUME")
print("----------------")
for t in sorted(all_volume, key=lambda x: (x.get("converted_volume") or {}).get("usd") or 0, reverse=True)[:20]:
    market = (t.get("market") or {}).get("name")
    pair = f"{t.get('base')}/{t.get('target')}"
    volume = (t.get("converted_volume") or {}).get("usd") or 0
    up = t.get("cost_to_move_up_usd") or 0
    down = t.get("cost_to_move_down_usd") or 0
    ratio = up / down if down else None
    print(f"{market} | {pair} | vol={round(volume,2)} | up={round(up,2)} | down={round(down,2)} | ratio={round(ratio,4) if ratio else None}")
