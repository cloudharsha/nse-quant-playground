# BTC Local Multi-Timeframe Multi-Reward Target + Trailing MA Stop Capital Backtest

## Strategy Details

- Results are written under `btc/results`.
- Tested mappings:
  - `15m` with `MA 96`
  - `30m` with `MA 48`
  - `1h` with `MA 24`
- Target levels tested: `3R, 4R, 5R`.
- Fixed trade notional: `$1000000.00` per trade across all timeframes.
- Each trade uses a fixed target based on the selected reward multiple and trails the MA stop until exit.
- Entry requires price to be within `0.5%` of the moving average.
- Same-candle stop/target ambiguity uses `stop_first`.
- Same-candle reversal after target is allowed only if the signal flips and the gap filter passes.
- No brokerage, slippage, borrow cost, or compounding position sizing is modeled.

## Timeframe Comparison

| Timeframe | MA | Target | Date Range | Gaps | Trades | Targets | Stops | Gap Exits | Win Rate % | Total Points | Gross PnL USD | Ending Equity | Max DD USD | Max DD % |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 15m | 96 | 3R | 2025-05-15 -> 2025-05-20 | 0 | 79 | 19 | 60 | 0 | 24.0506 | 1752.41 | 16881.01 | 1016881.01 | 26150.49 | 2.5663 |
| 15m | 96 | 4R | 2025-05-15 -> 2025-05-21 | 0 | 75 | 14 | 60 | 0 | 22.6667 | 2769.37 | 26604.18 | 1026604.18 | 23433.22 | 2.3157 |
| 15m | 96 | 5R | 2025-05-15 -> 2025-05-21 | 0 | 74 | 13 | 60 | 0 | 22.9730 | 3117.93 | 29944.60 | 1029944.60 | 18555.85 | 1.8275 |
| 30m | 48 | 3R | 2025-05-15 -> 2025-05-20 | 0 | 57 | 13 | 44 | 0 | 22.8070 | -92.09 | -676.42 | 999323.58 | 28230.95 | 2.7795 |
| 30m | 48 | 4R | 2025-05-15 -> 2025-05-20 | 0 | 54 | 9 | 45 | 0 | 20.3704 | 280.64 | 2812.76 | 1002812.76 | 23393.68 | 2.3294 |
| 30m | 48 | 5R | 2025-05-15 -> 2025-05-20 | 0 | 52 | 6 | 46 | 0 | 19.2308 | -1271.30 | -12153.10 | 987846.90 | 28034.24 | 2.7888 |
| 1h | 24 | 3R | 2025-05-15 -> 2025-05-20 | 0 | 37 | 8 | 29 | 0 | 24.3243 | -558.39 | -5272.00 | 994728.00 | 31678.73 | 3.1282 |
| 1h | 24 | 4R | 2025-05-15 -> 2025-05-20 | 0 | 35 | 6 | 29 | 0 | 25.7143 | 112.09 | 1073.59 | 1001073.59 | 27549.81 | 2.7548 |
| 1h | 24 | 5R | 2025-05-15 -> 2025-05-20 | 0 | 35 | 4 | 31 | 0 | 22.8571 | -1715.55 | -16522.80 | 983477.20 | 26343.41 | 2.6342 |

## Per-Timeframe Output Folders

- `15m 3R`: `btc/results/btc_ma_target_trailing_multi_reward_tmp/15m_ma96_rr3` (MA 96, gaps 0)
- `15m 4R`: `btc/results/btc_ma_target_trailing_multi_reward_tmp/15m_ma96_rr4` (MA 96, gaps 0)
- `15m 5R`: `btc/results/btc_ma_target_trailing_multi_reward_tmp/15m_ma96_rr5` (MA 96, gaps 0)
- `30m 3R`: `btc/results/btc_ma_target_trailing_multi_reward_tmp/30m_ma48_rr3` (MA 48, gaps 0)
- `30m 4R`: `btc/results/btc_ma_target_trailing_multi_reward_tmp/30m_ma48_rr4` (MA 48, gaps 0)
- `30m 5R`: `btc/results/btc_ma_target_trailing_multi_reward_tmp/30m_ma48_rr5` (MA 48, gaps 0)
- `1h 3R`: `btc/results/btc_ma_target_trailing_multi_reward_tmp/1h_ma24_rr3` (MA 24, gaps 0)
- `1h 4R`: `btc/results/btc_ma_target_trailing_multi_reward_tmp/1h_ma24_rr4` (MA 24, gaps 0)
- `1h 5R`: `btc/results/btc_ma_target_trailing_multi_reward_tmp/1h_ma24_rr5` (MA 24, gaps 0)

## Output Files

- `btc/results/btc_ma_target_trailing_multi_reward_tmp/timeframe_summary.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/timeframe_target_summary.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/summary.json`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/summary.md`
- `btc/results/btc_ma_target_trailing_multi_reward_tmp/run_config.json`

## Remarks

- All timestamps and grouping are UTC.
- Gap handling is consistent across all selected timeframes: flat gaps log an event; live gaps force an exit at the last known boundary before the gap.
