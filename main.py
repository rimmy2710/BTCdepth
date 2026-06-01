from collectors.coingecko_collector import (
    fetch_btc_tickers,
    build_market_summary,
    print_summary,
)

from storage.market_writer import write_market_snapshot


def main():
    print("BTC Depth System Started")
    print("Environment Loaded")

    data = fetch_btc_tickers()

    summary = build_market_summary(data)

    print_summary(summary)

    write_market_snapshot(summary)

    print("\nPipeline completed successfully")


if __name__ == "__main__":
    main()
