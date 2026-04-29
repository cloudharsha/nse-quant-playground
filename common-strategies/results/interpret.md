# How To Interpret Strategy Result Files

Each folder under `common-strategies/results/` is one backtest run. The folder
name usually tells you the strategy, whether it was normal/inverse/no-cost, and
the timestamp when it was generated.

Start with `summary.md`, then use the CSV files to answer specific questions.

## Recommended Reading Order

1. Open `summary.md`
2. Check `Testing Scope`
3. Check `Cost Model`
4. Read the comparison table (`target_comparison.csv` or `method_comparison.csv`)
5. Check `market_metrics*.csv`
6. Check `instrument_metrics*.csv`
7. Use `datewise_pnl*.csv`, `equity_curve*.csv`, and `trades*.csv` for details

## Common Files

### `summary.md`

Human-readable summary of the run.

Use it to quickly understand:

- strategy tested
- markets tested
- timeframe
- whether brokerage/slippage were included
- total trades
- win rate
- net P&L
- max drawdown
- profit factor
- Sharpe ratio
- output files generated

Always check the `Cost Model` section before comparing results.

Example:

```text
brokerage_calculated: False
slippage_calculated: False
pnl_basis: Gross P&L; brokerage and slippage disabled
```

This means the result ignores brokerage, charges, and slippage.

If it says:

```text
brokerage_calculated: True
slippage_calculated: True
pnl_basis: Net P&L after brokerage and slippage
```

then the headline P&L already includes trading costs.

### `summary.json`

Machine-readable version of `summary.md`.

Use this if you want to process results later with Python, dashboards, or
comparison scripts.

### `run_config.json`

The exact parameters used for the run.

Use it to confirm:

- markets tested
- data files included
- capital
- risk per trade
- target levels
- brokerage/slippage values
- session start and exit time
- whether inverse signals were used

This file is useful when two result folders look similar but were run with
different settings.

## Sniper Strategy Files

Sniper result folders usually contain files with `tp1`, `tp2`, `tp3`, `tp4`,
and `tp5`.

### What TP1, TP2, TP3, TP4, TP5 Mean

`TP` means take-profit target.

The Sniper strategy uses:

```text
risk = ATR(14) * 1.5
```

For a BUY trade:

```text
SL  = entry - risk
TP1 = entry + 1 * risk
TP2 = entry + 2 * risk
TP3 = entry + 3 * risk
TP4 = entry + 4 * risk
TP5 = entry + 5 * risk
```

For a SELL trade:

```text
SL  = entry + risk
TP1 = entry - 1 * risk
TP2 = entry - 2 * risk
TP3 = entry - 3 * risk
TP4 = entry - 4 * risk
TP5 = entry - 5 * risk
```

Each TP file is a separate test where the full position exits at that target.

### `target_comparison.csv`

Best first file for Sniper runs.

Shows one row per target level:

- TP1
- TP2
- TP3
- TP4
- TP5

Columns:

- `target_level`: target tested
- `total_trades`: number of trades
- `win_rate_pct`: percentage of winning trades
- `net_pnl`: total P&L for that target variant
- `ending_equity`: starting capital plus net P&L
- `average_profit_loss`: average P&L per trade
- `max_drawdown`: worst equity drop in money
- `max_drawdown_pct`: worst equity drop in percent
- `profit_factor`: gross profit divided by gross loss
- `sharpe_ratio`: risk-adjusted return estimate

Use this file to decide which target variant performed best.

### `market_metrics_tp*.csv`

Shows performance by market group:

- `commodities`
- `derivatives`
- `equity`

Use this to answer:

```text
How much did commodities make?
How much did derivatives make?
How much did equity make?
```

Example:

```text
market,trades,net_pnl,profit_factor
commodities,321,-12688.34,0.8299
derivatives,251,10203.88,1.4161
equity,509,33683.53,1.4398
```

This tells you the total P&L came mainly from equity and derivatives, while
commodities lost money.

### `instrument_metrics_tp*.csv`

Shows performance by individual symbol/instrument.

Use this to answer:

```text
Which stock/index/commodity made money?
Which instrument caused the drawdown?
```

Important columns:

- `market`
- `instrument`
- `trades`
- `win_rate_pct`
- `net_pnl`
- `best_trade`
- `worst_trade`
- `profit_factor`

### `datewise_pnl_tp*.csv`

Shows daily P&L.

Use this to answer:

```text
Which days made money?
Which days lost money?
Was profit from one lucky day or many days?
```

Important columns:

- `date`
- `trades`
- `wins`
- `losses`
- `gross_pnl`
- `costs`
- `net_pnl`
- `day_return_pct`
- `ending_equity`
- `drawdown`
- `drawdown_pct`

If `costs` is `0.0`, brokerage and slippage were disabled for that result.

### `equity_curve_tp*.csv`

Shows equity after every closed trade.

Use this to understand:

- how smoothly the strategy grew or fell
- when drawdown happened
- whether the system recovered after losses

Important columns:

