# Sniper Entry/Exit 5m Backtest

## Target Comparison

| Target | Trades | Win Rate % | Net P&L | Ending Equity | Max DD % | Profit Factor | Sharpe |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| TP1 | 73 | 50.68 | -29857.74 | 970142.26 | -7.179 | 0.788 | -2.9082 |
| TP2 | 73 | 43.84 | -36725.36 | 963274.64 | -8.2342 | 0.7749 | -3.3822 |
| TP3 | 73 | 43.84 | -45171.87 | 954828.13 | -8.5462 | 0.7232 | -4.0263 |
| TP4 | 73 | 43.84 | -41762.18 | 958237.82 | -8.5462 | 0.7441 | -3.5835 |
| TP5 | 73 | 43.84 | -43810.27 | 956189.73 | -8.5462 | 0.7315 | -3.8482 |

## Testing Scope

- **markets_tested**: derivatives
- **timeframe**: 5-minute candles
- **files_tested**: 5
- **sessions_tested**: 85
- **candles_tested**: 2125
- **trade_variants_tested**: TP1, TP2, TP3, TP4, TP5

## Cost Model

- **brokerage_calculated**: True
- **slippage_calculated**: True
- **cost_model**: Segment-wise brokerage calculator rates from brokerage.md
- **cost_multiplier**: 1.0
- **reference_buy_value**: 1000000.0
- **reference_sell_value**: 1000000.0
- **intraday_equity_reference_total_charges**: 402.01
- **futures_reference_total_charges**: 612.75
- **options_reference_total_charges**: 2418.07
- **commodity_futures_reference_total_charges**: 17239.2
- **equity_slippage**: 0.2
- **derivatives_slippage**: 5.0
- **commodities_slippage**: 0.2
- **pnl_basis**: Net P&L after segment-wise brokerage/charges and fixed slippage

## Backtest Rules

- Signal uses EMA 9 / EMA 21 crossovers from 5-minute candles.
- Original BUY signals are traded as LONG and original SELL signals are traded as SHORT.
- Entry is the next candle open after signal close to avoid lookahead.
- Stop and TP levels are anchored to the signal candle close, matching the indicator's plotted entry lines.
- TP1 through TP5 are tested as separate full-position exits.
- Trades also exit on stop, opposite signal, session end, or final bar.

## Skip Counts

### TP1
- **invalid_or_unsized_entry**: 11
- **signal_without_next_session_bar**: 1

### TP2
- **invalid_or_unsized_entry**: 11
- **signal_without_next_session_bar**: 1

### TP3
- **invalid_or_unsized_entry**: 11
- **signal_without_next_session_bar**: 1

### TP4
- **invalid_or_unsized_entry**: 11
- **signal_without_next_session_bar**: 1

### TP5
- **invalid_or_unsized_entry**: 11
- **signal_without_next_session_bar**: 1

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
- **cost_multiplier**: 1.0
- **equity_slippage**: 0.2
- **derivatives_slippage**: 5.0
- **commodities_slippage**: 0.2
- **session_start**: 09:15
- **exit_time**: 15:20
- **require_session_open**: True
- **exit_at_session_end**: True
- **ambiguous_policy**: stop_first
- **target_levels**: (1, 2, 3, 4, 5)
- **invert_signals**: False
- **top_trade_count**: 10

## Output Files

