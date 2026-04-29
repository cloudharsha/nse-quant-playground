# Derivatives Python Scripts Directory

This directory contains Python scripts for fetching, processing, and analyzing NSE derivatives and index data.

## Available Scripts

### `fetch_nifty_data.py`

Main script for fetching historical NSE index data with comprehensive technical indicators.

#### Features

- **Comprehensive data collection**: Fetches OHLCV data for major NSE indices
- **Technical indicator calculation**: Computes 15+ technical indicators automatically
- **Data validation**: Ensures data quality and completeness
- **CSV export**: Saves data in standardized CSV format

#### Usage

```bash
# Run the script (uses default configuration)
python fetch_nifty_data.py
```

#### Configuration

Edit the script to customize:

- **Ticker symbols**: Add/remove NSE indices in the `ticker_symbols` list
- **Time period**: Change the `period` variable (e.g., '1mo', '6mo', '1y', '2y')
- **Timeframe**: Modify the `interval` variable (e.g., '1d', '1wk', '1mo')
- **Output directory**: Modify the `output_dir` path
- **Indicator parameters**: Adjust calculation periods for technical indicators

#### Default Indices

The script fetches data for major NSE indices:
- ^NSEI (Nifty 50 Index)
- ^NSEBANK (Nifty Bank Index)
- ^CNXIT (Nifty IT Index)
- ^CNXFMCG (Nifty FMCG Index)
- ^CNXAUTO (Nifty Auto Index)

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
- Each index gets its own CSV file with comprehensive indicators

## Script Structure

### Functions

- `get_nifty_data()`: Main data fetching function
- `calculate_rsi()`: Calculates RSI indicator
- `calculate_macd()`: Calculates MACD indicator
- `calculate_bollinger_bands()`: Calculates Bollinger Bands
- `calculate_atr()`: Calculates ATR indicator
- `calculate_stochastic()`: Calculates Stochastic Oscillator
- `save_to_csv()`: Saves data to CSV file
- `main()`: Main execution function

## Future Enhancements

Potential additions to this directory:

- Real-time index data fetching scripts
- Options data collection
- Futures data collection
- Data validation and cleaning utilities
- Backtesting frameworks
- Strategy implementation scripts
- Performance analysis tools
- Visualization utilities

## Notes

- Scripts are designed to be modular and reusable
- Error handling ensures robustness
- Progress reporting helps with monitoring
- Configuration is centralized for easy customization