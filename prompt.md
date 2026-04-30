# AI Prompt: Convert Pine Script Strategy to Python Multi-Timeframe Backtest

## Task Overview

You are to convert a Pine Script trading strategy into a Python backtesting script that tests the strategy across multiple markets (equity, derivatives, commodities, usdinr) and multiple timeframes (5m, 15m, 30m, 1h).

## Input

- **Pine Script File**: Located at `pine-scripts/<filename>.pine`
- **Example Reference**: `common-strategies/python/sniper_multi_timeframe.py`
- **Base Utilities**: `common-strategies/python/open_low_high_5m_strategy.py`

## Output Requirements

1. **Python Script**: Create `common-strategies/python/<strategy_name>_multi_timeframe.py`
2. **Results Directory**: Generate results in `common-strategies/results/<strategy_name>_multi_timeframe_<timestamp>/`
3. **Output Files**:
   - `summary.json` - Complete backtest results
   - `summary.md` - Human-readable markdown summary
   - `timeframe_target_summary.csv` - Comparison across timeframes and targets
   - `all_trades.csv` - Detailed trade log (optional, with `--write-trade-audit` flag)

## Step-by-Step Instructions

### 1. Analyze the Pine Script

Read and understand the Pine Script strategy:
- Identify entry/exit conditions
- Extract indicator calculations and parameters
- Note any special rules (session times, filters, etc.)
- Understand signal generation logic (BUY/SELL signals)

### 2. Design the Python Script Structure

Follow the pattern from `sniper_multi_timeframe.py`:

```python
"""
Run <Strategy Name> backtests across multiple timeframes.

The runner keeps the <Strategy Name> logic in <strategy_name>_5m_strategy.py,
but compares the same rules across 5m, 15m, 30m, and 1h data.
"""

# Imports
from __future__ import annotations
import argparse
import json
import statistics
from collections import defaultdict
from dataclasses import replace
from datetime import datetime, time
from pathlib import Path
from typing import Any

import open_low_high_5m_strategy as base
import <strategy_name>_5m_strategy as strategy  # Your strategy module
```

### 3. Define Constants and Configuration

```python
DEFAULT_TIMEFRAMES = ("5m", "15m", "30m", "1h")
DEFAULT_MARKETS = ("derivatives", "equity", "commodities", "usdinr")

# Timeframe aliases for user input
TIMEFRAME_ALIASES = {
    "5": "5m", "5m": "5m", "5min": "5m", "5minute": "5m", "5minutes": "5m",
    "15": "15m", "15m": "15m", "15min": "15m", "15minute": "15m", "15minutes": "15m",
    "30": "30m", "30m": "30m", "30min": "30m", "30minute": "30m", "30minutes": "30m",
    "60": "1h", "60m": "1h", "1h": "1h", "1hr": "1h", "1hour": "1h", "1hours": "1h",
}
```

### 4. Create Strategy-Specific Module

Create a companion file `<strategy_name>_5m_strategy.py` that contains:

- **Strategy Config Class**: Define parameters specific to your strategy
- **Indicator Calculations**: Convert Pine Script indicators to Python
- **Signal Generation**: Implement entry/exit logic
- **Backtest Function**: Core backtesting logic

Example structure:

```python
from dataclasses import dataclass
from datetime import time
from typing import Any
import pandas as pd
import numpy as np

@dataclass
class StrategyConfig:
    """Configuration for <Strategy Name> strategy."""
    # Indicator parameters
    ema_fast: int = 9
    ema_slow: int = 21
    atr_period: int = 14
    rsi_period: int = 14

    # Trading parameters
    capital: float = 1000000.0
    risk_per_trade_pct: float = 1.0
    target_levels: list[int] = None

    # Session parameters
    session_start: time = time(9, 15)
    exit_time: time = time(15, 20)
    require_session_open: bool = True

    # Cost model
    cost_multiplier: float = 1.0
    equity_slippage: float = 0.2
    derivatives_slippage: float = 5.0
    commodities_slippage: float = 0.2

    def __post_init__(self):
        if self.target_levels is None:
            self.target_levels = [1, 2, 3, 4, 5]

def calculate_indicators(df: pd.DataFrame, config: StrategyConfig) -> pd.DataFrame:
    """Calculate all indicators needed for the strategy."""
    # Convert Pine Script indicators to Python
    # Example: EMA, ATR, RSI, etc.
    df['ema_fast'] = df['close'].ewm(span=config.ema_fast, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=config.ema_slow, adjust=False).mean()
    # ... more indicators
    return df

def generate_signals(df: pd.DataFrame, config: StrategyConfig) -> pd.DataFrame:
    """Generate BUY/SELL signals based on strategy logic."""
    # Implement your Pine Script signal logic
    df['signal'] = None
    # Example: EMA crossover
    df.loc[(df['ema_fast'] > df['ema_slow']) & (df['ema_fast'].shift(1) <= df['ema_slow'].shift(1)), 'signal'] = 'BUY'
    df.loc[(df['ema_fast'] < df['ema_slow']) & (df['ema_fast'].shift(1) >= df['ema_slow'].shift(1)), 'signal'] = 'SELL'
    return df

def backtest_target_level(data_files: list[Path], target_level: int, config: StrategyConfig):
    """Run backtest for a specific target level."""
    # Implement backtesting logic
    # Return: trades, file_stats, skip_counts
    pass
```

### 5. Implement Multi-Timeframe Runner

In the main script, implement:

