# Inverse Sniper Entry/Exit 5m Backtest

## Target Comparison

| Target | Trades | Win Rate % | Net P&L | Ending Equity | Max DD % | Profit Factor | Sharpe |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| TP1 | 1084 | 54.52 | 49397.68 | 1049397.68 | -9.6267 | 1.0331 | 1.4357 |
| TP2 | 1084 | 51.29 | 70827.36 | 1070827.36 | -11.0188 | 1.0443 | 1.738 |
| TP3 | 1084 | 51.11 | 98971.29 | 1098971.29 | -10.5243 | 1.0618 | 2.2329 |
| TP4 | 1084 | 51.01 | 107152.89 | 1107152.89 | -10.2156 | 1.067 | 2.3585 |
| TP5 | 1084 | 51.11 | 105522.76 | 1105522.76 | -10.0229 | 1.0661 | 2.3542 |

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
- **cost_model**: Segment-wise brokerage calculator rates from brokerage.md
- **cost_multiplier**: 0.0
- **reference_buy_value**: 1000000.0
- **reference_sell_value**: 1000000.0
- **intraday_equity_reference_total_charges**: 402.01
- **futures_reference_total_charges**: 612.75
- **options_reference_total_charges**: 2418.07
- **commodity_futures_reference_total_charges**: 17239.2
- **equity_slippage**: 0.0
- **derivatives_slippage**: 0.0
- **commodities_slippage**: 0.0
- **pnl_basis**: Gross P&L; brokerage and slippage disabled

## Backtest Rules

- Signal uses EMA 9 / EMA 21 crossovers from 5-minute candles.
- In inverse mode, original BUY signals are traded as SHORT and original SELL signals are traded as LONG.
- Entry is the next candle open after signal close to avoid lookahead.
- Stop and TP levels are anchored to the signal candle close, matching the indicator's plotted entry lines.
- TP1 through TP5 are tested as separate full-position exits.
- Trades also exit on stop, opposite signal, session end, or final bar.

## Skip Counts

### TP1
- **invalid_or_unsized_entry**: 35
- **signal_without_next_session_bar**: 12

### TP2
- **invalid_or_unsized_entry**: 35
- **signal_without_next_session_bar**: 12

### TP3
- **invalid_or_unsized_entry**: 35
- **signal_without_next_session_bar**: 12

### TP4
- **invalid_or_unsized_entry**: 35
- **signal_without_next_session_bar**: 12

### TP5
- **invalid_or_unsized_entry**: 35
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
- **capital**: 1000000.0
- **risk_per_trade_pct**: 1.0
- **max_allocation_pct**: 100.0
- **cost_multiplier**: 0.0
- **equity_slippage**: 0.0
- **derivatives_slippage**: 0.0
- **commodities_slippage**: 0.0
- **session_start**: 09:15
- **exit_time**: 15:20
- **require_session_open**: True
- **exit_at_session_end**: True
- **ambiguous_policy**: stop_first
- **target_levels**: (1, 2, 3, 4, 5)
- **invert_signals**: True
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
