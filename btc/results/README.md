# BTC Results Directory

This directory contains BTC-specific backtest results, analysis outputs, and
performance metrics.

## Current Backtest Layout

BTC backtests now write timestamped run folders directly into this directory.

Example:

```text
results/
└── btc_ma_continuous_multi_timeframe_20260510_020000/
    ├── timeframe_summary.csv
    ├── summary.json
    ├── summary.md
    ├── run_config.json
    ├── 15m_ma96/
    ├── 30m_ma48/
    └── 1h_ma24/
```

Each timeframe subdirectory contains:

- `trades.csv`
- `gap_events.csv`
- `daywise_summary.csv`
- `monthly_summary.csv`
- `yearly_summary.csv`
- `summary.json`
- `summary.md`
- `backtest.log`

## Types of Results

- Per-timeframe trade logs
- Gap-event logs
- Daywise, monthly, and yearly summary CSVs
- Run configuration snapshots
- Machine-readable JSON summaries
- Human-readable Markdown summaries

## Notes

- BTC-local backtests are written here from `btc/python/`
- The preferred BTC workflow is now `btc/python` + `btc/results`
- Earlier BTC experiments under `common-strategies/results` are legacy outputs and are not used by the BTC-local multi-timeframe runner

## Current Status

This directory is expected to contain multiple timestamped BTC run folders over
time as strategies are tested and compared.
