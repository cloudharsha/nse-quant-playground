# Open = Low / Open = High Strategy Backtest

## Summary

- **strategy**: Open = Low / Open = High Strategy (5-min timeframe)
- **starting_capital**: 1000000.0
- **ending_equity**: 159796.45
- **net_pnl**: -840203.55
- **total_trades**: 138
- **total_costs**: 636178.84
- **wins**: 44
- **losses**: 94
- **win_rate_pct**: 31.88
- **average_profit_loss**: -6088.43
- **average_win**: 6259.76
- **average_loss**: -11868.43
- **max_drawdown**: -886519.22
- **max_drawdown_pct**: -88.6519
- **profit_factor**: 0.2469
- **sharpe_ratio**: -9.6693
- **markets_tested**: commodities,derivatives,equity
- **files_tested**: 20
- **sessions_tested**: 405
- **candles_tested**: 48989
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

## Testing Scope

- **markets_tested**: commodities,derivatives,equity
- **timeframe**: 5-minute candles
- **files_tested**: 20
- **sessions_tested**: 405
- **candles_tested**: 48989
- **total_trades**: 138

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

## Skip Counts

- **ambiguous_first_candle**: 22
- **missing_session_open**: 20
- **no_breakdown_entry**: 33
- **no_breakout_entry**: 25
- **no_open_low_high_setup**: 167

## Parameters

- **tolerance_pct**: 0.1
- **stop_buffer_pct**: 0.02
- **target_type**: rr
- **risk_reward**: 2.0
- **target_pct**: 0.75
- **trailing_stop_pct**: 0.0
- **capital**: 1000000.0
- **risk_per_trade_pct**: 1.0
- **max_allocation_pct**: 100.0
- **min_first_candle_volume**: 0.0
- **min_average_volume**: 0.0
- **max_gap_pct**: 0.0
- **cost_multiplier**: 1.0
- **equity_slippage**: 0.2
- **derivatives_slippage**: 5.0
- **commodities_slippage**: 0.2
- **session_start**: 09:15
- **exit_time**: 15:20
- **require_session_open**: True
- **ambiguous_policy**: stop_first
- **top_trade_count**: 10

## Output Files

- `trades.csv`
- `datewise_pnl.csv`
- `equity_curve.csv`
- `instrument_metrics.csv`
- `best_worst_trades.csv`
- `summary.json`
- `run_config.json`
- `summary.md`
