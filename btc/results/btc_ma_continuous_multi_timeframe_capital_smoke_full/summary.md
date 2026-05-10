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
| 15m | 96 | 2021-05-11 -> 2026-05-10 | 8 | 19396 | 9.7185 | 93403.52 | 1930133.92 | 2930133.92 | 505031.52 | 29.0419 |
| 30m | 48 | 2021-05-12 -> 2026-05-10 | 8 | 13829 | 11.3096 | 75415.76 | 1591841.06 | 2591841.06 | 406032.31 | 28.5617 |
| 1h | 24 | 2021-05-13 -> 2026-05-10 | 8 | 9873 | 12.9241 | 41223.66 | 1180180.94 | 2180180.94 | 514131.32 | 40.1173 |

## Per-Timeframe Output Folders

- `15m`: `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/15m_ma96` (MA 96, gaps 8)
- `30m`: `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/30m_ma48` (MA 48, gaps 8)
- `1h`: `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/1h_ma24` (MA 24, gaps 8)

## Output Files

- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/timeframe_summary.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/summary.json`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/summary.md`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/run_config.json`

## Remarks

- The capital backtest reuses the existing BTC MA trade engine to preserve trade/gap parity with the point-based script.
- All timestamps and grouping are UTC.
- Gap handling is consistent across all selected timeframes: flat gaps log an event; live gaps force an exit at the last known boundary before the gap.
