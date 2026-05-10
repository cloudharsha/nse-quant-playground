# BTC 15m MA96 Fixed-Notional Capital Backtest

## Strategy Details

- Dataset: `btc/data/BTCUSD_data_15m.csv`
- Tested UTC date range: `2025-05-15` through `2025-05-21`
- Signal source: BTC-USD 15m close
- Initial activation: `2025-05-15 00:00:00+00:00` (one-time UTC activation threshold)
- No routine day-end exit; positions carry continuously until stopped, forced flat on a data gap, or exited at end of data.
- MA rule: 96-SMA of 15m closes computed fresh from the BTC dataset
- Direction rule: close above SMA -> long; close below SMA -> short; equal -> no entry
- Stop rule: long exits when candle low touches the trailing SMA; short exits when candle high touches the trailing SMA
- Re-entry rule: after a stop, the same completed candle may immediately open a new trade if the signal remains valid.
- Gap rule: force flat at the last known boundary before a gap, then resume on the first post-gap candle and allow a new entry only after that candle completes.
- Accounting: fixed `$1000000.00` notional per trade, no costs, no compounding position sizing, and points/USD metrics reported together.

## Data Notes

- First CSV row: `2021-05-11 19:00:00+00:00`
- First MA-usable row: `2021-05-12 18:45:00+00:00`
- Source rows loaded: `175072`
- Rows inside requested date filter: `576`
- Rows processed after activation: `576`
- Gap events detected in this run: `0`

## Overall Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Overall | 7 | 0 | 0 | 0 | 63 | 0 | 3 | 4 | -2115.86 | -20344.54 | 979655.46 | 29745.44 | 2.9745 |

- Total trades: `63`
- Win rate: `15.8730%`
- Starting capital: `$1000000.00`
- Ending equity: `$979655.46`
- Gross PnL USD: `$-20344.54`
- Total return: `-2.0345%`
- Max drawdown: `$34868.14` (`3.4690%`)

## Yearly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025 | 7 | 0 | 0 | 0 | 63 | 0 | 3 | 4 | -2115.86 | -20344.54 | 979655.46 | 29745.44 | 2.9745 |

## Monthly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025-05 | 7 | 0 | 0 | 0 | 63 | 0 | 3 | 4 | -2115.86 | -20344.54 | 979655.46 | 29745.44 | 2.9745 |

## Gap Events / Exceptions

- None

## Output Files

- `btc/results/btc_ma_parity_capital_tmp/15m_ma96/trades.csv`
- `btc/results/btc_ma_parity_capital_tmp/15m_ma96/gap_events.csv`
- `btc/results/btc_ma_parity_capital_tmp/15m_ma96/daywise_summary.csv`
- `btc/results/btc_ma_parity_capital_tmp/15m_ma96/monthly_summary.csv`
- `btc/results/btc_ma_parity_capital_tmp/15m_ma96/yearly_summary.csv`
- `btc/results/btc_ma_parity_capital_tmp/15m_ma96/equity_curve.csv`
- `btc/results/btc_ma_parity_capital_tmp/15m_ma96/summary.json`
- `btc/results/btc_ma_parity_capital_tmp/15m_ma96/summary.md`
- `btc/results/btc_ma_parity_capital_tmp/15m_ma96/backtest.log`

## Remarks

- The one-time activation threshold is applied only on the first candidate UTC date.
- Opposite signals are ignored while a position is live; only the trailing SMA stop or a gap flat can close the trade.
- The entry candle itself cannot stop a newly opened position.
- Daywise results are grouped by realized exit date in UTC; held-only dates are preserved separately.
- Monthly and yearly drawdowns are period-local from day-ending equity; overall drawdown is full-run.
