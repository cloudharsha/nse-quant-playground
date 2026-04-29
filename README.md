# nse-quant-playground

Using math + data + algorithms to make trading decisions instead of gut feeling

## Project Structure

```
nse-quant-playground/
├── equity/              # Equity trading strategies and analysis
│   ├── data/            # Historical equity data files (daily & 5-minute)
│   ├── python/          # Data fetching and processing scripts
│   ├── results/         # Backtest results and analysis outputs
│   └── DATA_COLLECTION_SUMMARY.md  # Data collection documentation
├── commodities/         # Commodities trading
│   ├── data/            # Historical commodities data files
│   ├── python/          # Data fetching and processing scripts
│   └── results/         # Backtest results and analysis outputs
├── derivatives/         # Derivatives trading
│   ├── data/            # Historical derivatives data files
│   ├── python/          # Data fetching and processing scripts
│   └── results/         # Backtest results and analysis outputs
└── common-strategies/   # Cross-asset trading strategies
    ├── python/          # Strategy implementation scripts
    └── results/         # Backtest results and performance metrics
```

## Current Focus: Multi-Asset Trading Strategies

### Data Collection Status

**Equity Data:**
- **Exchange**: NSE (National Stock Exchange of India)
- **Time Period**: 3 months of historical data
- **Timeframes**: Daily and 5-minute intraday candles
- **Data Source**: Yahoo Finance (yfinance)
- **Format**: CSV files with comprehensive technical indicators
- **Stocks Covered**: RELIANCE.NS, TCS.NS, HDFCBANK.NS, INFY.NS, ICICIBANK.NS, SBIN.NS, BHARTIARTL.NS, ITC.NS, KOTAKBANK.NS, LT.NS

**Commodities Data:**
- **Exchange**: MCX (Multi Commodity Exchange)
- **Time Period**: 3 months of historical data
- **Timeframes**: Daily and 5-minute intraday candles
- **Data Source**: Yahoo Finance (yfinance)

**Derivatives Data:**
- **Exchange**: NSE (National Stock Exchange of India)
- **Instruments**: NIFTY 50 index and options
- **Time Period**: 3 months of historical data
- **Timeframes**: Daily and 5-minute intraday candles
- **Data Source**: Yahoo Finance (yfinance)

### Data Parameters

Each dataset includes:

**Price Data:**
- Open, High, Low, Close (OHLC)
- Volume

**Technical Indicators:**
- **Momentum**: RSI, MACD, Stochastic Oscillator
- **Volatility**: ATR, Bollinger Bands
- **Trend**: SMA (20, 50), EMA (12, 26)
- **Price/Volume Metrics**: Price change, Volume moving average

### Trading Strategies

**Common Strategies:**
- **Open-Low-High 5-Minute Strategy**: Intraday strategy based on opening range breakout patterns
  - Entry: Based on first 5-minute candle relationships
  - Exit: Target-based or time-based exits
  - Risk Management: Stop-loss and position sizing
  - Results: Comprehensive backtesting with equity curves, trade logs, and performance metrics

### Directory Usage

#### `equity/`
- **data/**: CSV files with historical equity data for NSE stocks (daily & 5-minute)
- **python/**: Scripts for fetching equity data, testing data availability, and calculating technical indicators
- **results/**: Backtesting results and analysis outputs
- **DATA_COLLECTION_SUMMARY.md**: Documentation of data collection process and status

#### `commodities/`
- **data/**: CSV files with historical commodities data
- **python/**: Scripts for fetching commodities data (daily & intraday)
- **results/**: Backtesting results and analysis outputs

#### `derivatives/`
- **data/**: CSV files with historical derivatives data (NIFTY index & options)
- **python/**: Scripts for fetching NIFTY data and intraday data
- **results/**: Backtesting results and analysis outputs

#### `common-strategies/`
- **python/**: Cross-asset trading strategy implementations
  - `open_low_high_5m_strategy.py`: Intraday breakout strategy
- **results/**: Strategy backtest results including:
  - Trade logs and performance metrics
  - Equity curves and P&L analysis
  - Best/worst trade analysis
  - Instrument-wise performance breakdown

### Getting Started

**1. Install Dependencies:**
```bash
# Equity data collection
cd equity/python
pip install -r requirements.txt

# Commodities data collection
cd ../../commodities/python
pip install -r requirements.txt

# Derivatives data collection
cd ../../derivatives/python
pip install -r requirements.txt
```

**2. Fetch Data:**
```bash
# Equity data (daily and 5-minute)
cd equity/python
python fetch_nse_equity_data.py
python fetch_intraday_data.py

# Commodities data
cd ../../commodities/python
python fetch_commodities_data.py
python fetch_commodities_intraday.py

# Derivatives data
cd ../../derivatives/python
python fetch_nifty_data.py
python fetch_nifty_intraday.py
```

**3. Run Strategies:**
```bash
# Common strategies
cd common-strategies/python
python open_low_high_5m_strategy.py
```

**4. Analyze Results:**
```python
import pandas as pd

# Load equity data
df = pd.read_csv('../equity/data/RELIANCE_NS_equity_data.csv')

# Load strategy results
results = pd.read_csv('../common-strategies/results/open_low_high_5m_20260429_143117/trades.csv')
summary = pd.read_json('../common-strategies/results/open_low_high_5m_20260429_143117/summary.json')
```

### Default Stocks

Initial data collection focuses on major NSE stocks:
- RELIANCE.NS, TCS.NS, HDFCBANK.NS, INFY.NS, ICICIBANK.NS
- SBIN.NS, BHARTIARTL.NS, ITC.NS, KOTAKBANK.NS, LT.NS

### Next Steps

1. ✅ Set up data collection infrastructure
2. ✅ Implement technical indicator calculations
3. ✅ Develop trading strategies
4. ✅ Run backtests
5. 🔄 Analyze performance and optimize
6. 🔄 Implement risk management
7. 🔄 Expand to commodities and derivatives strategies
8. 🔄 Develop portfolio management and position sizing
9. 🔄 Create real-time trading integration

## Project Philosophy

- **Data-Driven**: All decisions based on historical data and statistical analysis
- **Systematic**: Rule-based approaches eliminate emotional bias
- **Validated**: Strategies are thoroughly backtested before deployment
- **Transparent**: Clear documentation of all methodologies and results
