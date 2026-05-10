# BTC 15m MA96 Fixed-Notional Capital Backtest

## Strategy Details

- Dataset: `btc/data/BTCUSD_data_15m.csv`
- Tested UTC date range: `2021-05-11` through `2026-05-10`
- Signal source: BTC-USD 15m close
- Initial activation: `2021-05-11 19:00:00+00:00` (one-time UTC activation threshold)
- No routine day-end exit; positions carry continuously until stopped, forced flat on a data gap, or exited at end of data.
- MA rule: 96-SMA of 15m closes computed fresh from the BTC dataset
- Direction rule: close above SMA -> long; close below SMA -> short; equal -> no entry
- Stop rule: long exits when candle low touches the trailing SMA; short exits when candle high touches the trailing SMA
- Re-entry rule: after a stop, the same completed candle may immediately open a new trade if the signal remains valid.
- Gap rule: force flat at the last known boundary before a gap, then resume on the first post-gap candle and allow a new entry only after that candle completes.
- Accounting: fixed `$1000000.00` notional per trade, no costs, no compounding position sizing, and points/USD metrics reported together.

## Data Notes

- First CSV row: `2021-05-11 19:00:00+00:00`
- First MA-usable row: `2021-05-12 18:45:00+00:00`
- Source rows loaded: `175072`
- Rows inside requested date filter: `175072`
- Rows processed after activation: `175072`
- Gap events detected in this run: `8`

## Overall Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Overall | 1826 | 151 | 1 | 0 | 19396 | 8 | 691 | 983 | 93403.52 | 1930133.92 | 2930134.31 | 475763.64 | 27.7398 |

- Total trades: `19396`
- Win rate: `9.7185%`
- Starting capital: `$1000000.00`
- Ending equity: `$2930133.92`
- Gross PnL USD: `$1930133.92`
- Total return: `193.0134%`
- Max drawdown: `$505031.52` (`29.0419%`)

## Yearly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 235 | 20 | 1 | 0 | 2327 | 1 | 88 | 126 | 16066.03 | 484457.58 | 1484457.54 | 260045.80 | 15.1622 |
| 2022 | 365 | 32 | 0 | 0 | 4244 | 0 | 137 | 196 | 105.44 | -51444.73 | 1433012.96 | 266673.73 | 16.5127 |
| 2023 | 365 | 27 | 0 | 0 | 4014 | 2 | 131 | 207 | 13029.12 | 581417.33 | 2014429.99 | 190080.39 | 9.3760 |
| 2024 | 366 | 26 | 0 | 0 | 3828 | 3 | 147 | 193 | 28087.05 | 552823.68 | 2567254.03 | 191693.06 | 9.2592 |
| 2025 | 365 | 29 | 0 | 0 | 3748 | 1 | 140 | 196 | 22446.96 | 197906.22 | 2765160.45 | 255727.04 | 9.4028 |
| 2026 | 130 | 17 | 0 | 0 | 1235 | 1 | 48 | 65 | 13668.92 | 164973.84 | 2930134.31 | 215921.00 | 7.2928 |

