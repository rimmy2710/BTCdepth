from collectors.coingecko_collector import (
    fetch_btc_tickers,
    build_market_summary,
    print_summary,
)

from storage.market_writer import write_market_snapshot
from storage.exchange_depth_writer import write_exchange_depth
from storage.event_writer import write_events
from storage.run_log_writer import write_run_log, build_run_id
from processors.event_engine import detect_events
from alerts.liquidity_alert import send_liquidity_alert_if_needed


def main():
    run_id = build_run_id()

    run_log = {
        "run_id": run_id,
        "status": "STARTED",
        "raw_written": False,
        "exchange_rows_written": 0,
        "events_written": 0,
        "alert_sent": False,
        "error_type": "",
        "error_message": "",
        "source": "",
    }

    try:
        print("BTC Depth System Started")
        print("Environment Loaded")

        data = fetch_btc_tickers()
        summary = build_market_summary(data)

        run_log["source"] = summary.get("source")

        print_summary(summary)

        write_market_snapshot(summary)
        run_log["raw_written"] = True

        write_exchange_depth(summary["selected_tickers"])
        run_log["exchange_rows_written"] = len(summary["selected_tickers"])

        send_liquidity_alert_if_needed(
            summary=summary,
            selected_tickers=summary["selected_tickers"],
        )

        events = detect_events(summary)
        write_events(events)
        run_log["events_written"] = len(events)

        run_log["status"] = "SUCCESS"

        print("\nPipeline completed successfully")

    except Exception as error:
        run_log["status"] = "FAILED"
        run_log["error_type"] = type(error).__name__
        run_log["error_message"] = str(error)
        print(f"\nPipeline failed: {error}")
        raise

    finally:
        write_run_log(run_log)


if __name__ == "__main__":
    main()