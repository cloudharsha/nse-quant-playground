# BTC 15m MA96 4R Target + Trailing MA Stop Backtest

## Strategy Details

- Dataset: `btc/data/BTCUSD_data_15m.csv`
- Tested UTC date range: `2025-05-15` through `2025-05-21`
- Signal source: BTC-USD 15m close
- Initial activation: `2025-05-15 00:00:00+00:00` (one-time UTC activation threshold)
- Entry rule: close above SMA -> long, close below SMA -> short, and entry requires close within `0.5%` of the SMA.
- Target rule: fixed `4R` target from the entry-to-initial-MA-stop distance.
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
| Overall | 7 | 0 | 0 | 0 | 75 | 0 | 14 | 60 | 0 | 1 | 5 | 2 | 2769.37 | 26604.18 | 1026604.19 | 18815.86 | 1.8621 |

- Total trades: `75`
- Target exits: `14`
- Stop exits: `60`
- Gap exits: `0`
- Win rate: `22.6667%`
- Starting capital: `$1000000.00`
- Ending equity: `$1026604.18`
- Gross PnL USD: `$26604.18`
- Total return: `2.6604%`
- Max drawdown: `$23433.22` (`2.3157%`)

## Yearly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Targets | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025 | 7 | 0 | 0 | 0 | 75 | 0 | 14 | 60 | 0 | 1 | 5 | 2 | 2769.37 | 26604.18 | 1026604.19 | 18815.86 | 1.8621 |

## Monthly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Targets | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025-05 | 7 | 0 | 0 | 0 | 75 | 0 | 14 | 60 | 0 | 1 | 5 | 2 | 2769.37 | 26604.18 | 1026604.19 | 18815.86 | 1.8621 |

## Gap Events / Exceptions

- None

## Output Files

- `btc/results/btc_ma_target_trailing_multi_reward_tmp/15m_ma96_rr4/trades.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/15m_ma96_rr4/gap_events.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/15m_ma96_rr4/daywise_summary.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/15m_ma96_rr4/monthly_summary.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/15m_ma96_rr4/yearly_summary.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/15m_ma96_rr4/equity_curve.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/15m_ma96_rr4/summary.json`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/15m_ma96_rr4/summary.md`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/15m_ma96_rr4/backtest.log`

## Remarks

- The one-time activation threshold is applied only on the first candidate UTC date.
- The entry candle itself cannot exit a newly opened position.
- Daywise results are grouped by realized exit date in UTC; held-only dates are preserved separately.
- Monthly and yearly drawdowns are period-local from day-ending equity; overall drawdown is full-run.
