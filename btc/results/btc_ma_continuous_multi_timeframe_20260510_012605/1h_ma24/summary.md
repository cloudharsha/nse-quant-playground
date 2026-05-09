# BTC 1h MA24 Continuous Trailing Backtest

## Strategy Details

- Dataset: `btc/data/BTCUSD_data_1h.csv`
- Tested UTC date range: `2025-05-11` through `2026-05-09`
- Signal source: BTC-USD 1h close
- Initial activation: `2025-05-11 20:00:00+00:00` (one-time UTC activation threshold)
- No routine day-end exit; positions carry continuously until stopped, forced flat on a data gap, or exited at end of data.
- MA rule: 24-SMA of 1h closes computed fresh from the BTC dataset
- Direction rule: close above SMA -> long; close below SMA -> short; equal -> no entry
- Stop rule: long exits when candle low touches the trailing SMA; short exits when candle high touches the trailing SMA
- Re-entry rule: after a stop, the same completed candle may immediately open a new trade if the signal remains valid.
- Gap rule: force flat at the last known boundary before a gap, then resume on the first post-gap candle and allow a new entry only after that candle completes.
- Accounting: points only; no brokerage, slippage, leverage, or position sizing.

## Data Notes

- First CSV row: `2025-05-11 20:00:00+00:00`
- First MA-usable row: `2025-05-12 19:00:00+00:00`
- Source rows loaded: `8698`
- Rows inside requested date filter: `8698`
- Rows processed after activation: `8698`
- Gap events detected in this run: `2`

## Overall Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Long | Short | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | Avg Points | Max Profit | Max Loss | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Overall | 364 | 32 | 1 | 0 | 1825 | 2 | 948 | 877 | 1822 | 2 | 1 | 135 | 196 | 26289.22 | 79.42 | 9915.87 | -3602.18 | 16541.13 |

- Total trades: `1825`
- Win rate: `14.08%`

## Yearly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Long | Short | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | Avg Points | Max Profit | Max Loss | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025 | 235 | 18 | 1 | 0 | 1194 | 1 | 638 | 556 | 1193 | 1 | 0 | 84 | 132 | 2858.36 | 13.23 | 7925.68 | -3602.18 | 16541.13 |
| 2026 | 129 | 14 | 0 | 0 | 631 | 1 | 310 | 321 | 629 | 1 | 1 | 51 | 64 | 23430.86 | 203.75 | 9915.87 | -2429.76 | 8007.80 |

## Monthly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Long | Short | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | Avg Points | Max Profit | Max Loss | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025-05 | 21 | 4 | 1 | 0 | 84 | 0 | 41 | 43 | 84 | 0 | 0 | 5 | 11 | -5594.65 | -349.67 | 3504.67 | -1969.22 | 10270.17 |
| 2025-06 | 30 | 3 | 0 | 0 | 178 | 0 | 98 | 80 | 178 | 0 | 0 | 9 | 18 | -5553.60 | -205.69 | 4136.20 | -2329.56 | 6573.86 |
| 2025-07 | 31 | 1 | 0 | 0 | 166 | 0 | 90 | 76 | 166 | 0 | 0 | 12 | 18 | -456.88 | -15.23 | 6057.05 | -2938.37 | 11918.60 |
| 2025-08 | 31 | 2 | 0 | 0 | 160 | 0 | 78 | 82 | 160 | 0 | 0 | 8 | 21 | 4311.40 | 148.67 | 4478.81 | -2370.14 | 5401.81 |
| 2025-09 | 30 | 2 | 0 | 0 | 148 | 0 | 81 | 67 | 148 | 0 | 0 | 11 | 17 | -1648.67 | -58.88 | 3766.57 | -2147.74 | 8933.93 |
| 2025-10 | 31 | 3 | 0 | 0 | 145 | 1 | 79 | 66 | 144 | 1 | 0 | 15 | 13 | 11575.47 | 413.41 | 7925.68 | -2251.15 | 4852.02 |
| 2025-11 | 30 | 2 | 0 | 0 | 167 | 0 | 90 | 77 | 167 | 0 | 0 | 10 | 18 | -715.43 | -25.55 | 5393.63 | -3602.18 | 7444.31 |
| 2025-12 | 31 | 1 | 0 | 0 | 146 | 0 | 81 | 65 | 146 | 0 | 0 | 14 | 16 | 940.72 | 31.36 | 4836.85 | -3415.91 | 10247.38 |
| 2026-01 | 31 | 3 | 0 | 0 | 161 | 0 | 80 | 81 | 161 | 0 | 0 | 11 | 17 | 1290.67 | 46.10 | 4594.21 | -1965.74 | 6251.88 |
| 2026-02 | 28 | 4 | 0 | 0 | 124 | 0 | 60 | 64 | 124 | 0 | 0 | 12 | 12 | 16767.41 | 698.64 | 9915.87 | -1933.32 | 8007.80 |
| 2026-03 | 31 | 5 | 0 | 0 | 153 | 0 | 82 | 71 | 153 | 0 | 0 | 12 | 14 | 4772.23 | 183.55 | 4384.59 | -2429.76 | 3862.34 |
| 2026-04 | 30 | 1 | 0 | 0 | 155 | 0 | 69 | 86 | 155 | 0 | 0 | 11 | 18 | -206.37 | -7.12 | 2216.63 | -1669.19 | 3625.57 |
| 2026-05 | 9 | 1 | 0 | 0 | 38 | 1 | 19 | 19 | 36 | 1 | 1 | 5 | 3 | 806.92 | 100.86 | 2064.85 | -1276.66 | 1791.47 |

## Gap Events / Exceptions

- `2025-10-25 14:00:00+00:00` -> `2025-10-25 21:00:00+00:00`: `6` missing candles; active trade = `YES`. Missing 6 candle(s) between 2025-10-25 14:00:00+00:00 and 2025-10-25 21:00:00+00:00; resumed on next available row.
- `2026-05-08 00:00:00+00:00` -> `2026-05-08 08:00:00+00:00`: `7` missing candles; active trade = `YES`. Missing 7 candle(s) between 2026-05-08 00:00:00+00:00 and 2026-05-08 08:00:00+00:00; resumed on next available row.

## Output Files

- `btc/results/btc_ma_continuous_multi_timeframe_20260510_012605/1h_ma24/trades.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_20260510_012605/1h_ma24/gap_events.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_20260510_012605/1h_ma24/daywise_summary.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_20260510_012605/1h_ma24/monthly_summary.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_20260510_012605/1h_ma24/yearly_summary.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_20260510_012605/1h_ma24/summary.json`
- `btc/results/btc_ma_continuous_multi_timeframe_20260510_012605/1h_ma24/summary.md`
- `btc/results/btc_ma_continuous_multi_timeframe_20260510_012605/1h_ma24/backtest.log`

## Remarks

- The one-time activation threshold is applied only on the first candidate UTC date.
- Opposite signals are ignored while a position is live; only the trailing SMA stop or a gap flat can close the trade.
- The entry candle itself cannot stop a newly opened position.
- Daywise results are grouped by realized exit date in UTC; held-only dates are preserved separately.
- Monthly and yearly results are derived from daywise realized P&L in points.
