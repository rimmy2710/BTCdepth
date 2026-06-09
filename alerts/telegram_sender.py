import asyncio
import os

from dotenv import load_dotenv
from telegram import Bot


def get_telegram_config():
    load_dotenv()

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN in .env")

    if not chat_id:
        raise ValueError("Missing TELEGRAM_CHAT_ID in .env")

    return bot_token, chat_id


async def send_telegram_message_async(message: str):
    bot_token, chat_id = get_telegram_config()

    bot = Bot(token=bot_token)

    await bot.send_message(
        chat_id=chat_id,
        text=message,
    )


def send_telegram_message(message: str):
    asyncio.run(send_telegram_message_async(message))


if __name__ == "__main__":
    send_telegram_message("BTC Liquidity System Test")
    print("Telegram test message sent")