## Monthly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021-05 | 21 | 2 | 1 | 0 | 145 | 0 | 9 | 9 | 3921.14 | 61346.64 | 1061346.65 | 127012.70 | 11.3141 |
| 2021-06 | 30 | 1 | 0 | 0 | 282 | 0 | 11 | 18 | 7678.55 | 220764.05 | 1282110.69 | 77579.31 | 6.6070 |
| 2021-07 | 31 | 1 | 0 | 0 | 298 | 0 | 16 | 14 | 5365.51 | 174201.36 | 1456312.06 | 68698.50 | 4.5651 |
| 2021-08 | 31 | 3 | 0 | 0 | 243 | 0 | 12 | 16 | 6589.56 | 168371.40 | 1624683.43 | 50768.95 | 3.1991 |
| 2021-09 | 30 | 3 | 0 | 0 | 344 | 0 | 10 | 17 | -1856.87 | -51875.53 | 1572807.82 | 114216.47 | 6.9232 |
| 2021-10 | 31 | 3 | 0 | 0 | 361 | 0 | 11 | 17 | -1865.08 | 4092.09 | 1576899.98 | 140795.98 | 8.2092 |
| 2021-11 | 30 | 4 | 0 | 0 | 290 | 1 | 9 | 17 | 682.16 | 11648.48 | 1588548.47 | 94863.58 | 6.0158 |
| 2021-12 | 31 | 3 | 0 | 0 | 364 | 0 | 10 | 18 | -4448.94 | -104090.91 | 1484457.54 | 183104.27 | 11.1775 |
| 2022-01 | 31 | 2 | 0 | 0 | 391 | 0 | 9 | 20 | -6709.63 | -161782.06 | 1322675.40 | 245124.57 | 16.5127 |
| 2022-02 | 28 | 3 | 0 | 0 | 365 | 0 | 11 | 14 | 443.10 | 32785.65 | 1355461.08 | 172273.09 | 11.7418 |
| 2022-03 | 31 | 3 | 0 | 0 | 435 | 0 | 9 | 19 | 371.55 | 16860.28 | 1372321.33 | 159536.29 | 10.4390 |
| 2022-04 | 30 | 4 | 0 | 0 | 285 | 0 | 13 | 13 | 3032.89 | 63297.73 | 1435619.13 | 47604.48 | 3.3534 |
| 2022-05 | 31 | 4 | 0 | 0 | 359 | 0 | 15 | 12 | 627.36 | -17656.56 | 1417962.52 | 186435.38 | 12.1412 |
| 2022-06 | 30 | 3 | 0 | 0 | 248 | 0 | 13 | 14 | 4614.22 | 153773.30 | 1571735.77 | 89385.78 | 5.4705 |
| 2022-07 | 31 | 2 | 0 | 0 | 299 | 0 | 11 | 18 | -1277.22 | -54098.93 | 1517636.88 | 137022.96 | 8.7179 |
| 2022-08 | 31 | 2 | 0 | 0 | 354 | 0 | 12 | 17 | -52.61 | -14893.62 | 1502743.29 | 108088.73 | 6.7712 |
| 2022-09 | 30 | 2 | 0 | 0 | 336 | 0 | 10 | 18 | -506.08 | -27117.88 | 1475625.50 | 120085.64 | 7.5624 |
| 2022-10 | 31 | 3 | 0 | 0 | 358 | 0 | 12 | 16 | -396.18 | -19081.17 | 1456544.33 | 93493.69 | 6.2989 |
| 2022-11 | 30 | 2 | 0 | 0 | 365 | 0 | 12 | 16 | 493.21 | 10130.05 | 1466674.39 | 131923.41 | 8.3946 |
| 2022-12 | 31 | 2 | 0 | 0 | 449 | 0 | 10 | 19 | -535.17 | -33661.52 | 1433012.96 | 94442.83 | 6.1830 |
| 2023-01 | 31 | 3 | 0 | 0 | 342 | 0 | 11 | 17 | 2038.73 | 132267.07 | 1565279.93 | 98107.11 | 6.0114 |
| 2023-02 | 28 | 3 | 0 | 0 | 237 | 0 | 11 | 14 | 3459.46 | 156355.01 | 1721635.04 | 36829.98 | 2.3529 |
| 2023-03 | 31 | 3 | 0 | 0 | 373 | 1 | 10 | 18 | 1514.31 | 103112.11 | 1824747.14 | 99218.55 | 5.3219 |
| 2023-04 | 30 | 1 | 0 | 0 | 331 | 0 | 10 | 19 | -567.21 | -22750.88 | 1801996.15 | 132362.63 | 6.8427 |
| 2023-05 | 31 | 5 | 0 | 0 | 287 | 1 | 14 | 12 | 1396.90 | 49221.58 | 1851217.72 | 58826.03 | 3.2148 |
| 2023-06 | 30 | 2 | 0 | 0 | 357 | 0 | 11 | 17 | 1583.03 | 70428.02 | 1921645.68 | 66705.86 | 3.5063 |
| 2023-07 | 31 | 1 | 0 | 0 | 376 | 0 | 8 | 22 | -1485.35 | -50948.61 | 1870697.03 | 58542.12 | 3.0345 |
| 2023-08 | 31 | 3 | 0 | 0 | 322 | 0 | 11 | 17 | 3237.38 | 111680.36 | 1982377.31 | 36423.54 | 1.8444 |
| 2023-09 | 30 | 1 | 0 | 0 | 417 | 0 | 8 | 21 | -2317.90 | -89383.91 | 1892993.40 | 142690.79 | 7.0385 |
| 2023-10 | 31 | 3 | 0 | 0 | 335 | 0 | 11 | 17 | 899.87 | 45906.58 | 1938899.94 | 65137.69 | 3.2503 |
| 2023-11 | 30 | 0 | 0 | 0 | 371 | 0 | 10 | 20 | -2788.47 | -76984.66 | 1861915.30 | 101680.34 | 5.2442 |
| 2023-12 | 31 | 2 | 0 | 0 | 266 | 0 | 16 | 13 | 6058.37 | 152514.66 | 2014429.99 | 26799.97 | 1.3556 |
| 2024-01 | 31 | 2 | 0 | 0 | 420 | 0 | 10 | 19 | -3450.75 | -77028.91 | 1937401.14 | 160746.39 | 7.7644 |
| 2024-02 | 29 | 3 | 0 | 0 | 295 | 1 | 7 | 19 | 8797.31 | 182328.48 | 2119729.65 | 80052.88 | 3.9977 |
| 2024-03 | 31 | 2 | 0 | 0 | 304 | 0 | 11 | 18 | -202.15 | 1137.49 | 2120867.20 | 100181.00 | 4.7028 |
| 2024-04 | 30 | 0 | 0 | 0 | 329 | 0 | 15 | 15 | -2203.20 | -41019.03 | 2079848.17 | 76320.60 | 3.5426 |
| 2024-05 | 31 | 2 | 0 | 0 | 287 | 1 | 17 | 12 | 12459.18 | 203577.07 | 2283425.34 | 39708.95 | 1.8030 |
| 2024-06 | 30 | 1 | 0 | 0 | 347 | 0 | 10 | 19 | -3719.22 | -54785.93 | 2228639.43 | 90352.51 | 3.9569 |
| 2024-07 | 31 | 6 | 0 | 0 | 259 | 0 | 11 | 14 | 7270.87 | 127644.38 | 2356283.83 | 79364.85 | 3.3109 |
| 2024-08 | 31 | 1 | 0 | 0 | 292 | 0 | 14 | 16 | 6513.78 | 100939.66 | 2457223.51 | 60425.81 | 2.4523 |
| 2024-09 | 30 | 3 | 0 | 0 | 290 | 0 | 14 | 13 | 1502.22 | 30978.76 | 2488202.33 | 62404.70 | 2.4626 |
| 2024-10 | 31 | 3 | 0 | 0 | 299 | 1 | 15 | 13 | 6981.78 | 111313.47 | 2599515.88 | 20762.35 | 0.8240 |
| 2024-11 | 30 | 2 | 0 | 0 | 357 | 0 | 13 | 15 | 1726.06 | 50065.65 | 2649581.49 | 131812.16 | 4.8124 |
| 2024-12 | 31 | 1 | 0 | 0 | 349 | 0 | 10 | 20 | -7588.83 | -82327.41 | 2567254.03 | 83788.02 | 3.1606 |
| 2025-01 | 31 | 4 | 0 | 0 | 326 | 0 | 10 | 17 | -5120.74 | -45509.30 | 2521744.75 | 142733.64 | 5.3829 |
| 2025-02 | 28 | 3 | 0 | 0 | 274 | 0 | 9 | 16 | 1545.27 | 11904.63 | 2533649.40 | 115738.77 | 4.4610 |
| 2025-03 | 31 | 2 | 0 | 0 | 345 | 0 | 13 | 16 | 4479.57 | 46975.66 | 2580625.12 | 162965.62 | 5.9921 |
| 2025-04 | 30 | 1 | 0 | 0 | 340 | 0 | 12 | 17 | -5838.97 | -59250.09 | 2521374.98 | 101249.37 | 3.8606 |
| 2025-05 | 31 | 3 | 0 | 0 | 310 | 0 | 10 | 18 | 44.58 | 3217.25 | 2524592.29 | 111835.39 | 4.3418 |
| 2025-06 | 30 | 3 | 0 | 0 | 332 | 0 | 10 | 17 | -1684.95 | -13414.66 | 2511177.54 | 53132.47 | 2.0926 |
| 2025-07 | 31 | 1 | 0 | 0 | 306 | 0 | 13 | 17 | 3531.07 | 36566.24 | 2547743.79 | 96579.11 | 3.6523 |
| 2025-08 | 31 | 2 | 0 | 0 | 321 | 0 | 13 | 16 | 4851.70 | 39218.22 | 2586962.08 | 38128.75 | 1.4633 |
| 2025-09 | 30 | 2 | 0 | 0 | 299 | 0 | 12 | 16 | 2648.18 | 23661.17 | 2610623.31 | 38846.77 | 1.5016 |
| 2025-10 | 31 | 4 | 0 | 0 | 278 | 1 | 13 | 14 | 12888.05 | 112806.41 | 2723429.75 | 56999.25 | 2.1123 |
| 2025-11 | 30 | 2 | 0 | 0 | 350 | 0 | 10 | 18 | 921.71 | -5583.83 | 2717845.96 | 98295.30 | 3.5008 |
| 2025-12 | 31 | 2 | 0 | 0 | 267 | 0 | 15 | 14 | 4181.49 | 47314.52 | 2765160.45 | 76881.49 | 2.7256 |
| 2026-01 | 31 | 4 | 0 | 0 | 305 | 0 | 10 | 17 | -1375.80 | -18320.20 | 2746840.27 | 78239.90 | 2.8004 |
| 2026-02 | 28 | 5 | 0 | 0 | 258 | 0 | 9 | 14 | 9940.44 | 115289.68 | 2862130.01 | 215921.00 | 7.2928 |
| 2026-03 | 31 | 5 | 0 | 0 | 303 | 0 | 12 | 14 | 2385.45 | 28694.39 | 2890824.41 | 72032.99 | 2.5120 |
| 2026-04 | 30 | 2 | 0 | 0 | 300 | 0 | 12 | 16 | 365.14 | 8444.51 | 2899268.87 | 50168.14 | 1.7075 |
| 2026-05 | 10 | 1 | 0 | 0 | 69 | 1 | 5 | 4 | 2353.69 | 30865.46 | 2930134.31 | 21967.10 | 0.7465 |

