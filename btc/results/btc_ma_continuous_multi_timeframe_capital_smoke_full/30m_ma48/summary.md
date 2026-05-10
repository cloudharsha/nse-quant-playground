# BTC 30m MA48 Fixed-Notional Capital Backtest

## Strategy Details

- Dataset: `btc/data/BTCUSD_data_30m.csv`
- Tested UTC date range: `2021-05-12` through `2026-05-10`
- Signal source: BTC-USD 30m close
- Initial activation: `2021-05-12 07:30:00+00:00` (one-time UTC activation threshold)
- No routine day-end exit; positions carry continuously until stopped, forced flat on a data gap, or exited at end of data.
- MA rule: 48-SMA of 30m closes computed fresh from the BTC dataset
- Direction rule: close above SMA -> long; close below SMA -> short; equal -> no entry
- Stop rule: long exits when candle low touches the trailing SMA; short exits when candle high touches the trailing SMA
- Re-entry rule: after a stop, the same completed candle may immediately open a new trade if the signal remains valid.
- Gap rule: force flat at the last known boundary before a gap, then resume on the first post-gap candle and allow a new entry only after that candle completes.
- Accounting: fixed `$1000000.00` notional per trade, no costs, no compounding position sizing, and points/USD metrics reported together.

## Data Notes

- First CSV row: `2021-05-12 07:30:00+00:00`
- First MA-usable row: `2021-05-13 07:00:00+00:00`
- Source rows loaded: `87505`
- Rows inside requested date filter: `87505`
- Rows processed after activation: `87505`
- Gap events detected in this run: `8`

## Overall Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Overall | 1825 | 146 | 1 | 0 | 13829 | 8 | 677 | 1001 | 75415.76 | 1591841.06 | 2591840.77 | 382260.70 | 27.2420 |

- Total trades: `13829`
- Win rate: `11.3096%`
- Starting capital: `$1000000.00`
- Ending equity: `$2591841.06`
- Gross PnL USD: `$1591841.06`
- Total return: `159.1841%`
- Max drawdown: `$406032.31` (`28.5617%`)

## Yearly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 234 | 19 | 1 | 0 | 1685 | 1 | 89 | 125 | 6291.11 | 237838.84 | 1237838.84 | 229139.85 | 18.7237 |
| 2022 | 365 | 31 | 0 | 0 | 2997 | 0 | 136 | 198 | 590.31 | -20015.71 | 1217823.05 | 258612.28 | 18.6161 |
| 2023 | 365 | 25 | 0 | 0 | 2880 | 2 | 130 | 210 | 11599.70 | 543659.88 | 1761483.02 | 213658.38 | 11.6499 |
| 2024 | 366 | 25 | 0 | 0 | 2714 | 3 | 140 | 201 | 25798.15 | 488229.57 | 2249712.53 | 149952.82 | 7.6013 |
| 2025 | 365 | 30 | 0 | 0 | 2658 | 1 | 137 | 198 | 13673.11 | 119253.09 | 2368965.33 | 306163.18 | 12.8149 |
| 2026 | 130 | 16 | 0 | 0 | 895 | 1 | 45 | 69 | 17463.38 | 222875.39 | 2591840.77 | 184256.69 | 7.2265 |

