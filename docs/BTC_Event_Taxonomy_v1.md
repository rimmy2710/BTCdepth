# BTC Event Taxonomy v1

## Purpose

This document defines the first standardized Event types for BTC Market Memory System.

The goal is not to predict price.

The goal is to convert raw market data into measurable market events.

---

## Current Data Available

- BTC Price
- Total Volume USD
- Total Depth Up USD
- Total Depth Down USD
- Depth Ratio
- Top Exchange
- Snapshot Bucket
- Exchange Depth Details

---

## Event Group 1: Depth Imbalance Events

### EVENT: DEPTH_SELL_IMBALANCE

Condition:

depth_ratio <= 0.7

Meaning:

Sell-side liquidity pressure is stronger than buy-side liquidity.

Outcome to track:

- price_after_1h
- price_after_4h
- price_after_24h
- max_runup
- max_drawdown
- reversal_or_continuation

---

### EVENT: DEPTH_SELL_EXTREME

Condition:

depth_ratio <= 0.5

Meaning:

Strong sell-side liquidity imbalance.

Outcome to track:

- price_after_1h
- price_after_4h
- price_after_24h
- liquidity_sweep
- max_drawdown

---

### EVENT: DEPTH_BUY_IMBALANCE

Condition:

depth_ratio >= 1.3

Meaning:

Buy-side liquidity pressure is stronger than sell-side liquidity.

Outcome to track:

- price_after_1h
- price_after_4h
- price_after_24h
- max_runup
- max_drawdown
- reversal_or_continuation

---

### EVENT: DEPTH_BUY_EXTREME

Condition:

depth_ratio >= 1.5

Meaning:

Strong buy-side liquidity imbalance.

Outcome to track:

- price_after_1h
- price_after_4h
- price_after_24h
- liquidity_sweep
- max_runup

---

## Event Group 2: Volume Events

### EVENT: VOLUME_SPIKE

Condition:

current_total_volume_usd > average_volume_1h * 1.3

Meaning:

Market activity is increasing abnormally.

Outcome to track:

- price_after_1h
- price_after_4h
- volatility_after_event
- continuation_or_reversal

---

## Event Group 3: Exchange Dominance Events

### EVENT: TOP_EXCHANGE_SHIFT

Condition:

top_exchange changes from previous snapshot.

Meaning:

Liquidity leadership shifts between major exchanges.

Outcome to track:

- next_price_direction
- depth_ratio_change
- volume_change

---

## Event Group 4: Future Research Events

These events require future data sources such as CoinGlass.

### EVENT: OI_EXPANSION

Required data:

Open Interest

Condition:

OI increases more than 10% within 4H.

---

### EVENT: OI_FLUSH

Required data:

Open Interest

Condition:

OI decreases more than 15% within 1H.

---

### EVENT: FUNDING_EXTREME

Required data:

Funding Rate

Condition:

Funding Rate > 0.03 or Funding Rate < -0.03.

---

### EVENT: LIQUIDITY_SWEEP

Required data:

Liquidity Heatmap / Liquidation Cluster

Condition:

Price reaches major liquidity cluster.

---

## Event Database MVP

First events to implement:

1. DEPTH_SELL_IMBALANCE
2. DEPTH_SELL_EXTREME
3. DEPTH_BUY_IMBALANCE
4. DEPTH_BUY_EXTREME
5. VOLUME_SPIKE
6. TOP_EXCHANGE_SHIFT

---

## Principle

Do not create too many events at the beginning.

Start small.

Collect clean events.

Track outcomes.

Then build probability.