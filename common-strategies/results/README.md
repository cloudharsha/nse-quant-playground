# Common Strategy Results

Each timestamped folder in this directory is one backtest run. The folder should
contain a `summary.md` file first, then detailed CSV/JSON files for deeper
analysis.

## Summary Template

Every `summary.md` should include:

- **Strategy name**: the strategy and variant tested.
- **Testing scope**: markets tested (`commodities`, `derivatives`, `equity`),
  timeframe, number of files, sessions, candles, and trades where available.
- **Cost model**: whether fixed brokerage/charges and fixed slippage were
  included, with the exact rupee values used.
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

Brokerage and other charges are fixed per completed trade unless explicitly set
to zero. Do not change these defaults unless the brokerage model itself changes:

- `brokerage_entry_fee`: `20.0`
- `brokerage_exit_fee`: `20.0`
- `other_charges`: `10.0`
- `fixed_cost_per_trade`: `50.0`

Slippage is a fixed price-point adjustment, not a percentage:

- `equity_slippage`: `0.2`
- `derivatives_slippage`: `5.0`
- `commodities_slippage`: `0.2`

For example, a BUY entry in equity adds `0.2` to the raw entry price, while a
SELL exit in derivatives adds `5.0` points to the raw exit price.

For each closed trade, the scripts calculate:

- entry slippage
- exit slippage
- fixed brokerage/charges
- gross P&L before costs
- net P&L after costs

The headline P&L, equity curve, drawdown, profit factor, and Sharpe ratio are
based on **net P&L after fixed brokerage/charges and fixed slippage**.
