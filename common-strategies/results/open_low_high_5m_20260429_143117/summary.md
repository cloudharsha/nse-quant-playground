# Open = Low / Open = High Strategy Backtest

## Summary

- **strategy**: Open = Low / Open = High Strategy (5-min timeframe)
- **starting_capital**: 100000.0
- **ending_equity**: 96509.67
- **net_pnl**: -3490.33
- **total_trades**: 138
- **wins**: 59
- **losses**: 79
- **win_rate_pct**: 42.75
- **average_profit_loss**: -25.29
- **average_win**: 630.37
- **average_loss**: -514.96
- **max_drawdown**: -11360.08
- **max_drawdown_pct**: -11.0529
- **profit_factor**: 0.9142
- **sharpe_ratio**: -1.1159
- **markets_tested**: commodities,derivatives,equity
- **files_tested**: 20
- **sessions_tested**: 405
- **candles_tested**: 48989

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
- **brokerage_bps**: 3.0
- **slippage_bps**: 2.0
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
