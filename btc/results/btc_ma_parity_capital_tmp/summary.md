# BTC Local Multi-Timeframe Continuous MA Capital Backtest

## Strategy Details

- Results are written under `btc/results`.
- Tested mappings:
  - `15m` with `MA 96`
  - `30m` with `MA 48`
  - `1h` with `MA 24`
- Fixed trade notional: `$1000000.00` per trade across all timeframes.
- Accounting includes both raw points and realized USD/equity metrics.
- No brokerage, slippage, borrow cost, or compounding position sizing is modeled.
- Each timeframe has its own subdirectory with detailed trades, gap events, daywise, monthly, yearly, equity-curve, and summary outputs.

## Timeframe Comparison

| Timeframe | MA | Date Range | Gaps | Trades | Win Rate % | Total Points | Gross PnL USD | Ending Equity | Max DD USD | Max DD % |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 15m | 96 | 2025-05-15 -> 2025-05-21 | 0 | 63 | 15.8730 | -2115.86 | -20344.54 | 979655.46 | 34868.14 | 3.4690 |
| 30m | 48 | 2025-05-15 -> 2025-05-21 | 0 | 49 | 18.3673 | -3599.12 | -34495.12 | 965504.88 | 43958.52 | 4.3763 |
| 1h | 24 | 2025-05-15 -> 2025-05-21 | 0 | 35 | 17.1429 | -5752.58 | -54833.49 | 945166.51 | 54833.48 | 5.4833 |

## Per-Timeframe Output Folders

- `15m`: `btc/results/btc_ma_parity_capital_tmp/15m_ma96` (MA 96, gaps 0)
- `30m`: `btc/results/btc_ma_parity_capital_tmp/30m_ma48` (MA 48, gaps 0)
- `1h`: `btc/results/btc_ma_parity_capital_tmp/1h_ma24` (MA 24, gaps 0)

## Output Files

- `btc/results/btc_ma_parity_capital_tmp/timeframe_summary.csv`
- `btc/results/btc_ma_parity_capital_tmp/summary.json`
- `btc/results/btc_ma_parity_capital_tmp/summary.md`
- `btc/results/btc_ma_parity_capital_tmp/run_config.json`

## Remarks

- The capital backtest reuses the existing BTC MA trade engine to preserve trade/gap parity with the point-based script.
- All timestamps and grouping are UTC.
- Gap handling is consistent across all selected timeframes: flat gaps log an event; live gaps force an exit at the last known boundary before the gap.
