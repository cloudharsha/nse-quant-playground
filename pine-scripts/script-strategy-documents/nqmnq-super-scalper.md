# NQ/MNQ Super Scalper

## Overview

This file is a true TradingView `strategy(...)`, not just an indicator. It is designed as a **1-minute NQ/MNQ futures scalping framework** that blends trend-following, ICT-style structure, order-flow proxies, session logic, and adaptive risk management.

From the code in [`NQMNQ Super Scalper.pine`](../scripts/NQMNQ%20Super%20Scalper.pine), the strategy is built for:

- `NQ` / `MNQ` index futures
- fixed 1-contract entries
- backtesting with `$15,000` initial capital
- `2` ticks slippage
- `$0.62` cash commission per contract
- pyramiding enabled in code

## Core Idea

The strategy tries to solve a real NQ scalping problem:

- the open behaves differently from lunch
- ETH behaves differently from RTH
- breakouts, pullbacks, and reversals should not be traded with the same thresholds

So instead of using one static setup, the script changes its behavior based on:

- session
- volatility
- trend strength
- higher-timeframe alignment
- structure
- volume and flow

In short, this is a **session-adaptive confluence scalper**.

## What The Strategy Uses

The script combines a large set of signals and context layers:

- EMA `9`, `21`, `100`, `200`
- VWAP and VWAP bands
- ATR-based dynamic volatility sizing
- ADX for trend strength
- RSI and MACD
- TTM Squeeze momentum
- AER regime detection
- ADF mean-reversion / trending test
- Hurst exponent for persistence vs mean reversion
- ICT concepts like `ORB`, `FVG`, `OTE`, `BOS/MSS`, order blocks, and liquidity sweeps
- previous day pivots, overnight range, and premarket range
- volume profile concepts like `POC`, `VAH`, `VAL`, and `PoV`
- external references:
  - `SPY` for relative strength
  - `ES1!` for SMT divergence
  - `QQQ` for round-number level mapping
  - `USI:TICK` for breadth
  - `CBOE:VIX` for risk regime

## Session Design

The script is heavily session-aware. It defines and treats these periods differently:

- RTH
- Asia
- London
- premarket
- opening hour
- lunch
- afternoon
- last hour

This matters because many thresholds are dynamic:

- ATR speed changes by session
- regime tests change by session
- entry quality thresholds change by session
- stop-loss and take-profit distances change by session
- some signals are loosened at the open and tightened in thin sessions

That is one of the main reasons this strategy is used: **NQ is not one market all day long**.

## Entry Architecture

The strategy has **six entry paths**. They are prioritized so one higher-priority setup can block lower-priority ones on the same bar.

### 1. MAIN

The main signal is the primary trend-continuation engine.

It requires:

- trend alignment
- RSI confirmation
- a structure break
- liquidity confirmation
- one of these location triggers:
  - ORB breakout retest
  - ORB failure / S&R rotation
  - OTE zone location

It also must pass:

- directional vetoes
- structural vetoes
- EMA100 trend alignment
- overextension filters

This is the cleanest “with-trend continuation” path in the script.

### 2. BOS

`BOS/MSS` trades fire when price breaks a recent structural high or low with enough force.

The script scores BOS quality using factors like:

- higher-timeframe alignment
- VWAP position
- ADX
- AER trend regime
- kill-zone timing
- FVG creation
- EMA21 support/resistance
- strong relative volume
- delta / buy-sell ratio confirmation
- candlestick quality
- confirmed structure continuation

This path is used when the strategy wants to trade **real structural expansion**, not just a small breakout.

### 3. OB

The order block path looks for:

- a strong impulsive move
- the last opposite candle before displacement
- FVG support
- kill-zone timing
- strong relative volume
- higher-timeframe agreement

This is an ICT-style continuation entry that assumes institutions defended a zone and price is likely to continue from it.

### 4. RE

The retest path is a pullback entry.

Examples:

- bullish retest: price dips under `EMA21` in an uptrend, then closes back above it
- bearish retest: price pokes above `EMA21` in a downtrend, then closes back below it

The strategy then scores the pullback using:

- ADX
- volume
- VWAP alignment
- higher-timeframe trend
- candle quality
- delta alignment

This path is used for **buy-the-dip / sell-the-rally** behavior inside an established move.

### 5. TRAP

The trap path trades liquidity sweeps and fake breaks.

It looks for:

- price sweeping a recent high or low
- a close back inside the range
- meaningful wick size
- wick/body quality
- volume expansion
- range expansion
- statistically significant wick behavior

This is the reversal path for moments when breakout traders get trapped.

### 6. OD

