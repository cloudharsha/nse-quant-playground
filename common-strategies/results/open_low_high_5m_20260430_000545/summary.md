# Open = Low / Open = High Strategy Backtest

## Summary

- **strategy**: Open = Low / Open = High Strategy (5-min timeframe)
- **starting_capital**: 100000.0
- **ending_equity**: 72705.32
- **net_pnl**: -27294.68
- **total_trades**: 138
- **total_costs**: 6900.0
- **wins**: 50
- **losses**: 88
- **win_rate_pct**: 36.23
- **average_profit_loss**: -197.79
- **average_win**: 652.8
- **average_loss**: -681.08
- **max_drawdown**: -33887.44
- **max_drawdown_pct**: -33.0325
- **profit_factor**: 0.5446
- **sharpe_ratio**: -7.3841
- **markets_tested**: commodities,derivatives,equity
- **files_tested**: 20
- **sessions_tested**: 405
- **candles_tested**: 48989
- **brokerage_calculated**: True
- **slippage_calculated**: True
- **brokerage_entry_fee**: 20.0
- **brokerage_exit_fee**: 20.0
- **other_charges**: 10.0
- **fixed_cost_per_trade**: 50.0
- **equity_slippage**: 0.2
- **derivatives_slippage**: 5.0
- **commodities_slippage**: 0.2
- **pnl_basis**: Net P&L after fixed brokerage/charges and fixed slippage

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
- **brokerage_entry_fee**: 20.0
- **brokerage_exit_fee**: 20.0
- **other_charges**: 10.0
- **fixed_cost_per_trade**: 50.0
- **equity_slippage**: 0.2
- **derivatives_slippage**: 5.0
- **commodities_slippage**: 0.2
- **pnl_basis**: Net P&L after fixed brokerage/charges and fixed slippage

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
- **capital**: 100000.0
- **risk_per_trade_pct**: 1.0
- **max_allocation_pct**: 100.0
- **min_first_candle_volume**: 0.0
- **min_average_volume**: 0.0
- **max_gap_pct**: 0.0
- **brokerage_entry_fee**: 20.0
- **brokerage_exit_fee**: 20.0
- **other_charges**: 10.0
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
