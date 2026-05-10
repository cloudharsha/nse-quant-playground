"""
Fetch five years of BTC-USD intraday candles from Coinbase Exchange.

The 15-minute series is fetched directly from Coinbase's public candles API.
The 30-minute and 1-hour series are derived from that canonical 15-minute data.
"""

from __future__ import annotations

import json
import math
import os
import socket
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib import error, parse, request

import numpy as np
import pandas as pd


PRODUCT_ID = "BTC-USD"
OUTPUT_SYMBOL = "BTCUSD"
LOOKBACK_DAYS = 365 * 5
BASE_GRANULARITY_SECONDS = 900
WINDOW_HOURS = 72
TARGET_INTERVALS = ("15m", "30m", "1h")
MAX_RETRIES = 5
REQUEST_SLEEP_SECONDS = 0.15

COINBASE_CANDLES_URL = (
    "https://api.exchange.coinbase.com/products/{product_id}/candles?{query}"
)
REQUEST_HEADERS = {
    "User-Agent": "nse-quant-playground/1.0",
    "Accept": "application/json",
}
OUTPUT_COLUMNS = [
    "Date",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "RSI",
    "MACD",
    "MACD_Signal",
    "MACD_Histogram",
    "BB_Upper",
    "BB_Middle",
    "BB_Lower",
    "ATR",
    "Stoch_K",
    "Stoch_D",
    "SMA_20",
    "SMA_50",
    "EMA_12",
    "EMA_26",
    "Price_Change",
    "Price_Change_Pct",
    "Volume_SMA",
]
MIN_ROWS_BY_INTERVAL = {
    "15m": 34000,
    "30m": 17000,
    "1h": 8500,
}
EXPECTED_SOURCE_COUNTS = {
    "30m": 2,
    "1h": 4,
}
RESAMPLE_RULES = {
    "30m": "30min",
    "1h": "1h",
}


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


def add_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()

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

    return data.dropna().reset_index(drop=True)[OUTPUT_COLUMNS]


