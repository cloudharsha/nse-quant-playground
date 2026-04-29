"""
Fetch intraday NSE equity data using multiple requests to overcome API limitations.
This script fetches data in 60-day chunks and combines them for longer periods.
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import time

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

def get_intraday_data_chunk(ticker_symbol, period, interval):
    """Fetch a single chunk of intraday data using period parameter"""
    ticker = yf.Ticker(ticker_symbol)

    try:
        data = ticker.history(period=period, interval=interval)
        if not data.empty:
            data = data.reset_index()
            data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
            data = data.drop(['Dividends', 'Stock Splits'], axis=1)
            return data
        return None
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return None

def get_extended_intraday_data(ticker_symbol, period='2mo', interval='5m'):
    """
    Fetch intraday data using period parameter

    Args:
        ticker_symbol: NSE ticker symbol (e.g., 'RELIANCE.NS')
        period: Time period ('1mo', '2mo', etc.)
        interval: Time interval ('5m', '15m', '30m', etc.)

    Returns:
        DataFrame with intraday data
    """
    print(f"Fetching {period} of {interval} data for {ticker_symbol}...")

    # Yahoo Finance limits intraday data to maximum 60 days
    # Valid periods for intraday: '1mo' (30 days), '2mo' (60 days)

    try:
        chunk_data = get_intraday_data_chunk(ticker_symbol, period, interval)

        if chunk_data is not None and not chunk_data.empty:
            print(f"✓ Retrieved {len(chunk_data)} candles")
            print(f"  Date range: {chunk_data['Date'].min()} to {chunk_data['Date'].max()}")
            return chunk_data
        else:
            print(f"✗ No data retrieved")
            return None

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return None

def add_technical_indicators(data):
    """Add all technical indicators to the data"""
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

    # Remove rows with NaN values (from indicator calculations)
    data = data.dropna()

    return data

def save_to_csv(data, ticker_symbol, interval, output_dir):
    """Save data to CSV file"""
    if data is None or data.empty:
        print("No data to save")
        return None

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename
    filename = f"{ticker_symbol.replace('.', '_')}_equity_data_{interval}.csv"
    filepath = os.path.join(output_dir, filename)

    # Save to CSV
    data.to_csv(filepath, index=False)
    print(f"Data saved to: {filepath}")

    return filepath

def main():
    """Main function to fetch and save intraday NSE equity data"""
    # Configuration
    ticker_symbols = [
        'RELIANCE.NS',
        'TCS.NS',
        'HDFCBANK.NS',
        'INFY.NS',
        'ICICIBANK.NS',
        'SBIN.NS',
        'BHARTIARTL.NS',
        'ITC.NS',
        'KOTAKBANK.NS',
        'LT.NS',
    ]

    period = '1mo'  # 1 month (30 days - try shorter period due to API limitations)
    intervals = ['5m', '15m', '30m', '1h']  # Multiple timeframes
    output_dir = '/mnt/c/Users/harsh/Desktop/workspace/git/nse-quant-playground/equity/data'

    print("=" * 60)
    print("NSE Intraday Equity Data Collection")
    print("=" * 60)
    print(f"Period: {period} (30 days - testing shorter period due to API limitations)")
    print(f"Intervals: {', '.join(intervals)}")
    print(f"Output directory: {output_dir}")
    print(f"Number of stocks: {len(ticker_symbols)}")
    print("=" * 60)
    print("Note: Yahoo Finance limits intraday data to maximum 60 days")
    print("=" * 60)

    # Fetch data for each stock and each interval
    for ticker in ticker_symbols:
        print(f"\n{'=' * 60}")
        print(f"Processing: {ticker}")
        print('=' * 60)

        for interval in intervals:
            print(f"\n--- Fetching {interval} data ---")

            try:
                # Fetch intraday data
                data = get_extended_intraday_data(ticker, period=period, interval=interval)

                # Add technical indicators
                if data is not None and not data.empty:
                    data = add_technical_indicators(data)

                    # Save to CSV
                    save_to_csv(data, ticker, interval, output_dir)
                    print(f"✓ Successfully processed {ticker} at {interval}")
                else:
                    print(f"✗ Failed to fetch data for {ticker} at {interval}")

            except Exception as e:
                print(f"✗ Error processing {ticker} at {interval}: {str(e)}")
                continue

    print("\n" + "=" * 60)
    print("Intraday data collection completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()