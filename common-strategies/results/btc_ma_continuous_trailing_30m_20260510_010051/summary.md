# BTC 30m 48-SMA Continuous Trailing Backtest

## Strategy Details

- Dataset: `/mnt/c/Users/harsh/Desktop/workspace/git/nse-quant-playground/btc/data/BTCUSD_data_30m.csv`
- Tested UTC date range: `2025-05-10` through `2026-05-09`
- Signal source: BTC-USD 30-minute close
- Initial activation: `2025-05-10 19:30:00+00:00` (one-time UTC activation threshold from `--initial-start-time=00:00`)
- No routine day-end exit; positions carry continuously until stopped, forced flat on a data gap, or exited at end of data.
- MA rule: 48-SMA of 30-minute closes computed fresh from the BTC dataset
- Direction rule: close above SMA -> long; close below SMA -> short; equal -> no entry
- Stop rule: long exits when candle low touches the trailing SMA; short exits when candle high touches the trailing SMA
- Re-entry rule: after a stop, the same completed candle may immediately open a new trade if the signal remains valid.
- Gap rule: force flat at the last known boundary before a gap, then resume on the first post-gap candle and allow a new entry only after that candle completes.
- Accounting: points only; no brokerage, slippage, leverage, position sizing, or currency conversion.

## Data Notes

- First CSV row: `2025-05-10 19:30:00+00:00`
- First MA-usable row: `2025-05-11 19:00:00+00:00`
- Source rows loaded: `17446`
- Rows inside requested date filter: `17446`
- Rows processed after activation: `17446`
- Gap events detected in this run: `2`

## Overall Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Long | Short | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | Avg Points | Max Profit | Max Loss | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Overall | 365 | 35 | 1 | 0 | 2561 | 2 | 1322 | 1239 | 2558 | 2 | 1 | 133 | 196 | 39496.32 | 120.05 | 12276.35 | -4320.62 | 15067.29 |

- Total trades: `2561`
- Win rate: `12.22%`

## Yearly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Long | Short | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | Avg Points | Max Profit | Max Loss | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025 | 236 | 19 | 1 | 0 | 1666 | 1 | 890 | 776 | 1665 | 1 | 0 | 89 | 127 | 21773.33 | 100.80 | 7728.79 | -4320.62 | 15067.29 |
| 2026 | 129 | 16 | 0 | 0 | 895 | 1 | 432 | 463 | 893 | 1 | 1 | 44 | 69 | 17722.99 | 156.84 | 12276.35 | -3294.08 | 12729.07 |

## Monthly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Long | Short | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | Avg Points | Max Profit | Max Loss | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025-05 | 22 | 2 | 1 | 0 | 136 | 0 | 67 | 69 | 136 | 0 | 0 | 4 | 15 | -2416.88 | -127.20 | 3531.10 | -2415.75 | 9337.29 |
| 2025-06 | 30 | 3 | 0 | 0 | 240 | 0 | 127 | 113 | 240 | 0 | 0 | 9 | 18 | -4776.20 | -176.90 | 4280.49 | -2525.07 | 6355.44 |
| 2025-07 | 31 | 1 | 0 | 0 | 231 | 0 | 129 | 102 | 231 | 0 | 0 | 13 | 17 | 1268.45 | 42.28 | 6335.26 | -2703.94 | 12747.15 |
| 2025-08 | 31 | 2 | 0 | 0 | 220 | 0 | 109 | 111 | 220 | 0 | 0 | 12 | 17 | 3224.34 | 111.18 | 4483.48 | -2193.75 | 6141.75 |
| 2025-09 | 30 | 2 | 0 | 0 | 204 | 0 | 114 | 90 | 204 | 0 | 0 | 12 | 16 | 2064.51 | 73.73 | 3735.18 | -2337.36 | 5544.48 |
| 2025-10 | 31 | 4 | 0 | 0 | 201 | 1 | 114 | 87 | 200 | 1 | 0 | 13 | 14 | 12845.56 | 475.76 | 7728.79 | -2303.88 | 6264.07 |
| 2025-11 | 30 | 2 | 0 | 0 | 246 | 0 | 132 | 114 | 246 | 0 | 0 | 9 | 19 | 2771.99 | 99.00 | 5067.03 | -4320.62 | 7207.20 |
| 2025-12 | 31 | 3 | 0 | 0 | 188 | 0 | 98 | 90 | 188 | 0 | 0 | 17 | 11 | 6791.56 | 242.56 | 4736.34 | -3060.79 | 7870.11 |
| 2026-01 | 31 | 4 | 0 | 0 | 229 | 0 | 111 | 118 | 229 | 0 | 0 | 10 | 17 | -2100.92 | -77.81 | 3174.84 | -3294.08 | 6888.41 |
| 2026-02 | 28 | 5 | 0 | 0 | 182 | 0 | 84 | 98 | 182 | 0 | 0 | 9 | 14 | 12139.52 | 527.81 | 12276.35 | -2644.41 | 12729.07 |
| 2026-03 | 31 | 5 | 0 | 0 | 212 | 0 | 112 | 100 | 212 | 0 | 0 | 12 | 14 | 7026.09 | 270.23 | 4352.82 | -1924.17 | 3886.94 |
| 2026-04 | 30 | 1 | 0 | 0 | 222 | 0 | 99 | 123 | 222 | 0 | 0 | 10 | 19 | -1983.81 | -68.41 | 2174.03 | -1742.50 | 5362.05 |
| 2026-05 | 9 | 1 | 0 | 0 | 50 | 1 | 26 | 24 | 48 | 1 | 1 | 3 | 5 | 2642.11 | 330.26 | 2111.08 | -1213.38 | 1257.97 |

