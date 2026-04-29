# Common Strategy Results

Each timestamped folder in this directory is one backtest run. The folder should
contain a `summary.md` file first, then detailed CSV/JSON files for deeper
analysis.

## Summary Template

Every `summary.md` should include:

- **Strategy name**: the strategy and variant tested.
- **Testing scope**: markets tested (`commodities`, `derivatives`, `equity`),
  timeframe, number of files, sessions, candles, and trades where available.
- **Cost model**: whether brokerage and slippage were included, with the exact
  `brokerage_bps` and `slippage_bps` values.
- **Backtest rules**: signal, entry, stop-loss, target, and exit assumptions.
- **Headline metrics**: trades, win rate, net P&L, ending equity, max drawdown,
  profit factor, and Sharpe ratio when possible.
- **Risk and sizing settings**: capital, risk per trade, allocation limits, and
  strategy-specific parameters.
- **Skip counts**: why any sessions or signals were ignored.
- **Output files**: generated trade logs, equity curves, date-wise P&L,
  market/instrument metrics, and best/worst trade reports.
- Total brokerage in INR value 
- Total Profit/Loss 
- Total Trades Time Frame 
- Traded instructments and there time frame 

## Cost Model

Brokerage is calculated in the current strategy scripts unless explicitly set to
zero. The default is:

- `brokerage_bps`: `3.0`
- `slippage_bps`: `2.0`

`bps` means basis points. One basis point is `0.01%`.

For each closed trade, the scripts calculate:

- entry slippage
- exit slippage
- brokerage on total turnover
- gross P&L before costs
- net P&L after brokerage

The headline P&L, equity curve, drawdown, profit factor, and Sharpe ratio are
based on **net P&L after brokerage and slippage**.
