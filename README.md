# nse-quant-playground

Using math + data + algorithms to make trading decisions instead of gut feeling

## Project Structure

```
nse-quant-playground/
├── equity/              # Equity trading strategies and analysis
│   ├── data/            # Historical equity data files
│   ├── python/          # Data fetching and processing scripts
│   └── results/         # Backtest results and analysis outputs
├── commodities/         # Commodities trading (future)
└── derivatives/         # Derivatives trading (future)
```

## Current Focus: Equity Data Collection

### Data Specifications

- **Exchange**: NSE (National Stock Exchange of India)
- **Time Period**: 3 months of historical data
- **Timeframe**: Auto-detected lowest available interval (preferably 1-minute candles)
- **Data Source**: Yahoo Finance (yfinance)
- **Format**: CSV files with comprehensive technical indicators

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

### Directory Usage

#### `equity/data/`
Contains CSV files with historical equity data for NSE stocks. Each file includes OHLCV data and 15+ technical indicators.

#### `equity/python/`
Contains Python scripts for:
- Fetching historical data from Yahoo Finance
- Auto-detecting available timeframes
- Calculating technical indicators
- Data validation and CSV export

#### `equity/results/`
Will contain:
- Backtesting results
- Strategy performance analysis
- Risk metrics and reports
- Visualizations and summaries

### Getting Started

1. **Install Dependencies:**
```bash
pip install yfinance pandas numpy
```

2. **Fetch Data:**
```bash
cd equity/python
python fetch_nse_equity_data.py
```

3. **Analyze Data:**
```python
import pandas as pd
df = pd.read_csv('../data/RELIANCE_NS_equity_data.csv')
```

### Default Stocks

Initial data collection focuses on major NSE stocks:
- RELIANCE.NS, TCS.NS, HDFCBANK.NS, INFY.NS, ICICIBANK.NS
- SBIN.NS, BHARTIARTL.NS, ITC.NS, KOTAKBANK.NS, LT.NS

### Next Steps

1. ✅ Set up data collection infrastructure
2. ✅ Implement technical indicator calculations
3. 🔄 Develop trading strategies
4. 🔄 Run backtests
5. 🔄 Analyze performance and optimize
6. 🔄 Implement risk management

## Project Philosophy

- **Data-Driven**: All decisions based on historical data and statistical analysis
- **Systematic**: Rule-based approaches eliminate emotional bias
- **Validated**: Strategies are thoroughly backtested before deployment
- **Transparent**: Clear documentation of all methodologies and results
