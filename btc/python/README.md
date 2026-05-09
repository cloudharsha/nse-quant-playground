# BTC Python Scripts Directory

This directory contains Python scripts for fetching and processing BTC-USD data.

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
