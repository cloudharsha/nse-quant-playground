"""
Fetch intraday USD/INR data from Yahoo Finance.

This mirrors the derivatives intraday fetcher, but intentionally pulls only
USDINR=X and writes only USDINR CSV files for the requested timeframes.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf


TICKER_SYMBOL = "USDINR=X"
OUTPUT_SYMBOL = "USDINR"
PERIOD = "1mo"
INTERVALS = ("5m", "15m", "30m", "1h")


def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
    delta = data["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def calculate_macd(
    data: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    exp_fast = data["Close"].ewm(span=fast, adjust=False).mean()
    exp_slow = data["Close"].ewm(span=slow, adjust=False).mean()
    macd = exp_fast - exp_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram


def calculate_bollinger_bands(
    data: pd.DataFrame,
    period: int = 20,
    std_dev: int = 2,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    sma = data["Close"].rolling(window=period).mean()
    std = data["Close"].rolling(window=period).std()
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    return upper_band, sma, lower_band


def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = data["High"] - data["Low"]
    high_close = np.abs(data["High"] - data["Close"].shift())
    low_close = np.abs(data["Low"] - data["Close"].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return true_range.rolling(window=period).mean()


def calculate_stochastic(
    data: pd.DataFrame,
    k_period: int = 14,
    d_period: int = 3,
) -> tuple[pd.Series, pd.Series]:
    low_min = data["Low"].rolling(window=k_period).min()
    high_max = data["High"].rolling(window=k_period).max()
    k_percent = 100 * ((data["Close"] - low_min) / (high_max - low_min))
    d_percent = k_percent.rolling(window=d_period).mean()
    return k_percent, d_percent


def fetch_intraday_data(ticker_symbol: str, period: str, interval: str) -> pd.DataFrame | None:
    print(f"Fetching {period} of {interval} data for {ticker_symbol}...")

    try:
        data = yf.Ticker(ticker_symbol).history(period=period, interval=interval)
    except Exception as exc:
        print(f"Error fetching {ticker_symbol} {interval}: {exc}")
        return None

    if data.empty:
        print("No data retrieved")
        return None

    data = data.reset_index()
    date_column = data.columns[0]
    data = data.rename(columns={date_column: "Date"})
    data = data[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()

    print(f"Retrieved {len(data)} candles")
    print(f"Date range: {data['Date'].min()} to {data['Date'].max()}")
    return data


def add_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
    print("Calculating technical indicators...")

    data["RSI"] = calculate_rsi(data)
    data["MACD"], data["MACD_Signal"], data["MACD_Histogram"] = calculate_macd(data)
    data["BB_Upper"], data["BB_Middle"], data["BB_Lower"] = calculate_bollinger_bands(data)
    data["ATR"] = calculate_atr(data)
    data["Stoch_K"], data["Stoch_D"] = calculate_stochastic(data)
    data["SMA_20"] = data["Close"].rolling(window=20).mean()
    data["SMA_50"] = data["Close"].rolling(window=50).mean()
    data["EMA_12"] = data["Close"].ewm(span=12, adjust=False).mean()
    data["EMA_26"] = data["Close"].ewm(span=26, adjust=False).mean()
    data["Price_Change"] = data["Close"].pct_change()
    data["Price_Change_Pct"] = data["Price_Change"] * 100
    data["Volume_SMA"] = data["Volume"].rolling(window=20).mean()

    return data.dropna()


def save_to_csv(data: pd.DataFrame, interval: str, output_dir: Path) -> Path | None:
    if data.empty:
        print(f"No processed data to save for {interval}")
        return None

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{OUTPUT_SYMBOL}_data_{interval}.csv"
    data.to_csv(path, index=False)
    print(f"Data saved to: {path}")
    return path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir = repo_root / "usdinr" / "data"

    print("=" * 60)
    print("USDINR Intraday Data Collection")
    print("=" * 60)
    print(f"Ticker: {TICKER_SYMBOL}")
    print(f"Period: {PERIOD}")
    print(f"Intervals: {', '.join(INTERVALS)}")
    print(f"Output directory: {output_dir}")
    print("=" * 60)
    print("Note: Yahoo Finance limits intraday data history.")
    print("=" * 60)

    saved_files: list[Path] = []
    for interval in INTERVALS:
        print(f"\n--- Fetching {interval} data ---")
        data = fetch_intraday_data(TICKER_SYMBOL, PERIOD, interval)
        if data is None or data.empty:
            print(f"Failed to fetch USDINR at {interval}")
            continue

        processed = add_technical_indicators(data)
        saved_path = save_to_csv(processed, interval, output_dir)
        if saved_path is not None:
            saved_files.append(saved_path)
            print(f"Successfully processed USDINR at {interval}")

    print("\n" + "=" * 60)
    print("USDINR intraday data collection completed")
    print("=" * 60)
    for path in saved_files:
        print(path)


if __name__ == "__main__":
    main()
