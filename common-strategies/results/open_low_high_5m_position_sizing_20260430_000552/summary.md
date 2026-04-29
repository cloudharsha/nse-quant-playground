# Open = Low / Open = High Position Sizing Backtest

## Method Comparison

| Method | Trades | Win Rate % | Net P&L | Ending Equity | Max DD % | Profit Factor | Sharpe |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fixed_fractional | 121 | 35.54 | -21692.67 | 78307.33 | -25.1858 | 0.5468 | -7.1789 |
| volatility_adjusted | 119 | 36.13 | -21085.06 | 78914.94 | -24.6555 | 0.5549 | -6.9532 |
| fractional_kelly | 31 | 35.48 | -2812.9 | 97187.1 | -7.0861 | 0.7871 | -2.108 |

## Testing Scope

- **markets_tested**: commodities,derivatives,equity
- **timeframe**: 5-minute candles
- **files_tested**: 20
- **sessions_tested**: 405
- **candles_tested**: 48989
- **total_candidates**: 138

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

## Position Sizing Logic

- `fixed_fractional`: quantity is capped by live-equity risk per trade, per-trade notional, portfolio stop-risk, and gross exposure.
- `volatility_adjusted`: same as fixed fractional, with an extra ATR exposure cap.
- `fractional_kelly`: starts fixed fractional, then uses capped fractional Kelly after the warmup sample closes.

## Sizing Skips

### fixed_fractional
- **gross_exposure_too_small**: 17

### volatility_adjusted
- **gross_exposure_too_small**: 19

### fractional_kelly
- **gross_exposure_too_small**: 6
- **no_positive_kelly_edge**: 101

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
- **atr_period**: 14
- **volatility_risk_pct**: 0.5
- **kelly_warmup_trades**: 30
- **fractional_kelly_factor**: 0.25
- **kelly_max_risk_pct**: 2.0
- **max_portfolio_risk_pct**: 6.0
- **max_gross_exposure_pct**: 300.0
- **max_open_positions**: 6
- **position_sizing_methods**: ('fixed_fractional', 'volatility_adjusted', 'fractional_kelly')

## Output Files

- `trades_fixed_fractional.csv`
- `datewise_pnl_fixed_fractional.csv`
- `equity_curve_fixed_fractional.csv`
- `instrument_metrics_fixed_fractional.csv`
- `best_worst_trades_fixed_fractional.csv`
- `trades_volatility_adjusted.csv`
- `datewise_pnl_volatility_adjusted.csv`
- `equity_curve_volatility_adjusted.csv`
- `instrument_metrics_volatility_adjusted.csv`
- `best_worst_trades_volatility_adjusted.csv`
- `trades_fractional_kelly.csv`
- `datewise_pnl_fractional_kelly.csv`
- `equity_curve_fractional_kelly.csv`
- `instrument_metrics_fractional_kelly.csv`
- `best_worst_trades_fractional_kelly.csv`
- `method_comparison.csv`
- `summary.json`
- `run_config.json`
- `summary.md`
