# BTC 15m MA96 5R Target + Trailing MA Stop Backtest

## Strategy Details

- Dataset: `btc/data/BTCUSD_data_15m.csv`
- Tested UTC date range: `2025-05-15` through `2025-05-21`
- Signal source: BTC-USD 15m close
- Initial activation: `2025-05-15 00:00:00+00:00` (one-time UTC activation threshold)
- Entry rule: close above SMA -> long, close below SMA -> short, and entry requires close within `0.5%` of the SMA.
- Target rule: fixed `5R` target from the entry-to-initial-MA-stop distance.
- Stop rule: the active stop uses the carried-forward moving average and trails with each completed candle if no exit occurs.
- Ambiguous same-candle stop/target handling: `stop_first`.
- Post-target rule: same-candle reversal is allowed if the signal flips across the MA and the entry gap filter passes; same-direction same-candle re-entry is blocked.
- Gap rule: force flat at the last known boundary before a gap, then resume on the first post-gap candle and allow a new entry only after that candle completes.
- Accounting: fixed `$1000000.00` notional per trade, no costs, no compounding position sizing, and points/USD metrics reported together.

## Data Notes

- First CSV row: `2021-05-11 19:00:00+00:00`
- First MA-usable row: `2021-05-12 18:45:00+00:00`
- Source rows loaded: `175072`
- Rows inside requested date filter: `576`
- Rows processed after activation: `576`
- Gap events detected in this run: `0`

## Overall Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Targets | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Overall | 7 | 0 | 0 | 0 | 74 | 0 | 13 | 60 | 0 | 1 | 5 | 2 | 3117.93 | 29944.60 | 1029944.61 | 8929.77 | 0.8674 |

- Total trades: `74`
- Target exits: `13`
- Stop exits: `60`
- Gap exits: `0`
- Win rate: `22.9730%`
- Starting capital: `$1000000.00`
- Ending equity: `$1029944.60`
- Gross PnL USD: `$29944.60`
- Total return: `2.9945%`
- Max drawdown: `$18555.85` (`1.8275%`)

## Yearly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Targets | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025 | 7 | 0 | 0 | 0 | 74 | 0 | 13 | 60 | 0 | 1 | 5 | 2 | 3117.93 | 29944.60 | 1029944.61 | 8929.77 | 0.8674 |

## Monthly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Targets | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025-05 | 7 | 0 | 0 | 0 | 74 | 0 | 13 | 60 | 0 | 1 | 5 | 2 | 3117.93 | 29944.60 | 1029944.61 | 8929.77 | 0.8674 |

## Gap Events / Exceptions

- None

## Output Files

- `btc/results/btc_ma_target_trailing_multi_reward_tmp/15m_ma96_rr5/trades.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/15m_ma96_rr5/gap_events.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/15m_ma96_rr5/daywise_summary.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/15m_ma96_rr5/monthly_summary.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/15m_ma96_rr5/yearly_summary.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/15m_ma96_rr5/equity_curve.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/15m_ma96_rr5/summary.json`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/15m_ma96_rr5/summary.md`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/15m_ma96_rr5/backtest.log`

## Remarks

- The one-time activation threshold is applied only on the first candidate UTC date.
- The entry candle itself cannot exit a newly opened position.
- Daywise results are grouped by realized exit date in UTC; held-only dates are preserved separately.
- Monthly and yearly drawdowns are period-local from day-ending equity; overall drawdown is full-run.