def floor_to_granularity(dt: datetime, granularity_seconds: int) -> datetime:
    timestamp = int(dt.timestamp())
    floored = (timestamp // granularity_seconds) * granularity_seconds
    return datetime.fromtimestamp(floored, tz=timezone.utc)


def format_coinbase_timestamp(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_candle_window(start_utc: datetime, end_utc: datetime) -> pd.DataFrame:
    params = parse.urlencode(
        {
            "start": format_coinbase_timestamp(start_utc),
            "end": format_coinbase_timestamp(end_utc),
            "granularity": BASE_GRANULARITY_SECONDS,
        }
    )
    url = COINBASE_CANDLES_URL.format(product_id=PRODUCT_ID, query=params)

    for attempt in range(MAX_RETRIES + 1):
        try:
            req = request.Request(url, headers=REQUEST_HEADERS)
            with request.urlopen(req, timeout=30) as response:
                payload = json.load(response)
            if not isinstance(payload, list):
                raise RuntimeError(f"Unexpected Coinbase response: {payload}")

            data = pd.DataFrame(
                payload,
                columns=["time", "Low", "High", "Open", "Close", "Volume"],
            )
            if data.empty:
                raise RuntimeError(
                    "Coinbase returned no candles for a BTC-USD window that should exist"
                )

            data["Date"] = pd.to_datetime(data["time"], unit="s", utc=True)
            data = data[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
            numeric_columns = ["Open", "High", "Low", "Close", "Volume"]
            data[numeric_columns] = data[numeric_columns].astype(float)
            return data.sort_values("Date").reset_index(drop=True)
        except error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504):
                raise
            should_retry = attempt < MAX_RETRIES
            if not should_retry:
                raise RuntimeError(
                    f"Coinbase request failed for {start_utc} -> {end_utc} with HTTP {exc.code}"
                ) from exc
            backoff_seconds = 2 ** attempt
            print(
                f"Retrying {start_utc} -> {end_utc} after HTTP {exc.code} "
                f"(attempt {attempt + 1}/{MAX_RETRIES + 1}, wait {backoff_seconds}s)"
            )
            time.sleep(backoff_seconds)
        except (error.URLError, TimeoutError, socket.timeout, json.JSONDecodeError) as exc:
            should_retry = attempt < MAX_RETRIES
            if not should_retry:
                raise RuntimeError(
                    f"Coinbase request failed for {start_utc} -> {end_utc}: {exc}"
                ) from exc
            backoff_seconds = 2 ** attempt
            print(
                f"Retrying {start_utc} -> {end_utc} after transient error "
                f"(attempt {attempt + 1}/{MAX_RETRIES + 1}, wait {backoff_seconds}s): {exc}"
            )
            time.sleep(backoff_seconds)

    raise RuntimeError(f"Failed to fetch candle window for {start_utc} -> {end_utc}")


def fetch_canonical_15m_data(start_utc: datetime, end_utc: datetime) -> pd.DataFrame:
    total_hours = (end_utc - start_utc).total_seconds() / 3600
    total_windows = math.ceil(total_hours / WINDOW_HOURS)
    frames: list[pd.DataFrame] = []
    window_start = start_utc
    window_number = 1

    while window_start < end_utc:
        window_end = min(window_start + timedelta(hours=WINDOW_HOURS), end_utc)
        print(
            f"Fetching 15m window {window_number}/{total_windows}: "
            f"{window_start} -> {window_end}"
        )
        frame = fetch_candle_window(window_start, window_end)
        frames.append(frame)
        time.sleep(REQUEST_SLEEP_SECONDS)
        window_start = window_end
        window_number += 1

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.sort_values("Date").drop_duplicates(subset="Date", keep="last")
    combined = combined[combined["Date"] >= start_utc]
    combined = combined[combined["Date"] < end_utc]
    return combined.reset_index(drop=True)


def resample_candles(data: pd.DataFrame, interval: str) -> pd.DataFrame:
    if interval not in RESAMPLE_RULES:
        raise ValueError(f"Unsupported interval for resampling: {interval}")

    base = data.set_index("Date").sort_index()
    aggregation = {
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum",
    }
    rule = RESAMPLE_RULES[interval]
    resampled = base.resample(rule, label="left", closed="left").agg(aggregation)
    counts = base["Close"].resample(rule, label="left", closed="left").count()
    resampled["Source_Count"] = counts
    resampled = resampled[resampled["Source_Count"] == EXPECTED_SOURCE_COUNTS[interval]]
    resampled = resampled.drop(columns="Source_Count").dropna().reset_index()
    return resampled[["Date", "Open", "High", "Low", "Close", "Volume"]]


def validate_processed_data(data: pd.DataFrame, interval: str) -> None:
    if list(data.columns) != OUTPUT_COLUMNS:
        raise RuntimeError(f"Unexpected column order for {interval}: {list(data.columns)}")
    if data.empty:
        raise RuntimeError(f"No processed rows available for {interval}")
    if not data["Date"].is_monotonic_increasing:
        raise RuntimeError(f"Timestamps are not sorted for {interval}")
    if data["Date"].duplicated().any():
        raise RuntimeError(f"Duplicate timestamps detected for {interval}")

    span_days = (data["Date"].iloc[-1] - data["Date"].iloc[0]).total_seconds() / 86400
    if span_days < 360:
        raise RuntimeError(f"{interval} coverage is only {span_days:.2f} days")
    if len(data) <= MIN_ROWS_BY_INTERVAL[interval]:
        raise RuntimeError(f"{interval} row count {len(data)} is below expected minimum")


def save_to_csv(data: pd.DataFrame, interval: str, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    final_path = output_dir / f"{OUTPUT_SYMBOL}_data_{interval}.csv"

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".csv.tmp",
        prefix=f"{OUTPUT_SYMBOL}_{interval}_",
        dir=output_dir,
        delete=False,
        newline="",
    ) as handle:
        temp_path = Path(handle.name)

    data.to_csv(temp_path, index=False)
    return temp_path, final_path


def commit_staged_files(staged_files: list[tuple[Path, Path]]) -> None:
    for temp_path, final_path in staged_files:
        os.replace(temp_path, final_path)
        print(f"Data saved to: {final_path}")


def cleanup_temp_files(staged_files: list[tuple[Path, Path]]) -> None:
    for temp_path, _ in staged_files:
        if temp_path.exists():
            temp_path.unlink()


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir = repo_root / "btc" / "data"

    current_bucket_start = floor_to_granularity(datetime.now(timezone.utc), BASE_GRANULARITY_SECONDS)
    end_utc = current_bucket_start
    start_utc = end_utc - timedelta(days=LOOKBACK_DAYS)

    print("=" * 60)
    print("BTCUSD Intraday Data Collection")
    print("=" * 60)
    print(f"Product: {PRODUCT_ID}")
    print(f"Lookback: {LOOKBACK_DAYS} days")
    print(f"Base interval: 15m")
    print(f"Derived intervals: {', '.join(TARGET_INTERVALS[1:])}")
    print(f"Output directory: {output_dir}")
    print(f"Time range: {start_utc} -> {end_utc}")
    print("=" * 60)

    canonical_15m = fetch_canonical_15m_data(start_utc, end_utc)
    print(f"Fetched {len(canonical_15m)} canonical 15m candles")

    raw_outputs = {
        "15m": canonical_15m,
        "30m": resample_candles(canonical_15m, "30m"),
        "1h": resample_candles(canonical_15m, "1h"),
    }

    processed_outputs: dict[str, pd.DataFrame] = {}
    for interval in TARGET_INTERVALS:
        print(f"\nProcessing {interval} data...")
        processed = add_technical_indicators(raw_outputs[interval])
        validate_processed_data(processed, interval)
        processed_outputs[interval] = processed
        print(
            f"{interval}: {len(processed)} rows, "
            f"{processed['Date'].iloc[0]} -> {processed['Date'].iloc[-1]}"
        )

    staged_files: list[tuple[Path, Path]] = []
    try:
        for interval in TARGET_INTERVALS:
            staged_files.append(save_to_csv(processed_outputs[interval], interval, output_dir))
        commit_staged_files(staged_files)
    except Exception:
        cleanup_temp_files(staged_files)
        raise

    print("\n" + "=" * 60)
    print("BTCUSD intraday data collection completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
