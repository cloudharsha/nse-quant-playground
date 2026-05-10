# BTC Local Multi-Timeframe 2R Target + Trailing MA Stop Capital Backtest

## Strategy Details

- Results are written under `btc/results`.
- Tested mappings:
  - `15m` with `MA 96`
  - `30m` with `MA 48`
  - `1h` with `MA 24`
- Fixed trade notional: `$1000000.00` per trade across all timeframes.
- Target is fixed at `2.00R` from the entry-to-initial-stop distance.
- Entry requires price to be within `0.50%` of the moving average.
- Same-candle stop/target ambiguity uses `stop_first`.
- Same-candle reversal after target is allowed only if the signal flips and the gap filter passes.
- No brokerage, slippage, borrow cost, or compounding position sizing is modeled.

## Timeframe Comparison

| Timeframe | MA | Date Range | Gaps | Trades | Targets | Stops | Gap Exits | Win Rate % | Total Points | Gross PnL USD | Ending Equity | Max DD USD | Max DD % |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 15m | 96 | 2021-05-11 -> 2026-05-10 | 8 | 24147 | 6175 | 17967 | 4 | 25.8583 | -90774.96 | -1757382.79 | -757382.79 | 1913988.55 | 183.6390 |
| 30m | 48 | 2021-05-12 -> 2026-05-10 | 8 | 16291 | 4005 | 12281 | 4 | 24.9524 | -117042.90 | -2237727.27 | -1237727.27 | 2278451.60 | 227.8452 |
| 1h | 24 | 2021-05-13 -> 2026-05-10 | 8 | 10706 | 2506 | 8195 | 4 | 23.7811 | -113316.37 | -2049407.24 | -1049407.24 | 2116360.86 | 210.1600 |

## Per-Timeframe Output Folders

- `15m`: `btc/results/btc_ma_target_trailing_multi_timeframe_capital_smoke_full/15m_ma96` (MA 96, gaps 8)
- `30m`: `btc/results/btc_ma_target_trailing_multi_timeframe_capital_smoke_full/30m_ma48` (MA 48, gaps 8)
- `1h`: `btc/results/btc_ma_target_trailing_multi_timeframe_capital_smoke_full/1h_ma24` (MA 24, gaps 8)

## Output Files

- `btc/results/btc_ma_target_trailing_multi_timeframe_capital_smoke_full/timeframe_summary.csv`
- `btc/results/btc_ma_target_trailing_multi_timeframe_capital_smoke_full/summary.json`
- `btc/results/btc_ma_target_trailing_multi_timeframe_capital_smoke_full/summary.md`
- `btc/results/btc_ma_target_trailing_multi_timeframe_capital_smoke_full/run_config.json`

## Remarks

- All timestamps and grouping are UTC.
- Gap handling is consistent across all selected timeframes: flat gaps log an event; live gaps force an exit at the last known boundary before the gap.
