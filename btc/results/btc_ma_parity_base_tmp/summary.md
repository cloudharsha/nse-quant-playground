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
| 15m | 96 | 2025-05-15 -> 2025-05-21 | 2021-05-12 18:45:00+00:00 | 2025-05-15 00:00:00+00:00 | 0 | 63 | 15.87 | -2115.86 | -33.59 | 3641.25 |
| 30m | 48 | 2025-05-15 -> 2025-05-21 | 2021-05-13 07:00:00+00:00 | 2025-05-15 00:00:00+00:00 | 0 | 49 | 18.37 | -3599.12 | -73.45 | 4592.33 |
| 1h | 24 | 2025-05-15 -> 2025-05-21 | 2021-05-14 07:00:00+00:00 | 2025-05-15 00:00:00+00:00 | 0 | 35 | 17.14 | -5752.58 | -164.36 | 5752.58 |

## Per-Timeframe Output Folders

- `15m`: `btc/results/btc_ma_parity_base_tmp/15m_ma96` (MA 96, gaps 0)
- `30m`: `btc/results/btc_ma_parity_base_tmp/30m_ma48` (MA 48, gaps 0)
- `1h`: `btc/results/btc_ma_parity_base_tmp/1h_ma24` (MA 24, gaps 0)

## Output Files

- `btc/results/btc_ma_parity_base_tmp/timeframe_summary.csv`
- `btc/results/btc_ma_parity_base_tmp/summary.json`
- `btc/results/btc_ma_parity_base_tmp/summary.md`
- `btc/results/btc_ma_parity_base_tmp/run_config.json`

## Remarks

- The multi-timeframe BTC-local workflow supersedes the placement of earlier BTC backtests under `common-strategies` for future runs.
- All timestamps and grouping are UTC.
- Accounting is in raw points only.
- Gap handling is consistent across all selected timeframes: flat gaps log an event; live gaps force an exit at the last known boundary before the gap.
