# Common Strategy Results

Each timestamped folder in this directory is one backtest run. The folder should
contain a `summary.md` file first, then detailed CSV/JSON files for deeper
analysis.

## Summary Template

Every `summary.md` should include:

- **Strategy name**: the strategy and variant tested.
- **Testing scope**: markets tested (`commodities`, `derivatives`, `equity`),
  timeframe, number of files, sessions, candles, and trades where available.
- **Cost model**: whether segment-wise brokerage/charges and fixed slippage were
  included, with the exact reference values used.
- **Backtest rules**: signal, entry, stop-loss, target, and exit assumptions.
- **Headline metrics**: trades, win rate, net P&L, ending equity, max drawdown,
  profit factor, and Sharpe ratio when possible.
- **Risk and sizing settings**: capital, risk per trade, allocation limits, and
  strategy-specific parameters.
- **Skip counts**: why any sessions or signals were ignored.
- **Output files**: generated trade logs, equity curves, date-wise P&L,
  market/instrument metrics, and best/worst trade reports.
- Total costs in INR value
- Total Profit/Loss 
- Total Trades Time Frame 
- Traded instruments and their time frame

## Cost Model

Brokerage and statutory charges are calculated from the segment-wise reference
values in `../../brokerage.md`. The default starting capital is:

- `capital`: `1000000.0`
- `cost_multiplier`: `1.0`

Reference calculator charges for Rs. 10,00,000 buy and Rs. 10,00,000 sell:

- `intraday_equity_reference_total_charges`: `402.01`
- `futures_reference_total_charges`: `612.75`
- `options_reference_total_charges`: `2418.07`
- `commodity_futures_reference_total_charges`: `17239.20`

Slippage is a fixed price-point adjustment, not a percentage:

- `equity_slippage`: `0.2`
- `derivatives_slippage`: `5.0`
- `commodities_slippage`: `0.2`

For example, a BUY entry in equity adds `0.2` to the raw entry price, while a
SELL exit in derivatives adds `5.0` points to the raw exit price.

For each closed trade, the scripts calculate:

- entry slippage
- exit slippage
- brokerage and statutory charges based on market segment
- gross P&L before costs
- net P&L after costs

The headline P&L, equity curve, drawdown, profit factor, and Sharpe ratio are
based on **net P&L after segment-wise brokerage/charges and fixed slippage**.