## Gap Events / Exceptions

- `2021-11-24 00:00:00+00:00` -> `2021-11-24 00:45:00+00:00`: `2` missing candles; active trade = `YES`. Missing 2 candle(s) between 2021-11-24 00:00:00+00:00 and 2021-11-24 00:45:00+00:00; resumed on next available row.
- `2023-03-04 16:45:00+00:00` -> `2023-03-04 21:30:00+00:00`: `18` missing candles; active trade = `YES`. Missing 18 candle(s) between 2023-03-04 16:45:00+00:00 and 2023-03-04 21:30:00+00:00; resumed on next available row.
- `2023-05-19 07:30:00+00:00` -> `2023-05-19 08:15:00+00:00`: `2` missing candles; active trade = `YES`. Missing 2 candle(s) between 2023-05-19 07:30:00+00:00 and 2023-05-19 08:15:00+00:00; resumed on next available row.
- `2024-02-09 21:30:00+00:00` -> `2024-02-09 22:00:00+00:00`: `1` missing candles; active trade = `YES`. Missing 1 candle(s) between 2024-02-09 21:30:00+00:00 and 2024-02-09 22:00:00+00:00; resumed on next available row.
- `2024-05-31 22:00:00+00:00` -> `2024-05-31 23:15:00+00:00`: `4` missing candles; active trade = `YES`. Missing 4 candle(s) between 2024-05-31 22:00:00+00:00 and 2024-05-31 23:15:00+00:00; resumed on next available row.
- `2024-10-26 16:00:00+00:00` -> `2024-10-26 17:15:00+00:00`: `4` missing candles; active trade = `YES`. Missing 4 candle(s) between 2024-10-26 16:00:00+00:00 and 2024-10-26 17:15:00+00:00; resumed on next available row.
- `2025-10-25 15:00:00+00:00` -> `2025-10-25 21:00:00+00:00`: `23` missing candles; active trade = `YES`. Missing 23 candle(s) between 2025-10-25 15:00:00+00:00 and 2025-10-25 21:00:00+00:00; resumed on next available row.
- `2026-05-08 01:15:00+00:00` -> `2026-05-08 07:45:00+00:00`: `25` missing candles; active trade = `YES`. Missing 25 candle(s) between 2026-05-08 01:15:00+00:00 and 2026-05-08 07:45:00+00:00; resumed on next available row.

## Output Files

- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/15m_ma96/trades.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/15m_ma96/gap_events.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/15m_ma96/daywise_summary.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/15m_ma96/monthly_summary.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/15m_ma96/yearly_summary.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/15m_ma96/equity_curve.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/15m_ma96/summary.json`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/15m_ma96/summary.md`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/15m_ma96/backtest.log`

## Remarks

- The one-time activation threshold is applied only on the first candidate UTC date.
- Opposite signals are ignored while a position is live; only the trailing SMA stop or a gap flat can close the trade.
- The entry candle itself cannot stop a newly opened position.
- Daywise results are grouped by realized exit date in UTC; held-only dates are preserved separately.
- Monthly and yearly drawdowns are period-local from day-ending equity; overall drawdown is full-run.