- `trade_number`
- `exit_time`
- `net_pnl`
- `equity`
- `drawdown`
- `drawdown_pct`

### `trades_tp*.csv`

Detailed trade log.

Use this when you want to inspect individual trades.

Important columns:

- `market`
- `instrument`
- `signal`
- `original_signal`
- `direction`
- `signal_time`
- `entry_time`
- `entry_price`
- `stop_price`
- `target_price`
- `exit_time`
- `exit_price`
- `exit_reason`
- `quantity`
- `gross_pnl`
- `costs`
- `net_pnl`
- `r_multiple`
- `bias`
- `bull_score_pct`
- `bear_score_pct`

Common exit reasons:

- `TP1`, `TP2`, `TP3`, `TP4`, `TP5`: target hit
- `STOP_LOSS`: stop-loss hit
- `OPPOSITE_SIGNAL`: opposite EMA signal appeared
- `SESSION_END`: exited at end of intraday session
- `FINAL_BAR`: exited at final available candle

### `best_worst_trades_tp*.csv`

Shows the top best and worst trades for that target variant.

Use this to inspect outliers:

- largest winning trades
- largest losing trades
- whether one instrument dominates results

## Open = Low / Open = High Files

These folders do not have TP1-TP5 suffixes unless a variant script creates
multiple methods. The basic files are:

### `trades.csv`

All trades from the Open = Low / Open = High strategy.

Important columns:

- `market`
- `instrument`
- `session_date`
- `setup`
- `direction`
- `first_open`
- `first_high`
- `first_low`
- `entry_price`
- `stop_price`
- `target_price`
- `exit_reason`
- `quantity`
- `gross_pnl`
- `costs`
- `net_pnl`
- `r_multiple`

### `instrument_metrics.csv`

Performance by instrument.

Use it to find which symbols worked and which failed.

### `datewise_pnl.csv`

Daily P&L across all tested instruments.

### `equity_curve.csv`

Equity after every closed trade.

### `best_worst_trades.csv`

Best and worst trades in the run.

## Position Sizing Files

The position sizing run compares multiple sizing methods:

- `fixed_fractional`
- `volatility_adjusted`
- `fractional_kelly`

### `method_comparison.csv`

Best first file for position sizing runs.

Shows one row per sizing method:

- total trades
- win rate
- net P&L
- ending equity
- max drawdown
- profit factor
- Sharpe ratio

### `trades_fixed_fractional.csv`

Trades using fixed percentage risk per trade.

### `trades_volatility_adjusted.csv`

Trades using fixed percentage risk plus ATR/volatility cap.

### `trades_fractional_kelly.csv`

Trades using capped fractional Kelly after a warmup period.

## Important Metrics

### Net P&L

Total profit/loss for the run.

If costs are enabled, this is after brokerage and slippage.

If costs are disabled, this is gross strategy P&L.

### Win Rate

Percentage of trades that made money.

A high win rate does not always mean a good strategy. A low win rate can still
work if winners are much larger than losers.

### Profit Factor

```text
profit_factor = gross_profit / gross_loss
```

Interpretation:

- `< 1.0`: losing strategy
- `= 1.0`: break-even before other risks
- `> 1.0`: profitable in the tested data
- `> 1.5`: stronger, but still needs validation

### Max Drawdown

Worst fall from an equity peak.

This tells you how painful the strategy was during the test.

### Sharpe Ratio

Risk-adjusted return estimate based on daily returns.

Higher is better, but for short backtests like one month, treat Sharpe as a
rough indicator only.

### R Multiple

Profit/loss measured relative to initial trade risk.

Example:

```text
r_multiple = 2.0
```

means the trade made about 2 times the amount risked.

## Charged Vs No-Cost Results

Charged runs include:

- brokerage
- slippage

No-cost runs set both to zero.

Compare these carefully. If a strategy is profitable only when costs are zero,
it may be too active or too sensitive to real execution costs.

For example:

- charged Sniper results were deeply negative
- no-cost Sniper TP2-TP5 became positive

That means trading costs were a major reason the charged strategy failed.

## Normal Vs Inverse Sniper

Normal Sniper:

```text
BUY signal  -> LONG trade
SELL signal -> SHORT trade
```

Inverse Sniper:

```text
BUY signal  -> SHORT trade
SELL signal -> LONG trade
```

Do not expect inverse results to be exactly the negative of normal results.
Stops, targets, same-candle ambiguity, skipped trades, and session exits make
the result path-dependent.

## Practical Checklist

When reviewing any result folder:

1. Is brokerage/slippage enabled?
2. What date range was tested?
3. Which markets were included?
4. Which TP or sizing method has the best profit factor?
5. Is net P&L positive?
6. Is max drawdown acceptable?
7. Did one market or one instrument create most of the profit?
8. Is the result still good after costs?
9. Are there enough trading days to trust the result?

For the current data, most runs cover approximately:

```text
2026-03-30 to 2026-04-29
```

That is about one calendar month, so treat results as exploratory rather than
final proof of a strategy.
