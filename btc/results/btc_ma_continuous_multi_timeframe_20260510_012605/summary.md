# BTC Local Multi-Timeframe Continuous MA Backtest

## Strategy Details

- Results are written under `btc/results`.
- Tested mappings:
  - `15m` with `MA 96`
  - `30m` with `MA 48`
  - `1h` with `MA 24`
- Earlier `common-strategies` BTC outputs were not used for this run and were left untouched.
- Each timeframe has its own subdirectory with detailed trades, gap events, daywise, monthly, yearly, and summary outputs.

## Timeframe Comparison

| Timeframe | MA | Date Range | First MA Row | Activation | Gaps | Trades | Win Rate % | Total Points | Avg Points | Max DD |
|---|---:|---|---|---|---:|---:|---:|---:|---:|---:|
| 15m | 96 | 2025-05-10 -> 2026-05-09 | 2025-05-11 07:00:00+00:00 | 2025-05-10 07:15:00+00:00 | 2 | 3590 | 10.45 | 37528.18 | 10.45 | 17745.14 |
| 30m | 48 | 2025-05-10 -> 2026-05-09 | 2025-05-11 19:00:00+00:00 | 2025-05-10 19:30:00+00:00 | 2 | 2561 | 12.22 | 39496.32 | 15.42 | 15484.10 |
| 1h | 24 | 2025-05-11 -> 2026-05-09 | 2025-05-12 19:00:00+00:00 | 2025-05-11 20:00:00+00:00 | 2 | 1825 | 14.08 | 26289.22 | 14.41 | 17209.11 |

## Per-Timeframe Output Folders

- `15m`: `btc/results/btc_ma_continuous_multi_timeframe_20260510_012605/15m_ma96` (MA 96, gaps 2)
- `30m`: `btc/results/btc_ma_continuous_multi_timeframe_20260510_012605/30m_ma48` (MA 48, gaps 2)
- `1h`: `btc/results/btc_ma_continuous_multi_timeframe_20260510_012605/1h_ma24` (MA 24, gaps 2)

## Output Files

- `btc/results/btc_ma_continuous_multi_timeframe_20260510_012605/timeframe_summary.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_20260510_012605/summary.json`
- `btc/results/btc_ma_continuous_multi_timeframe_20260510_012605/summary.md`
- `btc/results/btc_ma_continuous_multi_timeframe_20260510_012605/run_config.json`

## Remarks

- The multi-timeframe BTC-local workflow supersedes the placement of earlier BTC backtests under `common-strategies` for future runs.
- All timestamps and grouping are UTC.
- Accounting is in raw points only.
- Gap handling is consistent across all selected timeframes: flat gaps log an event; live gaps force an exit at the last known boundary before the gap.