## Monthly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021-05 | 20 | 1 | 1 | 0 | 107 | 0 | 7 | 11 | -2713.44 | -79839.22 | 920160.79 | 178443.38 | 16.6042 |
| 2021-06 | 30 | 1 | 0 | 0 | 207 | 0 | 11 | 18 | 5163.29 | 145617.46 | 1065778.16 | 82459.73 | 8.6262 |
| 2021-07 | 31 | 1 | 0 | 0 | 216 | 0 | 15 | 15 | 4773.07 | 158656.99 | 1224435.20 | 76607.93 | 5.9913 |
| 2021-08 | 31 | 3 | 0 | 0 | 177 | 0 | 13 | 15 | 5250.88 | 135065.81 | 1359500.96 | 43705.03 | 3.1147 |
| 2021-09 | 30 | 3 | 0 | 0 | 252 | 0 | 10 | 17 | -3197.09 | -82891.38 | 1276609.59 | 123276.57 | 8.8923 |
| 2021-10 | 31 | 3 | 0 | 0 | 264 | 0 | 10 | 18 | -2325.21 | -9420.16 | 1267189.44 | 166573.03 | 11.9131 |
| 2021-11 | 30 | 4 | 0 | 0 | 207 | 1 | 9 | 17 | 1621.59 | 28698.67 | 1295888.16 | 93123.31 | 7.3488 |
| 2021-12 | 31 | 3 | 0 | 0 | 255 | 0 | 14 | 14 | -2281.98 | -58049.33 | 1237838.84 | 168159.23 | 12.5144 |
| 2022-01 | 31 | 2 | 0 | 0 | 275 | 0 | 10 | 19 | -6468.05 | -156052.68 | 1081786.15 | 216893.55 | 17.5220 |
| 2022-02 | 28 | 3 | 0 | 0 | 252 | 0 | 11 | 14 | 827.41 | 43321.27 | 1125107.38 | 169871.72 | 13.6404 |
| 2022-03 | 31 | 3 | 0 | 0 | 315 | 0 | 10 | 18 | -859.61 | -12006.18 | 1113101.21 | 166972.08 | 13.0439 |
| 2022-04 | 30 | 4 | 0 | 0 | 205 | 0 | 13 | 13 | 3498.09 | 74017.25 | 1187118.51 | 65618.72 | 5.5909 |
| 2022-05 | 31 | 4 | 0 | 0 | 247 | 0 | 14 | 13 | -7.15 | -39881.99 | 1147236.56 | 212131.53 | 16.4714 |
| 2022-06 | 30 | 3 | 0 | 0 | 181 | 0 | 11 | 16 | 4448.43 | 140915.84 | 1288152.44 | 121992.08 | 8.7815 |
| 2022-07 | 31 | 1 | 0 | 0 | 218 | 0 | 14 | 16 | -922.63 | -43323.24 | 1244829.20 | 132206.53 | 10.2633 |
| 2022-08 | 31 | 2 | 0 | 0 | 248 | 0 | 9 | 20 | -15.32 | -11535.49 | 1233293.72 | 89686.94 | 6.8284 |
| 2022-09 | 30 | 2 | 0 | 0 | 233 | 0 | 8 | 20 | -833.60 | -41548.72 | 1191744.94 | 133099.27 | 10.1106 |
| 2022-10 | 31 | 3 | 0 | 0 | 251 | 0 | 13 | 15 | 366.42 | 19232.59 | 1210977.48 | 69564.76 | 5.7964 |
| 2022-11 | 30 | 2 | 0 | 0 | 262 | 0 | 11 | 17 | 607.96 | 12402.18 | 1223379.58 | 165081.39 | 12.2128 |
| 2022-12 | 31 | 2 | 0 | 0 | 310 | 0 | 12 | 17 | -51.64 | -5556.54 | 1217823.05 | 77531.34 | 5.9853 |
| 2023-01 | 31 | 3 | 0 | 0 | 245 | 0 | 11 | 17 | 2233.21 | 142507.10 | 1360330.14 | 102650.02 | 7.1690 |
| 2023-02 | 28 | 3 | 0 | 0 | 174 | 0 | 11 | 14 | 2921.82 | 127755.64 | 1488085.77 | 42561.70 | 3.1288 |
| 2023-03 | 31 | 3 | 0 | 0 | 243 | 1 | 12 | 16 | 4109.75 | 206112.20 | 1694197.99 | 68302.29 | 4.0003 |
| 2023-04 | 30 | 1 | 0 | 0 | 238 | 0 | 10 | 19 | -1725.96 | -62991.12 | 1631206.91 | 143835.77 | 8.1032 |
| 2023-05 | 31 | 4 | 0 | 0 | 217 | 1 | 13 | 14 | 1417.77 | 49634.63 | 1680841.52 | 53371.15 | 3.2070 |
| 2023-06 | 30 | 1 | 0 | 0 | 257 | 0 | 10 | 19 | 1063.52 | 51269.64 | 1732111.17 | 69519.03 | 4.0452 |
| 2023-07 | 31 | 1 | 0 | 0 | 256 | 0 | 9 | 21 | -991.60 | -34567.57 | 1697543.56 | 53712.98 | 3.0717 |
| 2023-08 | 31 | 3 | 0 | 0 | 231 | 0 | 11 | 17 | 2700.10 | 89409.90 | 1786953.45 | 37367.85 | 2.0635 |
| 2023-09 | 30 | 1 | 0 | 0 | 306 | 0 | 6 | 23 | -2768.10 | -106526.66 | 1680426.81 | 161663.54 | 8.8148 |
| 2023-10 | 31 | 3 | 0 | 0 | 244 | 0 | 9 | 19 | 417.70 | 30317.67 | 1710744.48 | 68814.92 | 3.8670 |
| 2023-11 | 30 | 0 | 0 | 0 | 265 | 0 | 11 | 19 | -2779.88 | -76406.41 | 1634338.10 | 90410.66 | 5.2849 |
| 2023-12 | 31 | 2 | 0 | 0 | 204 | 0 | 17 | 12 | 5001.37 | 127144.86 | 1761483.02 | 29362.36 | 1.6616 |
| 2024-01 | 31 | 2 | 0 | 0 | 296 | 0 | 9 | 20 | -380.91 | -9567.28 | 1751915.81 | 85641.81 | 4.7096 |
| 2024-02 | 29 | 3 | 0 | 0 | 212 | 1 | 8 | 18 | 7882.67 | 161238.64 | 1913154.45 | 95393.74 | 5.2690 |
| 2024-03 | 31 | 2 | 0 | 0 | 213 | 0 | 11 | 18 | 1329.29 | 23404.51 | 1936558.93 | 67526.05 | 3.5114 |
| 2024-04 | 30 | 0 | 0 | 0 | 235 | 0 | 11 | 19 | -6789.70 | -111689.07 | 1824869.77 | 149952.82 | 7.6013 |
| 2024-05 | 31 | 1 | 0 | 0 | 206 | 1 | 17 | 13 | 11990.84 | 195399.06 | 2020268.83 | 35694.56 | 1.8402 |
| 2024-06 | 30 | 1 | 0 | 0 | 232 | 0 | 10 | 19 | -3039.88 | -43770.10 | 1976498.73 | 89226.38 | 4.4166 |
| 2024-07 | 31 | 6 | 0 | 0 | 186 | 0 | 13 | 12 | 7249.91 | 125882.37 | 2102381.08 | 61867.31 | 2.9065 |
| 2024-08 | 31 | 1 | 0 | 0 | 217 | 0 | 15 | 15 | 4261.33 | 64308.15 | 2166689.25 | 83599.97 | 3.8018 |
| 2024-09 | 30 | 3 | 0 | 0 | 209 | 0 | 12 | 15 | 406.68 | 10510.82 | 2177200.05 | 55030.45 | 2.4875 |
| 2024-10 | 31 | 3 | 0 | 0 | 221 | 1 | 12 | 16 | 3269.85 | 52812.06 | 2230012.13 | 45526.60 | 2.0625 |
| 2024-11 | 30 | 2 | 0 | 0 | 243 | 0 | 11 | 17 | 2842.02 | 57104.19 | 2287116.35 | 108926.60 | 4.6555 |
| 2024-12 | 31 | 1 | 0 | 0 | 244 | 0 | 11 | 19 | -3223.95 | -37403.78 | 2249712.53 | 71326.65 | 3.1133 |
| 2025-01 | 31 | 4 | 0 | 0 | 234 | 0 | 9 | 18 | -6672.54 | -57898.25 | 2191814.24 | 142359.12 | 6.0989 |
| 2025-02 | 28 | 3 | 0 | 0 | 188 | 0 | 9 | 16 | 5400.10 | 54310.82 | 2246125.00 | 93681.88 | 4.1332 |
| 2025-03 | 31 | 2 | 0 | 0 | 247 | 0 | 11 | 18 | -4577.27 | -54642.96 | 2191482.03 | 221769.38 | 9.2825 |
| 2025-04 | 30 | 1 | 0 | 0 | 242 | 0 | 11 | 18 | -5464.13 | -54404.49 | 2137077.60 | 109125.79 | 4.8582 |
| 2025-05 | 31 | 3 | 0 | 0 | 217 | 0 | 10 | 18 | 796.74 | 9977.33 | 2147054.86 | 105631.84 | 4.8265 |
| 2025-06 | 30 | 3 | 0 | 0 | 240 | 0 | 9 | 18 | -4776.21 | -43612.60 | 2103442.34 | 60864.36 | 2.8348 |
| 2025-07 | 31 | 1 | 0 | 0 | 231 | 0 | 13 | 17 | 1268.47 | 17591.67 | 2121033.98 | 107540.84 | 4.8255 |
| 2025-08 | 31 | 2 | 0 | 0 | 220 | 0 | 12 | 17 | 3224.31 | 25407.57 | 2146441.48 | 53906.72 | 2.4753 |
| 2025-09 | 30 | 2 | 0 | 0 | 204 | 0 | 12 | 16 | 2064.52 | 18140.28 | 2164581.74 | 49017.36 | 2.2837 |
| 2025-10 | 31 | 4 | 0 | 0 | 201 | 1 | 13 | 14 | 12845.57 | 111737.40 | 2276319.13 | 55308.25 | 2.4453 |
| 2025-11 | 30 | 2 | 0 | 0 | 246 | 0 | 10 | 18 | 2771.98 | 17874.89 | 2294193.96 | 83671.64 | 3.5410 |
| 2025-12 | 31 | 3 | 0 | 0 | 188 | 0 | 18 | 10 | 6791.57 | 74771.43 | 2368965.33 | 89671.44 | 3.6763 |
| 2026-01 | 31 | 4 | 0 | 0 | 229 | 0 | 10 | 17 | -2100.92 | -27615.14 | 2341350.17 | 78486.02 | 3.2803 |
| 2026-02 | 28 | 5 | 0 | 0 | 182 | 0 | 9 | 14 | 12139.52 | 147999.37 | 2489349.57 | 184256.69 | 7.2265 |
| 2026-03 | 31 | 5 | 0 | 0 | 212 | 0 | 12 | 14 | 7026.09 | 95066.92 | 2584416.54 | 57589.44 | 2.3068 |
| 2026-04 | 30 | 1 | 0 | 0 | 222 | 0 | 10 | 19 | -1983.81 | -23643.11 | 2560773.42 | 69909.92 | 2.6718 |
| 2026-05 | 10 | 1 | 0 | 0 | 50 | 1 | 4 | 5 | 2382.50 | 31067.35 | 2591840.77 | 15908.04 | 0.6113 |