## Gap Events / Exceptions

- `2025-10-25 14:30:00+00:00` -> `2025-10-25 21:00:00+00:00`: `12` missing candles; active trade = `YES`. Missing 12 candle(s) between 2025-10-25 14:30:00+00:00 and 2025-10-25 21:00:00+00:00; resumed on next available row.
- `2026-05-08 01:00:00+00:00` -> `2026-05-08 08:00:00+00:00`: `13` missing candles; active trade = `YES`. Missing 13 candle(s) between 2026-05-08 01:00:00+00:00 and 2026-05-08 08:00:00+00:00; resumed on next available row.

## Output Files

- `/mnt/c/Users/harsh/Desktop/workspace/git/nse-quant-playground/common-strategies/results/btc_ma_continuous_trailing_30m_20260510_010051/trades.csv`
- `/mnt/c/Users/harsh/Desktop/workspace/git/nse-quant-playground/common-strategies/results/btc_ma_continuous_trailing_30m_20260510_010051/gap_events.csv`
- `/mnt/c/Users/harsh/Desktop/workspace/git/nse-quant-playground/common-strategies/results/btc_ma_continuous_trailing_30m_20260510_010051/daywise_summary.csv`
- `/mnt/c/Users/harsh/Desktop/workspace/git/nse-quant-playground/common-strategies/results/btc_ma_continuous_trailing_30m_20260510_010051/monthly_summary.csv`
- `/mnt/c/Users/harsh/Desktop/workspace/git/nse-quant-playground/common-strategies/results/btc_ma_continuous_trailing_30m_20260510_010051/yearly_summary.csv`
- `/mnt/c/Users/harsh/Desktop/workspace/git/nse-quant-playground/common-strategies/results/btc_ma_continuous_trailing_30m_20260510_010051/summary.json`
- `/mnt/c/Users/harsh/Desktop/workspace/git/nse-quant-playground/common-strategies/results/btc_ma_continuous_trailing_30m_20260510_010051/summary.md`
- `/mnt/c/Users/harsh/Desktop/workspace/git/nse-quant-playground/common-strategies/results/btc_ma_continuous_trailing_30m_20260510_010051/run_config.json`
- `/mnt/c/Users/harsh/Desktop/workspace/git/nse-quant-playground/common-strategies/results/btc_ma_continuous_trailing_30m_20260510_010051/backtest.log`

## Remarks

- The one-time activation threshold is applied only on the first candidate UTC date.
- Opposite signals are ignored while a position is live; only the trailing SMA stop or a gap flat can close the trade.
- The entry candle itself cannot stop a newly opened position.
- Daywise results are grouped by realized exit date in UTC; held-only dates are preserved separately.
- Monthly and yearly results are derived from daywise realized P&L in points.
