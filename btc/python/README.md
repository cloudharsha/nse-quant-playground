# BTC Python Scripts Directory

This directory contains Python scripts for fetching BTC-USD data and running
BTC-specific backtests.

## Available Scripts

### `fetch_btc_intraday.py`

Fetches five years of BTC-USD intraday candles and calculates the same technical
indicators used by the other asset modules in this repo.

#### Features

- **Five-year BTC-USD history**: pulls a canonical 15-minute series for the last 1,825 days
- **Multiple timeframes**: writes 15-minute, 30-minute, and 1-hour CSV files
- **Coinbase-backed collection**: uses Coinbase Exchange public candles instead of `yfinance`
- **Consistent indicators**: computes RSI, MACD, Bollinger Bands, ATR, stochastic, moving averages, and price/volume metrics
- **Atomic CSV writes**: stages outputs first, then replaces the final files only after a successful full run

#### Usage

```bash
cd btc/python
python fetch_btc_intraday.py
```

#### Provider Choice

`yfinance` does not provide a true multi-year `BTC-USD` history for `15m` and `30m`
intervals. This script uses Coinbase Exchange public candles for the canonical
15-minute series, then derives:

- `30m` from grouped `15m` candles
- `1h` from grouped `15m` candles

#### Output

- `../data/BTCUSD_data_15m.csv`
- `../data/BTCUSD_data_30m.csv`
- `../data/BTCUSD_data_1h.csv`

#### Dependencies

```bash
pip install -r requirements.txt
```

#### Notes

- Timestamps are stored in UTC
- The script only writes closed candles
- All three outputs share a consistent five-year source range

### `btc_ma_continuous_trailing_multi_timeframe.py`

Runs the BTC continuous trailing-MA backtest locally from the `btc/` module and
writes results into `btc/results`.

#### Features

- **BTC-local workflow**: reads only `btc/data` and writes only `btc/results`
- **Multiple timeframe tests in one run**:
  - `15m` with `MA 96`
  - `30m` with `MA 48`
  - `1h` with `MA 24`
- **Continuous carry logic**: positions stay open until MA stop, data-gap exit, or end of data
- **UTC-aware activation**: supports a one-time initial start time for the first candidate day
- **Per-timeframe outputs**: writes detailed trade, gap, daywise, monthly, yearly, JSON, Markdown, and log files per timeframe

#### Usage

```bash
cd btc/python
python btc_ma_continuous_trailing_multi_timeframe.py
```

Optional examples:

```bash
# Run only 30m and 1h
python btc_ma_continuous_trailing_multi_timeframe.py --timeframes 30m 1h

# Start evaluation from 14:30 UTC on the first candidate date
python btc_ma_continuous_trailing_multi_timeframe.py --initial-start-time 14:30
```

#### Output

- Run folders are created in `../results/`
- Each run writes a top-level timeframe comparison summary
- Each tested timeframe gets its own subdirectory such as:
  - `15m_ma96/`
  - `30m_ma48/`
  - `1h_ma24/`

#### Notes

- Uses existing BTC CSVs from `../data/`
- Ignores precomputed moving averages in the CSV and computes fresh day-average MAs from raw closes
- Leaves earlier experimental BTC outputs under `common-strategies/` untouched

### `btc_ma_continuous_trailing_multi_timeframe_capital.py`

Runs the same BTC continuous trailing-MA strategy as the point-based script, but
sizes every trade to a fixed USD notional and tracks realized equity.

#### Features

- **Same trade engine**: reuses the existing BTC MA signal, stop, gap, and end-of-data logic
- **Fixed capital deployment**: uses `$1,000,000` notional per trade by default
- **Multiple timeframe tests in one run**:
  - `15m` with `MA 96`
  - `30m` with `MA 48`
  - `1h` with `MA 24`
- **Dual reporting**: keeps raw point metrics and adds USD P&L, BTC quantity, equity, and drawdown outputs
- **Equity curve export**: writes `equity_curve.csv` for each tested timeframe

#### Usage

```bash
cd btc/python
python btc_ma_continuous_trailing_multi_timeframe_capital.py
```

Optional examples:

```bash
# Run only 1h with a different fixed trade notional
python btc_ma_continuous_trailing_multi_timeframe_capital.py --timeframes 1h --capital 500000

# Start evaluation from 14:30 UTC on the first candidate date
python btc_ma_continuous_trailing_multi_timeframe_capital.py --initial-start-time 14:30
```

#### Output

- Run folders are created in `../results/`
- Default run names look like `btc_ma_continuous_multi_timeframe_capital_YYYYMMDD_HHMMSS`
- Each tested timeframe gets its own subdirectory such as:
  - `15m_ma96/`
  - `30m_ma48/`
  - `1h_ma24/`
