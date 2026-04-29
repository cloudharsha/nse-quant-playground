# Smart Money Concepts [LuxAlgo] Inspired 5m Backtest

## Variant Comparison

| Variant | Events | Trades | Win Rate % | Net P&L | Costs | Max DD % | Profit Factor | Sharpe |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| internal_all | 1334 | 1089 | 22.13 | -6205177.07 | 3993285.0 | -623.2282 | 0.1424 | -2.4766 |
| swing_all | 182 | 179 | 26.26 | -883770.04 | 553349.86 | -90.0544 | 0.2158 | -12.4306 |
| combined_all | 1516 | 1141 | 22.61 | -6448485.25 | 4156328.9 | -646.6234 | 0.147 | -2.3751 |

## Testing Scope

- **markets_tested**: commodities,derivatives,equity
- **timeframe**: 5-minute candles
- **files_tested**: 20
- **sessions_tested**: 385
- **candles_tested**: 27415
- **trade_start_date**: 2026-03-30
- **trade_end_date**: 2026-04-29
- **traded_instruments**: commodities:CLF:5m,commodities:GCF:5m,commodities:HGF:5m,commodities:NGF:5m,commodities:SIF:5m,derivatives:CNXAUTO:5m,derivatives:CNXFMCG:5m,derivatives:CNXIT:5m,derivatives:NSEBANK:5m,derivatives:NSEI:5m,equity:BHARTIARTL_NS:5m,equity:HDFCBANK_NS:5m,equity:ICICIBANK_NS:5m,equity:INFY_NS:5m,equity:ITC_NS:5m,equity:KOTAKBANK_NS:5m,equity:LT_NS:5m,equity:RELIANCE_NS:5m,equity:SBIN_NS:5m,equity:TCS_NS:5m

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

- Structure events are based on the LuxAlgo SMC BOS/CHoCH alert logic.
- Internal structure uses a 5-bar leg; swing structure uses a 50-bar leg.
- Entry happens at the next 5-minute candle open after a signal candle closes.
- Stop-loss uses the event order block when valid, otherwise ATR fallback.
- Target uses fixed risk/reward from the entry to stop distance.
- Trades exit on target, stop, opposite structure event, session end, or final bar.
- Same-candle target/stop ambiguity uses the configured ambiguous policy.

## Variant Meaning

- `internal_all`: internal BOS and internal CHoCH events.
- `internal_choch`: internal CHoCH events only.
- `swing_all`: swing BOS and swing CHoCH events.
- `swing_choch`: swing CHoCH events only.
- `combined_all`: internal and swing BOS/CHoCH events.

## Skip Counts

### internal_all
- **signal_without_next_session_bar**: 9

### swing_all
- **signal_without_next_session_bar**: 3

### combined_all
- **signal_without_next_session_bar**: 12

## Parameters

- **internal_length**: 5
- **swing_length**: 50
- **atr_period**: 14
- **order_block_atr_period**: 200
- **atr_multiplier**: 1.5
- **stop_buffer_pct**: 0.02
- **risk_reward**: 2.0
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
- **variants**: ('internal_all', 'swing_all', 'combined_all')
- **top_trade_count**: 10

## Output Files

- `trades_internal_all.csv`
- `datewise_pnl_internal_all.csv`
- `equity_curve_internal_all.csv`
- `market_metrics_internal_all.csv`
- `instrument_metrics_internal_all.csv`
- `best_worst_trades_internal_all.csv`
- `trades_swing_all.csv`
- `datewise_pnl_swing_all.csv`
- `equity_curve_swing_all.csv`
- `market_metrics_swing_all.csv`
- `instrument_metrics_swing_all.csv`
- `best_worst_trades_swing_all.csv`
- `trades_combined_all.csv`
- `datewise_pnl_combined_all.csv`
- `equity_curve_combined_all.csv`
- `market_metrics_combined_all.csv`
- `instrument_metrics_combined_all.csv`
- `best_worst_trades_combined_all.csv`
- `variant_comparison.csv`
- `summary.json`
- `run_config.json`
- `summary.md`
