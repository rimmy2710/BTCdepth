from collectors.coingecko_collector import (
    fetch_btc_tickers,
    build_market_summary,
    print_summary,
)

from storage.market_writer import write_market_snapshot
from storage.exchange_depth_writer import write_exchange_depth


def main():
    print("BTC Depth System Started")
    print("Environment Loaded")

    data = fetch_btc_tickers()

    summary = build_market_summary(data)

    print_summary(summary)

    write_market_snapshot(summary)

    write_exchange_depth(summary["selected_tickers"])

    print("\nPipeline completed successfully")


if __name__ == "__main__":
    main()