- Each timeframe writes:
  - `trades.csv`
  - `gap_events.csv`
  - `daywise_summary.csv`
  - `monthly_summary.csv`
  - `yearly_summary.csv`
  - `equity_curve.csv`
  - `summary.json`
  - `summary.md`
  - `backtest.log`

#### Notes

- Uses the existing BTC CSVs from `../data/`
- Keeps trade and gap parity with the point-based BTC MA backtest
- Uses fixed-notional sizing, not compounding position sizing
- Assumes no brokerage, slippage, or borrow costs

### `btc_ma_target_trailing_multi_timeframe_capital.py`

Runs a BTC multi-timeframe MA strategy with fixed-notional capital, a trailing
MA stop, and a fixed `2R` target from the initial entry-to-stop distance.

#### Features

- **Fixed-notional capital model**: uses `$1,000,000` notional per trade by default
- **Multiple timeframe tests in one run**:
  - `15m` with `MA 96`
  - `30m` with `MA 48`
  - `1h` with `MA 24`
- **Entry gap filter**: only enters when the close is within `0.5%` of the moving average
- **Target + trailing stop**: target is fixed at `2R`, while the stop continues to trail with the MA
- **Conservative intrabar handling**: if stop and target are both touched in the same candle, the stop is assumed first
- **Capital reporting**: writes points, USD P&L, equity, drawdown, and equity-curve outputs

#### Usage

```bash
cd btc/python
python btc_ma_target_trailing_multi_timeframe_capital.py
```

Optional examples:

```bash
# Run only 30m and 1h
python btc_ma_target_trailing_multi_timeframe_capital.py --timeframes 30m 1h

# Start evaluation from 14:30 UTC on the first candidate date
python btc_ma_target_trailing_multi_timeframe_capital.py --initial-start-time 14:30
```

#### Output

- Run folders are created in `../results/`
- Default run names look like `btc_ma_target_trailing_multi_timeframe_capital_YYYYMMDD_HHMMSS`
- Each tested timeframe gets its own subdirectory such as:
  - `15m_ma96/`
  - `30m_ma48/`
  - `1h_ma24/`
- Each timeframe writes:
  - `trades.csv`
  - `gap_events.csv`
  - `daywise_summary.csv`
  - `monthly_summary.csv`
  - `yearly_summary.csv`
  - `equity_curve.csv`
  - `summary.json`
  - `summary.md`
  - `backtest.log`

#### Notes

- Uses the existing BTC CSVs from `../data/`
- Keeps the same fixed-capital accounting shape as the BTC capital script
- Same-candle reversal after a target is allowed only if the signal flips and the entry gap filter passes
- Assumes no brokerage, slippage, or borrow costs

### `btc_ma_target_trailing_multi_timeframe_capital_multi_reward.py`

Runs the same BTC target + trailing MA stop strategy as the `2R` script, but
tests multiple reward multiples in one run and writes a combined comparison
summary.

#### Features

- **Fixed-notional capital model**: uses `$1,000,000` notional per trade by default
- **Multiple timeframe tests in one run**:
  - `15m` with `MA 96`
  - `30m` with `MA 48`
  - `1h` with `MA 24`
- **Multiple reward targets**: defaults to testing `3R`, `4R`, and `5R` in a single run
- **Entry gap filter**: only enters when the close is within `0.5%` of the moving average
- **Target + trailing stop**: target is fixed per selected reward multiple, while the stop continues to trail with the MA
- **Combined comparison export**: writes both `timeframe_summary.csv` and `timeframe_target_summary.csv` at the run root

#### Usage

```bash
cd btc/python
python btc_ma_target_trailing_multi_timeframe_capital_multi_reward.py
```

Optional examples:

```bash
# Test only 3R and 5R on the 1h timeframe
python btc_ma_target_trailing_multi_timeframe_capital_multi_reward.py --timeframes 1h --target-levels 3 5

# Start evaluation from 14:30 UTC on the first candidate date
python btc_ma_target_trailing_multi_timeframe_capital_multi_reward.py --initial-start-time 14:30
```

#### Output

- Run folders are created in `../results/`
- Default run names look like `btc_ma_target_trailing_multi_timeframe_capital_multi_reward_YYYYMMDD_HHMMSS`
- Each timeframe/target combination gets its own subdirectory such as:
  - `15m_ma96_rr3/`
  - `30m_ma48_rr4/`
  - `1h_ma24_rr5/`
- Each timeframe/target folder writes:
  - `trades.csv`
  - `gap_events.csv`
  - `daywise_summary.csv`
  - `monthly_summary.csv`
  - `yearly_summary.csv`
  - `equity_curve.csv`
  - `summary.json`
  - `summary.md`
  - `backtest.log`

#### Notes

- Uses the existing BTC CSVs from `../data/`
- Keeps the same fixed-capital accounting shape as the BTC capital scripts
- Same-candle stop/target ambiguity is handled with the conservative `stop_first` rule
- Assumes no brokerage, slippage, or borrow costs
