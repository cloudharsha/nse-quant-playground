# Smart Money Concepts [LuxAlgo] Inspired 5m Backtest

## Variant Comparison

| Variant | Events | Trades | Win Rate % | Net P&L | Costs | Max DD % | Profit Factor | Sharpe |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| internal_all | 1334 | 830 | 32.65 | -136555.64 | 41500.0 | -145.6998 | 0.5006 | 2.4956 |
| swing_all | 182 | 167 | 34.73 | -26259.24 | 8350.0 | -28.8446 | 0.4434 | -8.0272 |
| combined_all | 1516 | 846 | 32.62 | -139259.95 | 42300.0 | -147.4027 | 0.4954 | 0.7828 |

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
- **brokerage_entry_fee**: 20.0
- **brokerage_exit_fee**: 20.0
- **other_charges**: 10.0
- **fixed_cost_per_trade**: 50.0
- **equity_slippage**: 0.2
- **derivatives_slippage**: 5.0
- **commodities_slippage**: 0.2
- **pnl_basis**: Net P&L after fixed brokerage/charges and fixed slippage

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
- **invalid_or_unsized_entry**: 3
- **signal_without_next_session_bar**: 4

### swing_all
- **invalid_or_unsized_entry**: 5
- **signal_without_next_session_bar**: 2

### combined_all
- **invalid_or_unsized_entry**: 4
- **signal_without_next_session_bar**: 5

## Parameters

- **internal_length**: 5
- **swing_length**: 50
- **atr_period**: 14
- **order_block_atr_period**: 200
- **atr_multiplier**: 1.5
- **stop_buffer_pct**: 0.02
- **risk_reward**: 2.0
- **capital**: 100000.0
- **risk_per_trade_pct**: 1.0
- **max_allocation_pct**: 100.0
- **brokerage_entry_fee**: 20.0
- **brokerage_exit_fee**: 20.0
- **other_charges**: 10.0
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
