import subprocess
import time
from datetime import datetime


MARKET_COLLECTION_MINUTES = {0, 15, 30, 45}
SUMMARY_1H_MINUTES = {0}
SUMMARY_4H_HOURS = {0, 4, 8, 12, 16, 20}


last_market_collection_key = None
last_summary_1h_key = None
last_summary_4h_key = None


def run_command(command):
    print(f"\nRunning command: {' '.join(command)}")

    result = subprocess.run(
        command,
        check=False,
    )

    if result.returncode == 0:
        print("Command completed successfully")
    else:
        print(f"Command failed with exit code: {result.returncode}")

    return result.returncode


def run_market_collection():
    print("\nRunning 15m market collection...")
    return run_command(["python", "main.py"])


def run_summary_1h():
    print("\nRunning 1H summary job...")
    return run_command(["python", "-m", "processors.summary_1h_job"])


def run_summary_4h():
    print("\nRunning 4H summary job...")
    return run_command(["python", "-m", "processors.summary_4h_job"])


def should_run_market_collection(now):
    return now.minute in MARKET_COLLECTION_MINUTES


def should_run_summary_1h(now):
    return now.minute in SUMMARY_1H_MINUTES


def should_run_summary_4h(now):
    return now.minute == 0 and now.hour in SUMMARY_4H_HOURS


def scheduler_tick(now=None):
    global last_market_collection_key
    global last_summary_1h_key
    global last_summary_4h_key

    now = now or datetime.now()

    market_key = now.strftime("%Y-%m-%d %H:%M")
    summary_1h_key = now.strftime("%Y-%m-%d %H")
    summary_4h_key = now.strftime("%Y-%m-%d %H")

    if should_run_market_collection(now) and market_key != last_market_collection_key:
        run_market_collection()
        last_market_collection_key = market_key

    if should_run_summary_1h(now) and summary_1h_key != last_summary_1h_key:
        run_summary_1h()
        last_summary_1h_key = summary_1h_key

    if should_run_summary_4h(now) and summary_4h_key != last_summary_4h_key:
        run_summary_4h()
        last_summary_4h_key = summary_4h_key


def main():
    print("BTC Clock-Based Scheduler Started")
    print("Market collection: every 15 minutes at :00, :15, :30, :45")
    print("Summary 1H: every hour at :00")
    print("Summary 4H: every 4 hours at 00:00, 04:00, 08:00, 12:00, 16:00, 20:00")

    while True:
        scheduler_tick()
        time.sleep(10)


if __name__ == "__main__":
    main()