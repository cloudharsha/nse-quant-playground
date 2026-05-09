# BTC Python Scripts Directory

This directory contains Python scripts for fetching BTC-USD data and running
BTC-specific backtests.

## Available Scripts

### `fetch_btc_intraday.py`

Fetches one year of BTC-USD intraday candles and calculates the same technical
indicators used by the other asset modules in this repo.

#### Features

- **One-year BTC-USD history**: pulls a canonical 15-minute series for the last 365 days
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

`yfinance` does not provide a true one-year `BTC-USD` history for `15m` and `30m`
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
- All three outputs share a consistent one-year source range

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
