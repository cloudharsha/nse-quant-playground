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
| 15m | 96 | 2025-05-15 -> 2025-05-20 | 0 | 83 | 23 | 60 | 0 | 27.7108 | 300.14 | 3064.28 | 1003064.28 | 31049.84 | 3.0239 |
| 30m | 48 | 2025-05-15 -> 2025-05-20 | 0 | 63 | 19 | 44 | 0 | 30.1587 | 892.70 | 9016.61 | 1009016.61 | 17168.58 | 1.6730 |
| 1h | 24 | 2025-05-15 -> 2025-05-20 | 0 | 41 | 14 | 27 | 0 | 34.1463 | 2799.31 | 27299.16 | 1027299.16 | 17251.02 | 1.6767 |

## Per-Timeframe Output Folders

- `15m`: `btc/results/btc_ma_target_trailing_capital_tmp/15m_ma96` (MA 96, gaps 0)
- `30m`: `btc/results/btc_ma_target_trailing_capital_tmp/30m_ma48` (MA 48, gaps 0)
- `1h`: `btc/results/btc_ma_target_trailing_capital_tmp/1h_ma24` (MA 24, gaps 0)

## Output Files

- `btc/results/btc_ma_target_trailing_capital_tmp/timeframe_summary.csv`
- `btc/results/btc_ma_target_trailing_capital_tmp/summary.json`
- `btc/results/btc_ma_target_trailing_capital_tmp/summary.md`
- `btc/results/btc_ma_target_trailing_capital_tmp/run_config.json`

## Remarks

- All timestamps and grouping are UTC.
- Gap handling is consistent across all selected timeframes: flat gaps log an event; live gaps force an exit at the last known boundary before the gap.
