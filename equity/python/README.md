# Equity Python Scripts Directory

This directory contains Python scripts for fetching, processing, and analyzing NSE equity data.

## Available Scripts

### `fetch_nse_equity_data.py`

Main script for fetching historical equity data from NSE with comprehensive technical indicators.

#### Features

- **Auto-detects lowest available timeframe**: Checks from 1-minute upwards and uses the finest available granularity
- **Comprehensive data collection**: Fetches OHLCV data for multiple stocks
- **Technical indicator calculation**: Computes 15+ technical indicators automatically
- **Data validation**: Ensures data quality and completeness
- **CSV export**: Saves data in standardized CSV format

#### Usage

```bash
# Run the script (uses default configuration)
python fetch_nse_equity_data.py
```

#### Configuration

Edit the script to customize:

- **Ticker symbols**: Add/remove NSE stocks in the `ticker_symbols` list
- **Time period**: Change the `period` variable (e.g., '1mo', '6mo', '1y', '2y')
- **Output directory**: Modify the `output_dir` path
- **Indicator parameters**: Adjust calculation periods for technical indicators

#### Default Stocks

The script fetches data for major NSE stocks:
- RELIANCE.NS (Reliance Industries)
- TCS.NS (Tata Consultancy Services)
- HDFCBANK.NS (HDFC Bank)
- INFY.NS (Infosys)
- ICICIBANK.NS (ICICI Bank)
- SBIN.NS (State Bank of India)
- BHARTIARTL.NS (Bharti Airtel)
- ITC.NS (ITC Limited)
- KOTAKBANK.NS (Kotak Mahindra Bank)
- LT.NS (Larsen & Toubro)

#### Technical Indicators Calculated

**Momentum:**
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Stochastic Oscillator

**Volatility:**
- ATR (Average True Range)
- Bollinger Bands

**Trend:**
- SMA (Simple Moving Average) - 20 & 50 period
- EMA (Exponential Moving Average) - 12 & 26 period

**Price/Volume:**
- Price change metrics
- Volume moving average

#### Dependencies

```bash
pip install yfinance pandas numpy
```

#### Output

- CSV files saved to `../data/` directory
- Console output shows progress and any issues
- Each stock gets its own CSV file with comprehensive indicators

## Script Structure

### Functions

- `get_available_timeframes()`: Detects available timeframes for a ticker
- `get_nse_equity_data()`: Main data fetching function
- `calculate_rsi()`: Calculates RSI indicator
- `calculate_macd()`: Calculates MACD indicator
- `calculate_bollinger_bands()`: Calculates Bollinger Bands
- `calculate_atr()`: Calculates ATR indicator
- `calculate_stochastic()`: Calculates Stochastic Oscillator
- `save_to_csv()`: Saves data to CSV file
- `main()`: Main execution function

## Future Enhancements

Potential additions to this directory:

- Real-time data fetching scripts
- Data validation and cleaning utilities
- Backtesting frameworks
- Strategy implementation scripts
- Performance analysis tools
- Visualization utilities
- Data update automation

## Notes

- Scripts are designed to be modular and reusable
- Error handling ensures robustness
- Progress reporting helps with monitoring
- Configuration is centralized for easy customization