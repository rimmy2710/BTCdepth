# BTC Depth Project

## Current Status

### DONE

- CoinGecko API verified
- BTC tickers endpoint verified
- Volume data verified
- Depth data verified
- Google Sheets connected
- Service Account configured
- 01_raw_market created
- Google Sheets write test SUCCESS

### Next Task

TASK-004

Build CoinGecko Collector

Goal:

Collect:
- BTC Price
- Total Volume
- Total Depth Up
- Total Depth Down
- Depth Ratio

Output:

Python dict

No Google Sheets yet.

Test command:

python collectors/coingecko_collector.py

Expected:

Print market summary to terminal.

