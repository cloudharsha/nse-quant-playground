# BTC 30m MA48 4R Target + Trailing MA Stop Backtest

## Strategy Details

- Dataset: `btc/data/BTCUSD_data_30m.csv`
- Tested UTC date range: `2025-05-15` through `2025-05-20`
- Signal source: BTC-USD 30m close
- Initial activation: `2025-05-15 00:00:00+00:00` (one-time UTC activation threshold)
- Entry rule: close above SMA -> long, close below SMA -> short, and entry requires close within `0.5%` of the SMA.
- Target rule: fixed `4R` target from the entry-to-initial-MA-stop distance.
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
| Overall | 6 | 0 | 0 | 0 | 54 | 0 | 9 | 45 | 0 | 0 | 2 | 4 | 280.64 | 2812.76 | 1002812.73 | 16792.59 | 1.6501 |

- Total trades: `54`
- Target exits: `9`
- Stop exits: `45`
- Gap exits: `0`
- Win rate: `20.3704%`
- Starting capital: `$1000000.00`
- Ending equity: `$1002812.76`
- Gross PnL USD: `$2812.76`
- Total return: `0.2813%`
- Max drawdown: `$23393.68` (`2.3294%`)

## Yearly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Targets | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025 | 6 | 0 | 0 | 0 | 54 | 0 | 9 | 45 | 0 | 0 | 2 | 4 | 280.64 | 2812.76 | 1002812.73 | 16792.59 | 1.6501 |

## Monthly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Targets | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025-05 | 6 | 0 | 0 | 0 | 54 | 0 | 9 | 45 | 0 | 0 | 2 | 4 | 280.64 | 2812.76 | 1002812.73 | 16792.59 | 1.6501 |

## Gap Events / Exceptions

- None

## Output Files

- `btc/results/btc_ma_target_trailing_multi_reward_tmp/30m_ma48_rr4/trades.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/30m_ma48_rr4/gap_events.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/30m_ma48_rr4/daywise_summary.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/30m_ma48_rr4/monthly_summary.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/30m_ma48_rr4/yearly_summary.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/30m_ma48_rr4/equity_curve.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/30m_ma48_rr4/summary.json`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/30m_ma48_rr4/summary.md`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/30m_ma48_rr4/backtest.log`

## Remarks

- The one-time activation threshold is applied only on the first candidate UTC date.
- The entry candle itself cannot exit a newly opened position.
- Daywise results are grouped by realized exit date in UTC; held-only dates are preserved separately.
- Monthly and yearly drawdowns are period-local from day-ending equity; overall drawdown is full-run.
