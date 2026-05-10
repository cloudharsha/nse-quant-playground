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
| 15m | 96 | 3R | 2021-05-11 -> 2026-05-10 | 8 | 22849 | 4577 | 18267 | 4 | 20.7668 | -40812.00 | -844079.71 | 155920.29 | 1253636.61 | 110.2491 |
| 15m | 96 | 4R | 2021-05-11 -> 2026-05-10 | 8 | 22059 | 3643 | 18411 | 4 | 17.6844 | -4334.40 | -313911.69 | 686088.31 | 924674.22 | 80.3004 |
| 15m | 96 | 5R | 2021-05-11 -> 2026-05-10 | 8 | 21586 | 3064 | 18516 | 5 | 15.8112 | 23948.72 | 302452.39 | 1302452.39 | 531620.26 | 46.6640 |
| 30m | 48 | 3R | 2021-05-12 -> 2026-05-10 | 8 | 15553 | 3022 | 12526 | 4 | 20.2469 | -65532.50 | -1147673.37 | -147673.37 | 1226357.99 | 120.3965 |
| 30m | 48 | 4R | 2021-05-12 -> 2026-05-10 | 8 | 15104 | 2444 | 12655 | 4 | 17.5781 | -7901.03 | -141248.32 | 858751.68 | 591083.43 | 50.8298 |
| 30m | 48 | 5R | 2021-05-12 -> 2026-05-10 | 8 | 14777 | 2021 | 12750 | 5 | 15.7474 | 3249.28 | 70338.80 | 1070338.80 | 492689.31 | 44.0782 |
| 1h | 24 | 3R | 2021-05-13 -> 2026-05-10 | 8 | 10318 | 1925 | 8388 | 4 | 19.6647 | -52896.34 | -866115.11 | 133884.89 | 1086468.23 | 101.8466 |
| 1h | 24 | 4R | 2021-05-13 -> 2026-05-10 | 8 | 10067 | 1540 | 8521 | 5 | 17.2743 | -27395.78 | -293329.96 | 706670.04 | 646187.45 | 55.4646 |
| 1h | 24 | 5R | 2021-05-13 -> 2026-05-10 | 8 | 9865 | 1246 | 8613 | 5 | 15.6209 | -21818.33 | -209733.58 | 790266.42 | 664391.80 | 54.4215 |

## Per-Timeframe Output Folders

- `15m 3R`: `btc/results/btc_ma_target_trailing_multi_reward_smoke_full/15m_ma96_rr3` (MA 96, gaps 8)
- `15m 4R`: `btc/results/btc_ma_target_trailing_multi_reward_smoke_full/15m_ma96_rr4` (MA 96, gaps 8)
- `15m 5R`: `btc/results/btc_ma_target_trailing_multi_reward_smoke_full/15m_ma96_rr5` (MA 96, gaps 8)
- `30m 3R`: `btc/results/btc_ma_target_trailing_multi_reward_smoke_full/30m_ma48_rr3` (MA 48, gaps 8)
- `30m 4R`: `btc/results/btc_ma_target_trailing_multi_reward_smoke_full/30m_ma48_rr4` (MA 48, gaps 8)
- `30m 5R`: `btc/results/btc_ma_target_trailing_multi_reward_smoke_full/30m_ma48_rr5` (MA 48, gaps 8)
- `1h 3R`: `btc/results/btc_ma_target_trailing_multi_reward_smoke_full/1h_ma24_rr3` (MA 24, gaps 8)
- `1h 4R`: `btc/results/btc_ma_target_trailing_multi_reward_smoke_full/1h_ma24_rr4` (MA 24, gaps 8)
- `1h 5R`: `btc/results/btc_ma_target_trailing_multi_reward_smoke_full/1h_ma24_rr5` (MA 24, gaps 8)

## Output Files

- `btc/results/btc_ma_target_trailing_multi_reward_smoke_full/timeframe_summary.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_smoke_full/timeframe_target_summary.csv`
- `btc/results/btc_ma_target_trailing_multi_reward_smoke_full/summary.json`
- `btc/results/btc_ma_target_trailing_multi_reward_smoke_full/summary.md`
- `btc/results/btc_ma_target_trailing_multi_reward_smoke_full/run_config.json`

## Remarks

- All timestamps and grouping are UTC.
- Gap handling is consistent across all selected timeframes: flat gaps log an event; live gaps force an exit at the last known boundary before the gap.
