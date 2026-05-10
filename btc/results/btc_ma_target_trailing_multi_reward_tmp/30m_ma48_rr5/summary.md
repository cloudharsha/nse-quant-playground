# BTC 30m MA48 5R Target + Trailing MA Stop Backtest

## Strategy Details

- Dataset: `btc/data/BTCUSD_data_30m.csv`
- Tested UTC date range: `2025-05-15` through `2025-05-20`
- Signal source: BTC-USD 30m close
- Initial activation: `2025-05-15 00:00:00+00:00` (one-time UTC activation threshold)
- Entry rule: close above SMA -> long, close below SMA -> short, and entry requires close within `0.5%` of the SMA.
- Target rule: fixed `5R` target from the entry-to-initial-MA-stop distance.
- Stop rule: the active stop uses the carried-forward moving average and trails with each completed candle if no exit occurs.
- Ambiguous same-candle stop/target handling: `stop_first`.
- Post-target rule: same-candle reversal is allowed if the signal flips across the MA and the entry gap filter passes; same-direction same-candle re-entry is blocked.
- Gap rule: force flat at the last known boundary before a gap, then resume on the first post-gap candle and allow a new entry only after that candle completes.
- Accounting: fixed `$1000000.00` notional per trade, no costs, no compounding position sizing, and points/USD metrics reported together.

## Data Notes

- First CSV row: `2021-05-12 07:30:00+00:00`
- First MA-usable row: `2021-05-13 07:00:00+00:00`
- Source rows loaded: `87505`
- Rows inside requested date filter: `288`
- Rows processed after activation: `288`
- Gap events detected in this run: `0`

## Overall Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Targets | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Overall | 6 | 0 | 0 | 0 | 52 | 0 | 6 | 46 | 0 | 0 | 2 | 4 | -1271.30 | -12153.10 | 987846.89 | 20149.93 | 2.0150 |

- Total trades: `52`
- Target exits: `6`
- Stop exits: `46`
- Gap exits: `0`
- Win rate: `19.2308%`
- Starting capital: `$1000000.00`
- Ending equity: `$987846.90`
- Gross PnL USD: `$-12153.10`
- Total return: `-1.2153%`
- Max drawdown: `$28034.24` (`2.7888%`)

## Yearly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Targets | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025 | 6 | 0 | 0 | 0 | 52 | 0 | 6 | 46 | 0 | 0 | 2 | 4 | -1271.30 | -12153.10 | 987846.89 | 20149.93 | 2.0150 |

## Monthly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Targets | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025-05 | 6 | 0 | 0 | 0 | 52 | 0 | 6 | 46 | 0 | 0 | 2 | 4 | -1271.30 | -12153.10 | 987846.89 | 20149.93 | 2.0150 |

## Gap Events / Exceptions

- None

## Output Files

- `btc/results/btc_ma_target_trailing_multi_reward_tmp/30m_ma48_rr5/trades.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/30m_ma48_rr5/gap_events.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/30m_ma48_rr5/daywise_summary.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/30m_ma48_rr5/monthly_summary.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/30m_ma48_rr5/yearly_summary.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/30m_ma48_rr5/equity_curve.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/30m_ma48_rr5/summary.json`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/30m_ma48_rr5/summary.md`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/30m_ma48_rr5/backtest.log`

## Remarks

- The one-time activation threshold is applied only on the first candidate UTC date.
- The entry candle itself cannot exit a newly opened position.
- Daywise results are grouped by realized exit date in UTC; held-only dates are preserved separately.
- Monthly and yearly drawdowns are period-local from day-ending equity; overall drawdown is full-run.
