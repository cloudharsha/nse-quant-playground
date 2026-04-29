import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def calculate_rsi(data, period=14):
    """Calculate Relative Strength Index (RSI)"""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data, fast=12, slow=26, signal=9):
    """Calculate MACD (Moving Average Convergence Divergence)"""
    exp_fast = data['Close'].ewm(span=fast, adjust=False).mean()
    exp_slow = data['Close'].ewm(span=slow, adjust=False).mean()
    macd = exp_fast - exp_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram

def calculate_bollinger_bands(data, period=20, std_dev=2):
    """Calculate Bollinger Bands"""
    sma = data['Close'].rolling(window=period).mean()
    std = data['Close'].rolling(window=period).std()
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    return upper_band, sma, lower_band

def calculate_atr(data, period=14):
    """Calculate Average True Range (ATR)"""
    high_low = data['High'] - data['Low']
    high_close = np.abs(data['High'] - data['Close'].shift())
    low_close = np.abs(data['Low'] - data['Close'].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    return atr

def calculate_stochastic(data, k_period=14, d_period=3):
    """Calculate Stochastic Oscillator"""
    low_min = data['Low'].rolling(window=k_period).min()
    high_max = data['High'].rolling(window=k_period).max()
    k_percent = 100 * ((data['Close'] - low_min) / (high_max - low_min))
    d_percent = k_percent.rolling(window=d_period).mean()
    return k_percent, d_percent

def get_nifty_data(ticker_symbol, period='3mo', interval='1d'):
    """
    Fetch Nifty/Index data with all available parameters and technical indicators

    Args:
        ticker_symbol: NSE index ticker symbol (e.g., '^NSEI', 'NIFTY50.NS')
        period: Time period to fetch (default: '3mo' for 3 months)
        interval: Time interval (default: '1d' for daily)

    Returns:
        DataFrame with OHLCV data and technical indicators
    """
    print(f"Fetching data for {ticker_symbol}...")

    ticker = yf.Ticker(ticker_symbol)

    print(f"Using timeframe: {interval}")
    print(f"Fetching {period} of data...")

    # Fetch historical data
    data = ticker.history(period=period, interval=interval)

    if data.empty:
        print(f"No data found for {ticker_symbol}")
        return None

    # Reset index to make datetime a column
    data = data.reset_index()

    # Rename columns to standard format
    data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']

    # Calculate technical indicators
    print("Calculating technical indicators...")

    # RSI
    data['RSI'] = calculate_rsi(data)

    # MACD
    data['MACD'], data['MACD_Signal'], data['MACD_Histogram'] = calculate_macd(data)

    # Bollinger Bands
    data['BB_Upper'], data['BB_Middle'], data['BB_Lower'] = calculate_bollinger_bands(data)

    # ATR
    data['ATR'] = calculate_atr(data)

    # Stochastic
    data['Stoch_K'], data['Stoch_D'] = calculate_stochastic(data)

    # Additional indicators
    data['SMA_20'] = data['Close'].rolling(window=20).mean()
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    data['EMA_12'] = data['Close'].ewm(span=12, adjust=False).mean()
    data['EMA_26'] = data['Close'].ewm(span=26, adjust=False).mean()

    # Price change metrics
    data['Price_Change'] = data['Close'].pct_change()
    data['Price_Change_Pct'] = data['Price_Change'] * 100

    # Volume metrics
    data['Volume_SMA'] = data['Volume'].rolling(window=20).mean()

    # Drop unnecessary columns
    data = data.drop(['Dividends', 'Stock Splits'], axis=1)

    # Remove rows with NaN values (from indicator calculations)
    data = data.dropna()

    print(f"Successfully fetched {len(data)} data points")
    print(f"Date range: {data['Date'].min()} to {data['Date'].max()}")

    return data

def save_to_csv(data, ticker_symbol, output_dir):
    """Save data to CSV file"""
    if data is None or data.empty:
        print("No data to save")
        return None

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename
    filename = f"{ticker_symbol.replace('^', '').replace('.', '_')}_data.csv"
    filepath = os.path.join(output_dir, filename)

    # Save to CSV
    data.to_csv(filepath, index=False)
    print(f"Data saved to: {filepath}")

    return filepath

def main():
    """Main function to fetch and save Nifty/Index data"""
    # Configuration
    ticker_symbols = [
        '^NSEI',         # Nifty 50 Index
        '^NSEBANK',      # Nifty Bank Index
        '^CNXIT',        # Nifty IT Index
        '^CNXFMCG',      # Nifty FMCG Index
        '^CNXAUTO',      # Nifty Auto Index
    ]

    period = '3mo'  # 3 months of data
    interval = '1d'  # Daily timeframe
    output_dir = '/mnt/c/Users/harsh/Desktop/workspace/git/nse-quant-playground/derivatives/data'

    print("=" * 60)
    print("NSE Index/Derivatives Data Collection")
    print("=" * 60)
    print(f"Period: {period}")
    print(f"Timeframe: {interval}")
    print(f"Output directory: {output_dir}")
    print(f"Number of indices: {len(ticker_symbols)}")
    print("=" * 60)

    # Fetch data for each index
    for ticker in ticker_symbols:
        print(f"\n{'=' * 60}")
        print(f"Processing: {ticker}")
        print('=' * 60)

        try:
            # Fetch data
            data = get_nifty_data(ticker, period=period, interval=interval)

            # Save to CSV
            if data is not None:
                save_to_csv(data, ticker, output_dir)
                print(f"✓ Successfully processed {ticker}")
            else:
                print(f"✗ Failed to fetch data for {ticker}")

        except Exception as e:
            print(f"✗ Error processing {ticker}: {str(e)}")
            continue

    print("\n" + "=" * 60)
    print("Data collection completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()