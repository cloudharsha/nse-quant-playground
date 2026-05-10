# BTC Strategy Final Summary

## Scope

I reviewed the `summary.md` files under `btc/results` and treated the long `*_smoke_full` runs as decision-grade results.

The short `*_tmp` and `parity_*` runs are useful only as sanity checks because they cover roughly `2025-05-15` to `2025-05-21`, which is too small a sample to rank strategies reliably.

## Executive Conclusion

The clear winner is the **continuous MA strategy**. The **target + trailing-stop variants should not be used** in their current form.

If you want the best raw backtest result, pick:

- `btc_ma_continuous_multi_timeframe_capital_smoke_full/15m_ma96`

If you want the best balance to take forward for realistic testing, pick:

- `btc_ma_continuous_multi_timeframe_capital_smoke_full/30m_ma48`

## Why

### 1. Continuous MA is the only family with strong expectancy

| Strategy | Timeframe | Return % | Max DD % | Trades | Avg PnL / Trade USD | Notes |
|---|---|---:|---:|---:|---:|---|
| Continuous MA | 15m MA96 | 193.01 | 29.04 | 19396 | 99.51 | Best raw result |
| Continuous MA | 30m MA48 | 159.18 | 28.56 | 13829 | 115.11 | Best overall balance |
| Continuous MA | 1h MA24 | 118.02 | 40.12 | 9873 | 119.54 | Profitable, but weaker risk profile |
| Target + trailing 2R | 15m/30m/1h | -175.74 to -223.77 | 183.64 to 227.85 | 10706 to 24147 | negative | Reject |
| Multi-reward target + trailing | Best case: 15m 5R | 30.25 | 46.66 | 21586 | 14.01 | Too fragile |

The continuous strategy is profitable on all three full-sample timeframes.

The target-based variants raise win rate, but they cap the upside of trend trades and turn the edge negative. This is visible in the full runs:

- 2R target + trailing loses heavily on all timeframes.
- 3R and 4R multi-reward variants are also negative everywhere.
- 5R only rescues `15m` and barely `30m`, but with much worse drawdown and almost no per-trade edge.

## Best Approach

### Best raw backtest

`15m MA96 continuous` is the top in-sample result:

- Ending equity: `$2,930,133.92`
- Total return: `193.01%`
- Max drawdown: `29.04%`
- Positive years: `5 / 6`
- Positive months: `39 / 61`

If you are ranking strictly by the current no-cost backtest, this is the winner.

### Best practical candidate

`30m MA48 continuous` is the better strategy to advance first:

- Ending equity: `$2,591,841.06`
- Total return: `159.18%`
- Max drawdown: `28.56%`
- Positive years: `5 / 6`
- Positive months: `36 / 61`
- Trades are lower than 15m: `13,829` vs `19,396`
- Avg PnL per trade is higher: `$115.11` vs `$99.51`
- The only losing year is smaller: `2022 = -$20,015.71` vs `15m = -$51,444.73`

So the 30m version gives up some upside, but keeps almost the same drawdown while trading less and carrying better per-trade economics.

## Important Caveat

These backtests explicitly model:

- no brokerage
- no slippage
- no borrow/funding cost
- no compounding position sizing

That matters a lot because the edge per trade is not large.

Approximate break-even cost tolerance for the profitable continuous variants:

- `15m`: about `0.498 bps` per side (`0.995 bps` round trip)
- `30m`: about `0.576 bps` per side (`1.151 bps` round trip)
- `1h`: about `0.598 bps` per side (`1.195 bps` round trip)

This is the main reason I prefer `30m MA48 continuous` as the next strategy to validate. It is still strong, but slightly less exposed to execution friction than `15m`.

The profitable `5R` target-based variants are much worse on this test:

- `15m 5R`: only about `0.070 bps` per side
- `30m 5R`: only about `0.024 bps` per side

That is too thin to trust.

## Final Recommendation

Use this ranking:

1. `30m MA48 continuous` as the **best approach to carry forward**
2. `15m MA96 continuous` as the **best raw benchmark / aggressive variant**
3. `1h MA24 continuous` as a secondary fallback only
4. Reject all current `target + trailing` variants

## Next Step

Before treating any result as production-worthy, rerun at least the `15m` and `30m` continuous strategies with realistic:

- entry/exit trading costs
- slippage
- funding/borrow assumptions if relevant

If the strategy still survives after costs, the `30m MA48 continuous` setup is the best place to start.
