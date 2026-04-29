# Sniper Entry/Exit 5m Backtest

## Target Comparison

| Target | Trades | Win Rate % | Net P&L | Ending Equity | Max DD % | Profit Factor | Sharpe |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| TP1 | 1081 | 41.63 | -109174.82 | -9174.82 | -109.1748 | 0.4735 | -3.6955 |
| TP2 | 1081 | 28.86 | -96930.07 | 3069.93 | -98.4939 | 0.5997 | -4.8032 |
| TP3 | 1081 | 26.18 | -84046.46 | 15953.54 | -87.2109 | 0.6606 | -11.8608 |
| TP4 | 1081 | 25.99 | -77282.58 | 22717.42 | -82.3802 | 0.6886 | -10.7116 |
| TP5 | 1081 | 25.72 | -71444.23 | 28555.77 | -79.6651 | 0.7125 | -9.5233 |

## Testing Scope

- **markets_tested**: commodities, derivatives, equity
- **timeframe**: 5-minute candles
- **files_tested**: 20
- **sessions_tested**: 385
- **candles_tested**: 27415
- **trade_variants_tested**: TP1, TP2, TP3, TP4, TP5

## Cost Model

- **brokerage_calculated**: True
- **slippage_calculated**: True
- **brokerage_bps**: 3.0
- **slippage_bps**: 2.0
- **pnl_basis**: Net P&L after brokerage and slippage

## Backtest Rules

- Signal uses EMA 9 / EMA 21 crossovers from 5-minute candles.
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
- **brokerage_bps**: 3.0
- **slippage_bps**: 2.0
- **session_start**: 09:15
- **exit_time**: 15:20
- **require_session_open**: True
- **exit_at_session_end**: True
- **ambiguous_policy**: stop_first
- **target_levels**: (1, 2, 3, 4, 5)
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
