import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from gspread.exceptions import WorksheetNotFound
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from storage.sheets_writer import get_sheet


RAW_SHEET = "01_raw_market"
EXCHANGE_DEPTH_SHEET = "02_exchange_depth"
SUMMARY_1H_SHEET = "summary_1h"
SUMMARY_4H_SHEET = "summary_4h"


def get_worksheet_safe(spreadsheet, worksheet_name):
    try:
        return spreadsheet.worksheet(worksheet_name)
    except WorksheetNotFound:
        return None


def get_records_safe(worksheet):
    if worksheet is None:
        return []
    return worksheet.get_all_records()


def get_last_record(records):
    if not records:
        return None
    return records[-1]


def calculate_age_minutes(timestamp_str):
    timestamp = datetime.fromisoformat(timestamp_str)
    now = datetime.now(timezone.utc)
    delta = now - timestamp
    return round(delta.total_seconds() / 60, 2)


def get_system_health(age_minutes):
    if age_minutes is None:
        return "UNKNOWN"
    if age_minutes < 20:
        return "HEALTHY"
    if age_minutes < 45:
        return "WARNING"
    return "CRITICAL"


def build_status_message():
    spreadsheet = get_sheet()

    raw_ws = get_worksheet_safe(spreadsheet, RAW_SHEET)
    exchange_depth_ws = get_worksheet_safe(spreadsheet, EXCHANGE_DEPTH_SHEET)
    summary_1h_ws = get_worksheet_safe(spreadsheet, SUMMARY_1H_SHEET)
    summary_4h_ws = get_worksheet_safe(spreadsheet, SUMMARY_4H_SHEET)

    raw_records = get_records_safe(raw_ws)
    exchange_depth_records = get_records_safe(exchange_depth_ws)
    summary_1h_records = get_records_safe(summary_1h_ws)
    summary_4h_records = get_records_safe(summary_4h_ws)

    last_raw = get_last_record(raw_records)

    age_minutes = None
    health = "UNKNOWN"
    latest_price = "N/A"
    latest_depth_ratio = "N/A"
    latest_total_volume = "N/A"
    last_timestamp = "N/A"

    if last_raw:
        last_timestamp = last_raw.get("timestamp", "N/A")
        age_minutes = calculate_age_minutes(last_timestamp)
        health = get_system_health(age_minutes)

        latest_price = last_raw.get("btc_price", "N/A")
        latest_depth_ratio = last_raw.get("depth_ratio", "N/A")
        latest_total_volume = last_raw.get("total_volume_usd", "N/A")

    return f"""BTC LIQUIDITY SYSTEM STATUS

System:
{health}

Google Sheets:
01_raw_market: {len(raw_records)} rows
02_exchange_depth: {len(exchange_depth_records)} rows
summary_1h: {len(summary_1h_records)} rows
summary_4h: {len(summary_4h_records)} rows

Last Snapshot:
{last_timestamp}

Age:
{age_minutes if age_minutes is not None else "N/A"} minutes

Latest Market:
BTC Price: {latest_price}
Depth Ratio: {latest_depth_ratio}
Total Volume: {latest_total_volume}
"""


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = build_status_message()
    await update.message.reply_text(message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Available commands:\n/status - Check BTC Liquidity System status\n/help - Show commands"
    )


def get_bot_token():
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN in .env")

    return token


def main():
    token = get_bot_token()

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("help", help_command))

    print("Telegram status bot started")
    print("Send /status to the bot")
    print("Press Ctrl+C to stop")

    app.run_polling()


if __name__ == "__main__":
    main()
