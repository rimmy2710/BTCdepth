import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials


WORKSHEET_NAME = "02_exchange_depth"

HEADERS = [
    "timestamp",
    "exchange_name",
    "pair",
    "volume_usd",
    "depth_up_usd",
    "depth_down_usd",
    "depth_ratio",
]


def calculate_depth_ratio(depth_up_usd: float, depth_down_usd: float) -> Optional[float]:
    if depth_down_usd == 0:
        return None
    return round(depth_up_usd / depth_down_usd, 4)


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_exchange_depth_rows(
    selected_markets: List[Dict[str, Any]],
    timestamp: Optional[str] = None,
) -> List[List[Any]]:
    ts = timestamp or utc_timestamp()
    rows: List[List[Any]] = []

    for market in selected_markets:
        exchange_name = market.get("exchange_name")
        pair = market.get("pair")

        volume_usd = float(market.get("volume_usd", 0) or 0)
        depth_up_usd = float(market.get("depth_up_usd", 0) or 0)
        depth_down_usd = float(market.get("depth_down_usd", 0) or 0)

        depth_ratio = calculate_depth_ratio(depth_up_usd, depth_down_usd)

        rows.append(
            [
                ts,
                exchange_name,
                pair,
                round(volume_usd, 2),
                round(depth_up_usd, 2),
                round(depth_down_usd, 2),
                depth_ratio,
            ]
        )

    return rows


def get_spreadsheet():
    load_dotenv()

    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    credentials_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

    if not sheet_id:
        raise ValueError("Missing GOOGLE_SHEET_ID in .env")

    if not credentials_path:
        raise ValueError("Missing GOOGLE_SERVICE_ACCOUNT_JSON in .env")

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        credentials_path,
        scope,
    )

    client = gspread.authorize(creds)

    return client.open_by_key(sheet_id)


def get_or_create_worksheet(spreadsheet: Any):
    try:
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
    except Exception:
        worksheet = spreadsheet.add_worksheet(
            title=WORKSHEET_NAME,
            rows=1000,
            cols=len(HEADERS),
        )
        worksheet.append_row(HEADERS)

    return worksheet


def write_exchange_depth(selected_markets: List[Dict[str, Any]]) -> int:
    spreadsheet = get_spreadsheet()
    worksheet = get_or_create_worksheet(spreadsheet)

    rows = build_exchange_depth_rows(selected_markets)

    if not rows:
        print("No exchange depth rows to write")
        return 0

    worksheet.append_rows(rows)

    print(f"Exchange depth rows written to Google Sheets: {len(rows)}")

    return len(rows)


if __name__ == "__main__":
    sample_markets = [
        {
            "exchange_name": "Binance",
            "pair": "BTC/USDT",
            "volume_usd": 820_198_635,
            "depth_up_usd": 15_671_554.06,
            "depth_down_usd": 27_732_739.18,
        },
        {
            "exchange_name": "Bybit",
            "pair": "BTC/USDT",
            "volume_usd": 572_962_784,
            "depth_up_usd": 13_344_605.21,
            "depth_down_usd": 8_192_943.92,
        },
    ]

    prepared_rows = build_exchange_depth_rows(
        sample_markets,
        timestamp="2026-06-02T00:00:00+00:00",
    )

    assert len(prepared_rows) == 2
    assert prepared_rows[0][1] == "Binance"
    assert prepared_rows[0][2] == "BTC/USDT"
    assert prepared_rows[0][6] == 0.5651
    assert prepared_rows[1][1] == "Bybit"
    assert prepared_rows[1][6] == 1.6288

    print("02_exchange_depth writer dry-run OK")
    print(f"Rows prepared: {len(prepared_rows)}")