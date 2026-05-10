# BTC 1h MA24 2R Target + Trailing MA Stop Backtest

## Strategy Details

- Dataset: `btc/data/BTCUSD_data_1h.csv`
- Tested UTC date range: `2025-05-15` through `2025-05-20`
- Signal source: BTC-USD 1h close
- Initial activation: `2025-05-15 00:00:00+00:00` (one-time UTC activation threshold)
- Entry rule: close above SMA -> long, close below SMA -> short, and entry requires close within `0.50`% of the SMA.
- Target rule: fixed `2.00R` target from the entry-to-initial-MA-stop distance.
- Stop rule: the active stop uses the carried-forward moving average and trails with each completed candle if no exit occurs.
- Ambiguous same-candle stop/target handling: `stop_first`.
- Post-target rule: same-candle reversal is allowed if the signal flips across the MA and the entry gap filter passes; same-direction same-candle re-entry is blocked.
- Gap rule: force flat at the last known boundary before a gap, then resume on the first post-gap candle and allow a new entry only after that candle completes.
- Accounting: fixed `$1000000.00` notional per trade, no costs, no compounding position sizing, and points/USD metrics reported together.

## Data Notes

- First CSV row: `2021-05-13 08:00:00+00:00`
- First MA-usable row: `2021-05-14 07:00:00+00:00`
- Source rows loaded: `43724`
- Rows inside requested date filter: `144`
- Rows processed after activation: `144`
- Gap events detected in this run: `0`

## Overall Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Targets | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Overall | 6 | 0 | 0 | 0 | 41 | 0 | 14 | 27 | 0 | 0 | 4 | 2 | 2799.31 | 27299.16 | 1027299.14 | 7954.33 | 0.7683 |

- Total trades: `41`
- Target exits: `14`
- Stop exits: `27`
- Gap exits: `0`
- Win rate: `34.1463%`
- Starting capital: `$1000000.00`
- Ending equity: `$1027299.16`
- Gross PnL USD: `$27299.16`
- Total return: `2.7299%`
- Max drawdown: `$17251.02` (`1.6767%`)

## Yearly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Targets | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025 | 6 | 0 | 0 | 0 | 41 | 0 | 14 | 27 | 0 | 0 | 4 | 2 | 2799.31 | 27299.16 | 1027299.14 | 7954.33 | 0.7683 |

## Monthly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Targets | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025-05 | 6 | 0 | 0 | 0 | 41 | 0 | 14 | 27 | 0 | 0 | 4 | 2 | 2799.31 | 27299.16 | 1027299.14 | 7954.33 | 0.7683 |

## Gap Events / Exceptions

- None

## Output Files

- `btc/results/btc_ma_target_trailing_capital_tmp/1h_ma24/trades.csv`
- `btc/results/btc_ma_target_trailing_capital_tmp/1h_ma24/gap_events.csv`
- `btc/results/btc_ma_target_trailing_capital_tmp/1h_ma24/daywise_summary.csv`
- `btc/results/btc_ma_target_trailing_capital_tmp/1h_ma24/monthly_summary.csv`
- `btc/results/btc_ma_target_trailing_capital_tmp/1h_ma24/yearly_summary.csv`
- `btc/results/btc_ma_target_trailing_capital_tmp/1h_ma24/equity_curve.csv`
- `btc/results/btc_ma_target_trailing_capital_tmp/1h_ma24/summary.json`
- `btc/results/btc_ma_target_trailing_capital_tmp/1h_ma24/summary.md`
- `btc/results/btc_ma_target_trailing_capital_tmp/1h_ma24/backtest.log`

## Remarks

- The one-time activation threshold is applied only on the first candidate UTC date.
- The entry candle itself cannot exit a newly opened position.
- Daywise results are grouped by realized exit date in UTC; held-only dates are preserved separately.
- Monthly and yearly drawdowns are period-local from day-ending equity; overall drawdown is full-run.