```python
def discover_data_files_for_timeframe(repo_root: Path, markets: list[str], timeframe: str) -> list[Path]:
    """Find all data files for a specific timeframe."""
    files = []
    for market in markets:
        data_dir = repo_root / market / "data"
        if data_dir.exists():
            files.extend(sorted(data_dir.glob(f"*_{timeframe}.csv")))
    return sorted(files)

def run_timeframe(timeframe: str, data_files: list[Path], config: StrategyConfig):
    """Run backtest for a specific timeframe across all target levels."""
    # Iterate through target levels
    # Call backtest_target_level for each
    # Collect and return results
    pass

def main():
    """Main execution function."""
    # Parse arguments
    # Discover data files for each timeframe
    # Run backtests
    # Generate results
    pass
```

### 6. Implement Result Generation

Create comprehensive result summaries:

```python
def summary_for_timeframe_target(timeframe: str, target_level: int, trades: list, file_stats: list, skip_counts: dict, config: StrategyConfig) -> dict:
    """Generate summary statistics for a timeframe/target combination."""
    # Calculate: P&L, win rate, drawdown, Sharpe ratio, etc.
    # Return summary dictionary
    pass

def build_summary_markdown(payload: dict, config: StrategyConfig) -> str:
    """Generate human-readable markdown summary."""
    # Include: Executive summary, timeframe results, best trades, etc.
    pass
```

### 7. Handle Command-Line Arguments

Implement comprehensive argument parsing:

```python
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run <Strategy Name> backtests across multiple timeframes.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # Timeframes and markets
    parser.add_argument("--timeframes", nargs="+", default=list(DEFAULT_TIMEFRAMES))
    parser.add_argument("--markets", nargs="+", default=list(DEFAULT_MARKETS))

    # Strategy-specific parameters
    parser.add_argument("--ema-fast", type=int, default=9)
    parser.add_argument("--ema-slow", type=int, default=21)
    # ... more strategy parameters

    # Trading parameters
    parser.add_argument("--capital", type=float, default=1000000.0)
    parser.add_argument("--target-levels", nargs="+", type=int, default=[1, 2, 3, 4, 5])

    # Cost model
    parser.add_argument("--cost-multiplier", type=float, default=1.0)
    parser.add_argument("--equity-slippage", type=float, default=0.2)
    # ... more cost parameters

    # Session parameters
    parser.add_argument("--session-start", type=base.parse_clock, default=base.parse_clock("09:15"))
    parser.add_argument("--exit-time", type=base.parse_clock, default=base.parse_clock("15:20"))

    # Output options
    parser.add_argument("--write-trade-audit", action="store_true")
    parser.add_argument("--run-name", default="")

    return parser.parse_args()
```

### 8. Key Implementation Details

#### Data File Discovery
- Search for `*_<timeframe>.csv` files in each market's data directory
- Handle missing data gracefully
- Support multiple markets simultaneously

#### Timeframe Handling
- Normalize timeframe inputs (5m, 15m, 30m, 1h)
- Handle special cases (e.g., 30m candles aligned to 09:00/09:30)
- Adjust session rules per timeframe if needed

#### Cost Model
- Use `brokerage.md` reference for segment-wise charges
- Apply slippage per market type
- Calculate total costs accurately

#### Signal Processing
- Convert Pine Script signals to Python
- Handle signal inversion if needed
- Implement proper entry/exit logic

#### Result Organization
- Group results by timeframe and target level
- Create comparison tables
- Generate best/worst trade analysis
- Calculate comprehensive statistics

### 9. Testing and Validation

After implementation:

1. **Test with Single Timeframe**: Verify 5m backtest works correctly
2. **Test Multiple Timeframes**: Ensure all timeframes produce results
3. **Test Multiple Markets**: Verify all markets are included
4. **Validate Results**: Check P&L calculations, win rates, drawdowns
5. **Compare with Pine Script**: Ensure similar results (accounting for costs)

### 10. Documentation

Add comprehensive docstrings:
- Module-level documentation
- Function documentation
- Parameter descriptions
- Usage examples

## Example Usage

```bash
# Run with default parameters
cd common-strategies/python
python <strategy_name>_multi_timeframe.py

# Run with custom parameters
python <strategy_name>_multi_timeframe.py \
    --timeframes 5m 15m 30m \
    --markets equity usdinr \
    --ema-fast 8 --ema-slow 20 \
    --capital 500000 \
    --target-levels 1 2 3 \
    --cost-multiplier 1.0

# Run with trade audit
python <strategy_name>_multi_timeframe.py --write-trade-audit
```

## Important Notes

1. **Reuse Base Utilities**: Leverage functions from `open_low_high_5m_strategy.py` for common operations
2. **Follow Patterns**: Use `sniper_multi_timeframe.py` as a template for structure
3. **Handle Edge Cases**: Missing data, no signals, failed runs
4. **Cost Accuracy**: Use `brokerage.md` values for realistic cost modeling
5. **Performance**: Optimize for large datasets across multiple timeframes
6. **Error Handling**: Graceful failure with informative error messages
7. **Output Quality**: Clear, comprehensive results for analysis

## Success Criteria

- ✅ Script runs without errors on all markets and timeframes
- ✅ Results are written to correct directory structure
- ✅ All output files are generated (JSON, MD, CSV)
- ✅ Statistics are calculated correctly (P&L, win rate, drawdown, etc.)
- ✅ Results are comparable across timeframes and targets
- ✅ Command-line interface is flexible and well-documented
- ✅ Code follows Python best practices and is maintainable

## Troubleshooting

**Issue**: No data files found
- **Solution**: Check that data files exist in `*/data/*_<timeframe>.csv` format

**Issue**: Indicator calculations differ from Pine Script
- **Solution**: Verify parameter mappings and calculation methods

**Issue**: Cost calculations seem incorrect
- **Solution**: Review `brokerage.md` and ensure segment-wise charges are applied

**Issue**: Results don't match expectations
- **Solution**: Compare with Pine Script results, accounting for slippage and costs