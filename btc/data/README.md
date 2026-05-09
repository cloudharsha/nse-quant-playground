# BTC Data Directory

This directory contains historical BTC-USD intraday data with technical indicators.

## Data Files

Each CSV file contains OHLCV (Open, High, Low, Close, Volume) data plus the
same technical indicators used across the repo.

### File Naming Convention

`BTCUSD_data_{interval}.csv`

Examples:

- `BTCUSD_data_15m.csv`
- `BTCUSD_data_30m.csv`
- `BTCUSD_data_1h.csv`

## Data Columns

- `Date`
- `Open`
- `High`
- `Low`
- `Close`
- `Volume`
- `RSI`
- `MACD`
- `MACD_Signal`
- `MACD_Histogram`
- `BB_Upper`
- `BB_Middle`
- `BB_Lower`
- `ATR`
- `Stoch_K`
- `Stoch_D`
- `SMA_20`
- `SMA_50`
- `EMA_12`
- `EMA_26`
- `Price_Change`
- `Price_Change_Pct`
- `Volume_SMA`

## Data Specifications

- **Instrument**: BTC-USD
- **Time Period**: Last 1 year
- **Timeframes**: 15-minute, 30-minute, and 1-hour candles
- **Time Zone**: UTC
- **Data Source**: Coinbase Exchange public candles API
- **Update Frequency**: On demand

## Notes

- `15m` is the canonical fetched dataset
- `30m` and `1h` are derived from the canonical `15m` candles
- Technical indicators are calculated after each timeframe is finalized
- Rows with warmup `NaN` indicator values are removed before saving
