# Fibonacci Bollinger Bands

## Overview

This script is a TradingView overlay indicator built with `study(...)`, not a Pine `strategy(...)`. That means it does not contain entry, exit, stop-loss, or position-sizing rules by itself. Instead, it plots a volatility framework that a trader can use to make discretionary trading decisions.

The script combines:

- a `VWMA` (Volume Weighted Moving Average) as the centerline
- a standard deviation band expansion, similar to Bollinger Bands
- Fibonacci ratios to create multiple staged upper and lower bands

## What The Script Calculates

From the code in [`fibonaaci-bolinger.pine`](../scripts/fibonaaci-bolinger.pine):

- `length = 200`
- `src = hlc3`
- `mult = 3.0`
- `basis = vwma(src, length)`
- `dev = mult * stdev(src, length)`

The centerline is the 200-period VWMA of `hlc3`, where:

- `hlc3 = (high + low + close) / 3`

The script then creates six upper bands and six lower bands using Fibonacci ratios of the deviation:

- `0.236`
- `0.382`
- `0.5`
- `0.618`
- `0.764`
- `1.0`

Formula pattern:

```text
Upper band = basis + (ratio * dev)
Lower band = basis - (ratio * dev)
```

## Why This Strategy Framework Is Used

The idea is to measure how far price has moved away from a volume-sensitive fair-value line and to split that move into meaningful zones.

This is useful because:

- the `VWMA` gives more importance to higher-volume candles, which can make the centerline more relevant than a simple moving average in active markets
- standard deviation adapts the band width to current volatility
- Fibonacci band steps create progressive zones instead of a single outer Bollinger boundary

In practice, traders use this kind of structure to answer three questions:

1. Is price trading around fair value or stretched away from it?
2. If price pulls back, which band might act as support or resistance?
3. If price is extended, is the move strong enough to continue or likely to mean-revert?

## Typical Trading Interpretation

### 1. Trend Context

- Price above the VWMA basis suggests bullish context.
- Price below the VWMA basis suggests bearish context.

The basis acts like a dynamic equilibrium line.

### 2. Pullback Zones

In an uptrend:

- lower Fibonacci bands can act as staged support zones
- traders may look for bounce setups from `0.236`, `0.382`, or `0.5`

In a downtrend:

- upper Fibonacci bands can act as staged resistance zones
- traders may look for rejection setups from the matching upper bands

### 3. Overextension / Mean Reversion

Touches near the `0.764` or `1.0` bands often indicate that price is stretched relative to recent volatility.

That can be used in two ways:

- mean-reversion traders may expect a move back toward the basis
- trend traders may treat repeated closes outside inner bands as proof of strong momentum

### 4. Scaling Entries And Exits

Because the bands are layered, traders can:

- scale into positions gradually instead of entering all at once
- reduce exposure step by step as price returns toward the basis or reaches outer bands

## Best Use Cases

This framework is usually most useful when:

- the market alternates between trend and pullback phases
- the trader wants a structured way to map support and resistance
- volatility matters for timing entries
- volume-weighted mean price is more meaningful than a plain average

The default `length = 200` makes this a relatively slow, higher-context indicator. It is more suited to broader trend structure than ultra-fast scalping unless the user changes the inputs.

## Strengths

- combines trend, volatility, and volume sensitivity in one view
- provides more granular zones than standard Bollinger Bands
- useful for both trend-following and mean-reversion interpretation
- easy to use for staged entries, exits, and risk planning

## Limitations

- no actual trade rules are coded
- no alerts, entry conditions, or exit conditions are defined
- no backtesting is possible unless it is rewritten as a Pine `strategy(...)`
- Fibonacci ratios here are used as spacing levels, not as proof of predictive market behavior
- wide default settings (`length = 200`, `mult = 3.0`) may react slowly in fast markets

## Practical Summary

This script is best understood as a **Fibonacci-layered Bollinger framework around a 200-period VWMA**.

Traders use it to:

- identify the main directional bias from the VWMA basis
- locate pullback and resistance zones using the inner Fibonacci bands
- detect stretched price conditions using the outer bands
- manage entries and exits in a more structured way

If you want this turned into a true strategy, the next step would be to define exact rules such as:

- long only above the basis
- enter on bounce from `lower_2` or `lower_3`
- take profit at the basis or upper bands
- stop below `lower_6`

That logic is not present in the current script, but this indicator provides the structure needed to build it.
