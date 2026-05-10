# BTC 30m MA48 Fixed-Notional Capital Backtest

## Strategy Details

- Dataset: `btc/data/BTCUSD_data_30m.csv`
- Tested UTC date range: `2025-05-15` through `2025-05-21`
- Signal source: BTC-USD 30m close
- Initial activation: `2025-05-15 00:00:00+00:00` (one-time UTC activation threshold)
- No routine day-end exit; positions carry continuously until stopped, forced flat on a data gap, or exited at end of data.
- MA rule: 48-SMA of 30m closes computed fresh from the BTC dataset
- Direction rule: close above SMA -> long; close below SMA -> short; equal -> no entry
- Stop rule: long exits when candle low touches the trailing SMA; short exits when candle high touches the trailing SMA
- Re-entry rule: after a stop, the same completed candle may immediately open a new trade if the signal remains valid.
- Gap rule: force flat at the last known boundary before a gap, then resume on the first post-gap candle and allow a new entry only after that candle completes.
- Accounting: fixed `$1000000.00` notional per trade, no costs, no compounding position sizing, and points/USD metrics reported together.

## Data Notes

- First CSV row: `2021-05-12 07:30:00+00:00`
- First MA-usable row: `2021-05-13 07:00:00+00:00`
- Source rows loaded: `87505`
- Rows inside requested date filter: `288`
- Rows processed after activation: `288`
- Gap events detected in this run: `0`

## Overall Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Overall | 7 | 0 | 0 | 0 | 49 | 0 | 2 | 5 | -3599.12 | -34495.12 | 965504.85 | 39489.89 | 3.9490 |

- Total trades: `49`
- Win rate: `18.3673%`
- Starting capital: `$1000000.00`
- Ending equity: `$965504.88`
- Gross PnL USD: `$-34495.12`
- Total return: `-3.4495%`
- Max drawdown: `$43958.52` (`4.3763%`)

## Yearly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025 | 7 | 0 | 0 | 0 | 49 | 0 | 2 | 5 | -3599.12 | -34495.12 | 965504.85 | 39489.89 | 3.9490 |

## Monthly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025-05 | 7 | 0 | 0 | 0 | 49 | 0 | 2 | 5 | -3599.12 | -34495.12 | 965504.85 | 39489.89 | 3.9490 |

## Gap Events / Exceptions

- None

## Output Files

- `btc/results/btc_ma_parity_capital_tmp/30m_ma48/trades.csv`
- `btc/results/btc_ma_parity_capital_tmp/30m_ma48/gap_events.csv`
- `btc/results/btc_ma_parity_capital_tmp/30m_ma48/daywise_summary.csv`
- `btc/results/btc_ma_parity_capital_tmp/30m_ma48/monthly_summary.csv`
- `btc/results/btc_ma_parity_capital_tmp/30m_ma48/yearly_summary.csv`
- `btc/results/btc_ma_parity_capital_tmp/30m_ma48/equity_curve.csv`
- `btc/results/btc_ma_parity_capital_tmp/30m_ma48/summary.json`
- `btc/results/btc_ma_parity_capital_tmp/30m_ma48/summary.md`
- `btc/results/btc_ma_parity_capital_tmp/30m_ma48/backtest.log`

## Remarks

- The one-time activation threshold is applied only on the first candidate UTC date.
- Opposite signals are ignored while a position is live; only the trailing SMA stop or a gap flat can close the trade.
- The entry candle itself cannot stop a newly opened position.
- Daywise results are grouped by realized exit date in UTC; held-only dates are preserved separately.
- Monthly and yearly drawdowns are period-local from day-ending equity; overall drawdown is full-run.