## Gap Events / Exceptions

- `2021-11-23 23:30:00+00:00` -> `2021-11-24 01:00:00+00:00`: `2` missing candles; active trade = `YES`. Missing 2 candle(s) between 2021-11-23 23:30:00+00:00 and 2021-11-24 01:00:00+00:00; resumed on next available row.
- `2023-03-04 16:30:00+00:00` -> `2023-03-04 21:30:00+00:00`: `9` missing candles; active trade = `YES`. Missing 9 candle(s) between 2023-03-04 16:30:00+00:00 and 2023-03-04 21:30:00+00:00; resumed on next available row.
- `2023-05-19 07:00:00+00:00` -> `2023-05-19 08:30:00+00:00`: `2` missing candles; active trade = `YES`. Missing 2 candle(s) between 2023-05-19 07:00:00+00:00 and 2023-05-19 08:30:00+00:00; resumed on next available row.
- `2024-02-09 21:00:00+00:00` -> `2024-02-09 22:00:00+00:00`: `1` missing candles; active trade = `YES`. Missing 1 candle(s) between 2024-02-09 21:00:00+00:00 and 2024-02-09 22:00:00+00:00; resumed on next available row.
- `2024-05-31 21:30:00+00:00` -> `2024-05-31 23:30:00+00:00`: `3` missing candles; active trade = `YES`. Missing 3 candle(s) between 2024-05-31 21:30:00+00:00 and 2024-05-31 23:30:00+00:00; resumed on next available row.
- `2024-10-26 15:30:00+00:00` -> `2024-10-26 17:30:00+00:00`: `3` missing candles; active trade = `YES`. Missing 3 candle(s) between 2024-10-26 15:30:00+00:00 and 2024-10-26 17:30:00+00:00; resumed on next available row.
- `2025-10-25 14:30:00+00:00` -> `2025-10-25 21:00:00+00:00`: `12` missing candles; active trade = `YES`. Missing 12 candle(s) between 2025-10-25 14:30:00+00:00 and 2025-10-25 21:00:00+00:00; resumed on next available row.
- `2026-05-08 01:00:00+00:00` -> `2026-05-08 08:00:00+00:00`: `13` missing candles; active trade = `YES`. Missing 13 candle(s) between 2026-05-08 01:00:00+00:00 and 2026-05-08 08:00:00+00:00; resumed on next available row.

## Output Files

- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/30m_ma48/trades.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/30m_ma48/gap_events.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/30m_ma48/daywise_summary.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/30m_ma48/monthly_summary.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/30m_ma48/yearly_summary.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/30m_ma48/equity_curve.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/30m_ma48/summary.json`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/30m_ma48/summary.md`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/30m_ma48/backtest.log`

## Remarks

- The one-time activation threshold is applied only on the first candidate UTC date.
- Opposite signals are ignored while a position is live; only the trailing SMA stop or a gap flat can close the trade.
- The entry candle itself cannot stop a newly opened position.
- Daywise results are grouped by realized exit date in UTC; held-only dates are preserved separately.
- Monthly and yearly drawdowns are period-local from day-ending equity; overall drawdown is full-run.
