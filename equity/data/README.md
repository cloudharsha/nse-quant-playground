# Equity Data Directory

This directory contains historical equity data for NSE (National Stock Exchange of India) stocks.

## Data Files

Each CSV file contains comprehensive OHLCV (Open, High, Low, Close, Volume) data along with technical indicators for a specific stock.

### File Naming Convention

`{TICKER_SYMBOL}_equity_data.csv`

Example: `RELIANCE_NS_equity_data.csv`

### Data Columns

Each CSV file contains the following columns:

#### Price Data
- **Date**: Timestamp of the candle
- **Open**: Opening price
- **High**: Highest price during the period
- **Low**: Lowest price during the period
- **Close**: Closing price
- **Volume**: Trading volume

#### Technical Indicators

**Momentum Indicators:**
- **RSI**: Relative Strength Index (14-period)
- **MACD**: Moving Average Convergence Divergence
- **MACD_Signal**: MACD signal line (9-period EMA)
- **MACD_Histogram**: MACD histogram (MACD - Signal)
- **Stoch_K**: Stochastic %K (14-period)
- **Stoch_D**: Stochastic %D (3-period of %K)

**Volatility Indicators:**
- **ATR**: Average True Range (14-period)
- **BB_Upper**: Bollinger Bands upper band (20-period, 2 std dev)
- **BB_Middle**: Bollinger Bands middle band (20-period SMA)
- **BB_Lower**: Bollinger Bands lower band (20-period, 2 std dev)

**Trend Indicators:**
- **SMA_20**: Simple Moving Average (20-period)
- **SMA_50**: Simple Moving Average (50-period)
- **EMA_12**: Exponential Moving Average (12-period)
- **EMA_26**: Exponential Moving Average (26-period)

**Price & Volume Metrics:**
- **Price_Change**: Absolute price change from previous period
- **Price_Change_Pct**: Percentage price change from previous period
- **Volume_SMA**: Volume moving average (20-period)

## Data Specifications

- **Time Period**: 3 months of historical data
- **Timeframe**: Auto-detected lowest available interval (preferably 1-minute, fallback to higher timeframes)
- **Exchange**: NSE (National Stock Exchange of India)
- **Data Source**: Yahoo Finance (yfinance)
- **Update Frequency**: As needed

## Usage

Load the data in Python:

```python
import pandas as pd

# Load data
df = pd.read_csv('RELIANCE_NS_equity_data.csv')

# Convert date column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Display basic statistics
print(df.describe())

# Display first few rows
print(df.head())
```

## Notes

- Data includes only trading days (excludes weekends and holidays)
- Technical indicators are calculated using standard formulas
- Some initial rows may have NaN values for indicators that require historical data
- Data is cleaned to remove rows with missing indicator values

## Data Quality

- Data is sourced from Yahoo Finance, which provides reliable NSE data
- All calculations follow standard technical analysis methodologies
- Data is validated for completeness before saving