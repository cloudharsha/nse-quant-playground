# Sniper Entry/Exit 5m Backtest

## Target Comparison

| Target | Trades | Win Rate % | Net P&L | Ending Equity | Max DD % | Profit Factor | Sharpe |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| TP1 | 1081 | 44.96 | -6540.62 | 93459.38 | -16.9526 | 0.9562 | -1.4779 |
| TP2 | 1081 | 34.14 | 5750.57 | 105750.57 | -12.7072 | 1.0334 | 1.4964 |
| TP3 | 1081 | 32.19 | 18634.84 | 118634.84 | -10.5793 | 1.1064 | 3.9623 |
| TP4 | 1081 | 32.1 | 25357.99 | 125357.99 | -8.5214 | 1.1445 | 5.0788 |
| TP5 | 1081 | 32.01 | 31199.07 | 131199.07 | -10.2682 | 1.1776 | 5.319 |

## Testing Scope

- **markets_tested**: commodities,derivatives,equity
- **timeframe**: 5-minute candles
- **files_tested**: 20
- **sessions_tested**: 385
- **candles_tested**: 27415
- **trade_variants_tested**: TP1, TP2, TP3, TP4, TP5

## Cost Model

- **brokerage_calculated**: False
- **slippage_calculated**: False
- **brokerage_entry_fee**: 0.0
- **brokerage_exit_fee**: 0.0
- **other_charges**: 0.0
- **fixed_cost_per_trade**: 0.0
- **equity_slippage**: 0.0
- **derivatives_slippage**: 0.0
- **commodities_slippage**: 0.0
- **pnl_basis**: Gross P&L; brokerage and slippage disabled

## Backtest Rules

- Signal uses EMA 9 / EMA 21 crossovers from 5-minute candles.
- Original BUY signals are traded as LONG and original SELL signals are traded as SHORT.
- Entry is the next candle open after signal close to avoid lookahead.
- Stop and TP levels are anchored to the signal candle close, matching the indicator's plotted entry lines.
- TP1 through TP5 are tested as separate full-position exits.
- Trades also exit on stop, opposite signal, session end, or final bar.

## Skip Counts

### TP1
- **invalid_or_unsized_entry**: 38
- **signal_without_next_session_bar**: 12

### TP2
- **invalid_or_unsized_entry**: 38
- **signal_without_next_session_bar**: 12

### TP3
- **invalid_or_unsized_entry**: 38
- **signal_without_next_session_bar**: 12

### TP4
- **invalid_or_unsized_entry**: 38
- **signal_without_next_session_bar**: 12

### TP5
- **invalid_or_unsized_entry**: 38
- **signal_without_next_session_bar**: 12

## Parameters

- **ema_fast**: 9
- **ema_slow**: 21
- **atr_period**: 14
- **atr_multiplier**: 1.5
- **rsi_period**: 14
- **macd_fast**: 12
- **macd_slow**: 26
- **macd_signal**: 9
- **adx_period**: 14
- **adx_smoothing**: 14
- **volume_sma_period**: 20
- **capital**: 100000.0
- **risk_per_trade_pct**: 1.0
- **max_allocation_pct**: 100.0
- **brokerage_entry_fee**: 0.0
- **brokerage_exit_fee**: 0.0
- **other_charges**: 0.0
- **equity_slippage**: 0.0
- **derivatives_slippage**: 0.0
- **commodities_slippage**: 0.0
- **session_start**: 09:15
- **exit_time**: 15:20
- **require_session_open**: True
- **exit_at_session_end**: True
- **ambiguous_policy**: stop_first
- **target_levels**: (1, 2, 3, 4, 5)
- **invert_signals**: False
- **top_trade_count**: 10

## Output Files

- `trades_tp1.csv`
- `datewise_pnl_tp1.csv`
- `equity_curve_tp1.csv`
- `market_metrics_tp1.csv`
- `instrument_metrics_tp1.csv`
- `best_worst_trades_tp1.csv`
- `trades_tp2.csv`
- `datewise_pnl_tp2.csv`
- `equity_curve_tp2.csv`
- `market_metrics_tp2.csv`
- `instrument_metrics_tp2.csv`
- `best_worst_trades_tp2.csv`
- `trades_tp3.csv`
- `datewise_pnl_tp3.csv`
- `equity_curve_tp3.csv`
- `market_metrics_tp3.csv`
- `instrument_metrics_tp3.csv`
- `best_worst_trades_tp3.csv`
- `trades_tp4.csv`
- `datewise_pnl_tp4.csv`
- `equity_curve_tp4.csv`
- `market_metrics_tp4.csv`
- `instrument_metrics_tp4.csv`
- `best_worst_trades_tp4.csv`
- `trades_tp5.csv`
- `datewise_pnl_tp5.csv`
- `equity_curve_tp5.csv`
- `market_metrics_tp5.csv`
- `instrument_metrics_tp5.csv`
- `best_worst_trades_tp5.csv`
- `target_comparison.csv`
- `summary.json`
- `run_config.json`
- `summary.md`