The opening drive path is specialized for:

- the first few bars after the RTH open
- major economic release windows
- the 10:00 ET second-wave data window

It uses:

- opening impulse direction
- volume spike detection
- bar body quality
- premarket bias
- overnight range context
- previous day levels
- higher-timeframe agreement
- structural and delta confirmation

This path exists because NQ often makes its fastest and cleanest scalping moves around the open and data releases.

## Main Filters And Vetoes

This strategy does not blindly fire every setup. It uses several layers of blocking logic:

- higher-timeframe confluence score
- directional score built from many independent factors
- structural veto rules
- short-side extra filters
- macro veto rules
- EMA100 trend-alignment veto
- overextension filters
- session restrictions
- ETH toggle

A major design choice is that **shorts are treated more strictly** than longs, because the script assumes NQ has an upward structural bias more often than not.

## Confidence Model

The strategy has a unified confidence model for longs and shorts. It scores trades using factors such as:

- higher-timeframe confluence
- overall directional score
- swing-structure agreement
- flow / delta agreement
- distance from EMA21
- squeeze momentum timing
- Bollinger band position
- nearby support or resistance quality

That score is then reused across several entry paths instead of maintaining totally separate rating systems for every setup.

## Risk Management

Risk handling is one of the most important parts of this script.

### Stop-Loss Logic

Stops are not static. They adapt using:

- ATR
- session
- regime
- ADX
- volume
- structure
- path-specific logic

Examples:

- general session SL functions for main/BOS/RE
- OB stops placed around order-block structure
- trap stops placed around sweep wicks
- OD stops using opening-drive buffers

### Take-Profit Logic

Targets are also dynamic. The script tries to use the nearest meaningful level first, including:

- pivots
- ORB highs/lows
- overnight levels
- FVG zones
- order block midpoints
- HVB zones
- QQQ mapped levels
- volume profile references

If no strong nearby level exists, it falls back to ATR-based dynamic distance logic.

Each path then modifies the TP differently:

- `BOS` can run wider
- `RE` is a bit more conservative
- `OB` is moderate
- `TRAP` is tighter
- `OD` uses its own risk/reward framework

There is also a `minProfit` floor of `5` points before a trade is accepted.

## Exit Behavior

The code contains a large smart-exit framework with `20` exit patterns for longs and `20` for shorts. Those patterns look at things like:

- reversal candles
- adverse momentum
- BOS against the trade
- CHoCH
- SMT divergence
- squeeze reversals
- divergences
- PoV / flow behavior

However, in the current backtest file:

- `smartExitL = false`
- `smartExitS = false`

So the smart pattern exits are effectively disabled, and the active backtest behavior is mainly:

- hard stop-loss
- hard take-profit

This is important because the script contains more exit logic than the backtest is currently using.

## Why This Strategy Is Used

This strategy is useful for traders who want to scalp NQ/MNQ with more structure than a simple EMA crossover or single-indicator system.

It is used because it tries to combine:

- trend continuation
- pullback entries
- breakout entries
- reversal traps
- open-drive special handling
- adaptive risk sizing
- multi-session behavior

That makes it suitable for a market like NQ, where:

- momentum can be explosive
- fake breakouts are common
- the open is very different from lunch
- overnight conditions often require different rules than regular hours

## Strengths

- multiple entry models inside one framework
- strong session awareness
- adaptive thresholds instead of fixed numbers everywhere
- combines structure, momentum, volume, and macro context
- built specifically for fast index-futures behavior
- risk logic is more sophisticated than most simple scalping scripts

## Limitations

- very high complexity
- many moving parts can make optimization fragile
- heavy dependence on derived signals and proxies rather than true order-book data
- external symbols like `SPY`, `ES1!`, `QQQ`, `TICK`, and `VIX` must behave reliably
- more rules can reduce interpretability
- the smart exit engine exists but is disabled in the current backtest

## Important Implementation Notes

Two code details are worth calling out:

1. The header comment says `Pyramiding=6`, but the actual `strategy()` call uses `pyramiding=20`.
2. The script includes a smart-exit architecture, but it is disabled in the current backtest build.

So the best way to understand the live behavior of this file is:

- multi-path adaptive entry engine
- dynamic SL/TP placement
- stop/target-based backtest execution

## Practical Summary

This strategy is best understood as a **session-adaptive NQ/MNQ scalping system** that merges:

- trend continuation
- ICT structure
- order-flow proxies
- volume-profile context
- aggressive open-drive logic
- dynamic stop and target placement

It is used to trade different market conditions with different rule sets instead of forcing one static setup onto all hours of the day.
