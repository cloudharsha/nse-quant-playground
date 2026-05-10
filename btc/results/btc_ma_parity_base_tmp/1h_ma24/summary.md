# BTC 1h MA24 Continuous Trailing Backtest

## Strategy Details

- Dataset: `btc/data/BTCUSD_data_1h.csv`
- Tested UTC date range: `2025-05-15` through `2025-05-21`
- Signal source: BTC-USD 1h close
- Initial activation: `2025-05-15 00:00:00+00:00` (one-time UTC activation threshold)
- No routine day-end exit; positions carry continuously until stopped, forced flat on a data gap, or exited at end of data.
- MA rule: 24-SMA of 1h closes computed fresh from the BTC dataset
- Direction rule: close above SMA -> long; close below SMA -> short; equal -> no entry
- Stop rule: long exits when candle low touches the trailing SMA; short exits when candle high touches the trailing SMA
- Re-entry rule: after a stop, the same completed candle may immediately open a new trade if the signal remains valid.
- Gap rule: force flat at the last known boundary before a gap, then resume on the first post-gap candle and allow a new entry only after that candle completes.
- Accounting: points only; no brokerage, slippage, leverage, or position sizing.

## Data Notes

- First CSV row: `2021-05-13 08:00:00+00:00`
- First MA-usable row: `2021-05-14 07:00:00+00:00`
- Source rows loaded: `43724`
- Rows inside requested date filter: `144`
- Rows processed after activation: `144`
- Gap events detected in this run: `0`

## Overall Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Long | Short | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | Avg Points | Max Profit | Max Loss | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Overall | 7 | 0 | 0 | 0 | 35 | 0 | 19 | 16 | 34 | 0 | 1 | 1 | 6 | -5752.58 | -821.80 | 34.25 | -1969.22 | 5752.58 |

- Total trades: `35`
- Win rate: `17.14%`

## Yearly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Long | Short | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | Avg Points | Max Profit | Max Loss | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025 | 7 | 0 | 0 | 0 | 35 | 0 | 19 | 16 | 34 | 0 | 1 | 1 | 6 | -5752.58 | -821.80 | 34.25 | -1969.22 | 5752.58 |

## Monthly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Long | Short | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | Avg Points | Max Profit | Max Loss | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025-05 | 7 | 0 | 0 | 0 | 35 | 0 | 19 | 16 | 34 | 0 | 1 | 1 | 6 | -5752.58 | -821.80 | 34.25 | -1969.22 | 5752.58 |

## Gap Events / Exceptions

- None

## Output Files

- `btc/results/btc_ma_parity_base_tmp/1h_ma24/trades.csv`
- `btc/results/btc_ma_parity_base_tmp/1h_ma24/gap_events.csv`
- `btc/results/btc_ma_parity_base_tmp/1h_ma24/daywise_summary.csv`
- `btc/results/btc_ma_parity_base_tmp/1h_ma24/monthly_summary.csv`
- `btc/results/btc_ma_parity_base_tmp/1h_ma24/yearly_summary.csv`
- `btc/results/btc_ma_parity_base_tmp/1h_ma24/summary.json`
- `btc/results/btc_ma_parity_base_tmp/1h_ma24/summary.md`
- `btc/results/btc_ma_parity_base_tmp/1h_ma24/backtest.log`

## Remarks

- The one-time activation threshold is applied only on the first candidate UTC date.
- Opposite signals are ignored while a position is live; only the trailing SMA stop or a gap flat can close the trade.
- The entry candle itself cannot stop a newly opened position.
- Daywise results are grouped by realized exit date in UTC; held-only dates are preserved separately.
- Monthly and yearly results are derived from daywise realized P&L in points.
