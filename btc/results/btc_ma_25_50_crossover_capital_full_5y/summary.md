# BTC 15m 25/50 MA Crossover Capital Backtest

## Strategy Details

- Results are written under `btc/results`.
- Timeframe: `15m`
- MA pair: `25/50`
- Fixed trade notional: `$100000.00` per trade.
- Positioning is symmetric: bullish cross = long, bearish cross = short.
- No brokerage, slippage, borrow cost, or compounding position sizing is modeled.

## Summary

| Timeframe | MA Pair | Date Range | Gaps | Trades | Win Rate % | Total Points | Gross PnL USD | Ending Equity | Max DD USD | Max DD % |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 15m | 25/50 | 2021-05-11 -> 2026-05-10 | 8 | 4183 | 35.8116 | 28908.75 | 86599.46 | 186599.46 | 65720.49 | 43.0242 |

## Output Folder

- `btc/results/btc_ma_25_50_crossover_capital_full_5y/15m_ma25_50`

## Output Files

- `btc/results/btc_ma_25_50_crossover_capital_full_5y/timeframe_summary.csv`
- `btc/results/btc_ma_25_50_crossover_capital_full_5y/summary.json`
- `btc/results/btc_ma_25_50_crossover_capital_full_5y/summary.md`
- `btc/results/btc_ma_25_50_crossover_capital_full_5y/run_config.json`

## Remarks

- All timestamps and grouping are UTC.
- Gap handling is conservative: live positions are flattened at the last known boundary before a gap, then crossover detection restarts after the next completed post-gap candle.
