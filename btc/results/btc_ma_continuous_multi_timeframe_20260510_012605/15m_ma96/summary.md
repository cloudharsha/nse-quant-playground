# BTC 15m MA96 Continuous Trailing Backtest

## Strategy Details

- Dataset: `btc/data/BTCUSD_data_15m.csv`
- Tested UTC date range: `2025-05-10` through `2026-05-09`
- Signal source: BTC-USD 15m close
- Initial activation: `2025-05-10 07:15:00+00:00` (one-time UTC activation threshold)
- No routine day-end exit; positions carry continuously until stopped, forced flat on a data gap, or exited at end of data.
- MA rule: 96-SMA of 15m closes computed fresh from the BTC dataset
- Direction rule: close above SMA -> long; close below SMA -> short; equal -> no entry
- Stop rule: long exits when candle low touches the trailing SMA; short exits when candle high touches the trailing SMA
- Re-entry rule: after a stop, the same completed candle may immediately open a new trade if the signal remains valid.
- Gap rule: force flat at the last known boundary before a gap, then resume on the first post-gap candle and allow a new entry only after that candle completes.
- Accounting: points only; no brokerage, slippage, leverage, or position sizing.

## Data Notes

- First CSV row: `2025-05-10 07:15:00+00:00`
- First MA-usable row: `2025-05-11 07:00:00+00:00`
- Source rows loaded: `34943`
- Rows inside requested date filter: `34943`
- Rows processed after activation: `34943`
- Gap events detected in this run: `2`

## Overall Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Long | Short | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | Avg Points | Max Profit | Max Loss | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Overall | 365 | 35 | 1 | 0 | 3590 | 2 | 1838 | 1752 | 3587 | 2 | 1 | 137 | 192 | 37528.18 | 114.07 | 12176.67 | -4812.74 | 14953.16 |

- Total trades: `3590`
- Win rate: `10.45%`

## Yearly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Long | Short | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | Avg Points | Max Profit | Max Loss | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025 | 236 | 18 | 1 | 0 | 2355 | 1 | 1215 | 1140 | 2354 | 1 | 0 | 91 | 126 | 23658.96 | 109.03 | 7319.05 | -4812.74 | 11440.38 |
| 2026 | 129 | 17 | 0 | 0 | 1235 | 1 | 623 | 612 | 1233 | 1 | 1 | 46 | 66 | 13869.22 | 123.83 | 12176.67 | -3056.81 | 14953.16 |

## Monthly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Long | Short | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | Avg Points | Max Profit | Max Loss | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025-05 | 22 | 2 | 1 | 0 | 202 | 0 | 100 | 102 | 202 | 0 | 0 | 5 | 14 | -3678.27 | -193.59 | 3439.41 | -2626.97 | 10225.99 |
| 2025-06 | 30 | 3 | 0 | 0 | 332 | 0 | 170 | 162 | 332 | 0 | 0 | 10 | 17 | -1684.98 | -62.41 | 4915.68 | -2596.15 | 5497.58 |
| 2025-07 | 31 | 1 | 0 | 0 | 306 | 0 | 156 | 150 | 306 | 0 | 0 | 13 | 17 | 3531.07 | 117.70 | 6124.02 | -3126.60 | 11440.38 |
| 2025-08 | 31 | 2 | 0 | 0 | 321 | 0 | 160 | 161 | 321 | 0 | 0 | 13 | 16 | 4851.70 | 167.30 | 4406.87 | -1588.24 | 4326.71 |
| 2025-09 | 30 | 2 | 0 | 0 | 299 | 0 | 161 | 138 | 299 | 0 | 0 | 12 | 16 | 2648.17 | 94.58 | 3707.16 | -1677.40 | 4449.22 |
| 2025-10 | 31 | 4 | 0 | 0 | 278 | 1 | 147 | 131 | 277 | 1 | 0 | 13 | 14 | 12888.07 | 477.34 | 7319.05 | -2695.76 | 6481.50 |
| 2025-11 | 30 | 2 | 0 | 0 | 350 | 0 | 177 | 173 | 350 | 0 | 0 | 10 | 18 | 921.71 | 32.92 | 4772.52 | -4812.74 | 8463.02 |
| 2025-12 | 31 | 2 | 0 | 0 | 267 | 0 | 144 | 123 | 267 | 0 | 0 | 15 | 14 | 4181.49 | 144.19 | 4352.25 | -2798.74 | 6765.56 |
| 2026-01 | 31 | 4 | 0 | 0 | 305 | 0 | 152 | 153 | 305 | 0 | 0 | 10 | 17 | -1375.81 | -50.96 | 3507.04 | -3056.81 | 6945.55 |
| 2026-02 | 28 | 5 | 0 | 0 | 258 | 0 | 126 | 132 | 258 | 0 | 0 | 9 | 14 | 9940.43 | 432.19 | 12176.67 | -2885.19 | 14953.16 |
| 2026-03 | 31 | 5 | 0 | 0 | 303 | 0 | 164 | 139 | 303 | 0 | 0 | 11 | 15 | 2385.44 | 91.75 | 4509.64 | -2708.76 | 4858.41 |
| 2026-04 | 30 | 2 | 0 | 0 | 300 | 0 | 142 | 158 | 300 | 0 | 0 | 12 | 16 | 365.14 | 13.04 | 2466.00 | -2172.35 | 3881.06 |
| 2026-05 | 9 | 1 | 0 | 0 | 69 | 1 | 39 | 30 | 67 | 1 | 1 | 4 | 4 | 2554.02 | 319.25 | 1986.73 | -1678.64 | 1787.44 |

## Gap Events / Exceptions

- `2025-10-25 15:00:00+00:00` -> `2025-10-25 21:00:00+00:00`: `23` missing candles; active trade = `YES`. Missing 23 candle(s) between 2025-10-25 15:00:00+00:00 and 2025-10-25 21:00:00+00:00; resumed on next available row.
- `2026-05-08 01:15:00+00:00` -> `2026-05-08 07:45:00+00:00`: `25` missing candles; active trade = `YES`. Missing 25 candle(s) between 2026-05-08 01:15:00+00:00 and 2026-05-08 07:45:00+00:00; resumed on next available row.

## Output Files

- `btc/results/btc_ma_continuous_multi_timeframe_20260510_012605/15m_ma96/trades.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_20260510_012605/15m_ma96/gap_events.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_20260510_012605/15m_ma96/daywise_summary.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_20260510_012605/15m_ma96/monthly_summary.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_20260510_012605/15m_ma96/yearly_summary.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_20260510_012605/15m_ma96/summary.json`
- `btc/results/btc_ma_continuous_multi_timeframe_20260510_012605/15m_ma96/summary.md`
- `btc/results/btc_ma_continuous_multi_timeframe_20260510_012605/15m_ma96/backtest.log`

## Remarks

- The one-time activation threshold is applied only on the first candidate UTC date.
- Opposite signals are ignored while a position is live; only the trailing SMA stop or a gap flat can close the trade.
- The entry candle itself cannot stop a newly opened position.
- Daywise results are grouped by realized exit date in UTC; held-only dates are preserved separately.
- Monthly and yearly results are derived from daywise realized P&L in points.
