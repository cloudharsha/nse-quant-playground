# Open = Low / Open = High Position Sizing Backtest

## Method Comparison

| Method | Trades | Win Rate % | Net P&L | Ending Equity | Max DD % | Profit Factor | Sharpe |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fixed_fractional | 121 | 30.58 | -552910.54 | 447089.46 | -56.2839 | 0.2142 | -21.2086 |
| volatility_adjusted | 123 | 31.71 | -546665.3 | 453334.7 | -55.6737 | 0.2167 | -20.9588 |
| fractional_kelly | 32 | 18.75 | -195585.87 | 804414.13 | -19.8593 | 0.2271 | -14.8388 |

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

## Position Sizing Logic

- `fixed_fractional`: quantity is capped by live-equity risk per trade, per-trade notional, portfolio stop-risk, and gross exposure.
- `volatility_adjusted`: same as fixed fractional, with an extra ATR exposure cap.
- `fractional_kelly`: starts fixed fractional, then uses capped fractional Kelly after the warmup sample closes.

## Sizing Skips

### fixed_fractional
- **gross_exposure_too_small**: 17

### volatility_adjusted
- **gross_exposure_too_small**: 15

### fractional_kelly
- **gross_exposure_too_small**: 5
- **no_positive_kelly_edge**: 101

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
