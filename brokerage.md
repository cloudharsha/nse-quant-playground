# Brokerage Reference

This document records the brokerage calculator values shown in the reference
images for flat trades:

- Buy value: Rs. 10,00,000
- Sell value: Rs. 10,00,000
- Quantity: 1

Because buy and sell values are equal, gross P&L is zero. Net P&L is therefore
negative by the total tax and charges.

## NSE Calculator Snapshot

| Segment | Turnover | Brokerage | STT Total | Exchange Txn Charge | GST | SEBI Charges | Stamp Duty | Total Tax and Charges | Points to Breakeven | Net P&L |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Intraday equity | 20,00,000 | 40.00 | 250.00 | 61.40 | 18.61 | 2.00 | 30.00 | 402.01 | 402.01 | -402.01 |
| Delivery equity | 20,00,000 | 0.00 | 2,000.00 | 61.40 | 11.41 | 2.00 | 150.00 | 2,224.81 | 2,224.81 | -2,224.81 |
| F&O - Futures | 20,00,000 | 40.00 | 500.00 | 36.60 | 14.15 | 2.00 | 20.00 | 612.75 | 612.75 | -612.75 |
| F&O - Options | 20,00,000 | 40.00 | 1,500.00 | 710.60 | 135.47 | 2.00 | 30.00 | 2,418.07 | 2,418.07 | -2,418.07 |

## MCX Commodity Futures Snapshot

This is the commodity futures calculator snapshot for GOLD on MCX. The input
buy and sell values are Rs. 10,00,000 each, and the calculator displays
turnover as Rs. 20,00,00,000.

| Segment | Commodity | Turnover | Brokerage | Exchange Charge | GST | CTT | SEBI Charges | Stamp Duty | Total Tax and Charges | Points to Breakeven | Net P&L |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Commodity futures | GOLD | 20,00,00,000 | 40.00 | 4,200.00 | 799.20 | 10,000.00 | 200.00 | 2,000.00 | 17,239.20 | 172.39 | -17,239.20 |

## Notes For Backtesting

- Brokerage in the calculator is Rs. 20 on buy and Rs. 20 on sell where
  brokerage applies, capped at Rs. 40 for the complete round trip.
- Delivery equity shows zero brokerage, but statutory charges are much higher
  because STT and stamp duty are higher.
- Total tax and charges include brokerage, STT, exchange transaction charge,
  GST, SEBI charges, and stamp duty.
- Commodity futures use CTT instead of STT and use the MCX exchange charge.
- Points to breakeven equals total tax and charges in this flat-trade example.
- Common-strategy scripts now use these segment-wise calculator values as the
  default cost model with Rs. 10,00,000 starting capital.
- For each backtest trade, costs are calculated from actual entry and exit
  notional using the rates implied by these snapshots, with brokerage capped at
  Rs. 20 per order where applicable.
