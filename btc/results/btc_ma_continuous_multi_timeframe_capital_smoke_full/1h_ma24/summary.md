# BTC 1h MA24 Fixed-Notional Capital Backtest

## Strategy Details

- Dataset: `btc/data/BTCUSD_data_1h.csv`
- Tested UTC date range: `2021-05-13` through `2026-05-10`
- Signal source: BTC-USD 1h close
- Initial activation: `2021-05-13 08:00:00+00:00` (one-time UTC activation threshold)
- No routine day-end exit; positions carry continuously until stopped, forced flat on a data gap, or exited at end of data.
- MA rule: 24-SMA of 1h closes computed fresh from the BTC dataset
- Direction rule: close above SMA -> long; close below SMA -> short; equal -> no entry
- Stop rule: long exits when candle low touches the trailing SMA; short exits when candle high touches the trailing SMA
- Re-entry rule: after a stop, the same completed candle may immediately open a new trade if the signal remains valid.
- Gap rule: force flat at the last known boundary before a gap, then resume on the first post-gap candle and allow a new entry only after that candle completes.
- Accounting: fixed `$1000000.00` notional per trade, no costs, no compounding position sizing, and points/USD metrics reported together.

## Data Notes

- First CSV row: `2021-05-13 08:00:00+00:00`
- First MA-usable row: `2021-05-14 07:00:00+00:00`
- Source rows loaded: `43724`
- Rows inside requested date filter: `43724`
- Rows processed after activation: `43724`
- Gap events detected in this run: `8`

## Overall Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Overall | 1824 | 139 | 1 | 0 | 9873 | 8 | 661 | 1023 | 41223.66 | 1180180.94 | 2180180.93 | 498396.05 | 39.2020 |

- Total trades: `9873`
- Win rate: `12.9241%`
- Starting capital: `$1000000.00`
- Ending equity: `$2180180.94`
- Gross PnL USD: `$1180180.94`
- Total return: `118.0181%`
- Max drawdown: `$514131.32` (`40.1173%`)

## Yearly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 233 | 16 | 1 | 0 | 1219 | 1 | 80 | 136 | -5552.08 | -27113.03 | 972887.05 | 332861.47 | 26.1816 |
| 2022 | 365 | 29 | 0 | 0 | 2128 | 0 | 134 | 202 | 2216.17 | -3070.63 | 969816.59 | 259939.95 | 22.3206 |
| 2023 | 365 | 24 | 0 | 0 | 2039 | 2 | 134 | 207 | 15739.60 | 679160.04 | 1648976.54 | 164827.57 | 10.0744 |
| 2024 | 366 | 28 | 0 | 0 | 1939 | 3 | 135 | 203 | 12563.43 | 303805.71 | 1952782.18 | 176552.18 | 9.0513 |
| 2025 | 365 | 28 | 0 | 0 | 1917 | 1 | 127 | 210 | -6955.89 | -75749.32 | 1877032.81 | 299944.70 | 14.8432 |
| 2026 | 130 | 14 | 0 | 0 | 631 | 1 | 51 | 65 | 23212.43 | 303148.17 | 2180180.93 | 115943.66 | 5.5494 |

## Monthly Results

| Period | Days | Held | Flat | Skipped | Trades | Gaps | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021-05 | 19 | 0 | 1 | 0 | 82 | 0 | 6 | 12 | -4366.10 | -112885.94 | 887114.05 | 207617.99 | 20.2541 |
| 2021-06 | 30 | 1 | 0 | 0 | 152 | 0 | 11 | 18 | 2815.41 | 79665.48 | 966779.61 | 91600.36 | 8.8309 |
| 2021-07 | 31 | 0 | 0 | 0 | 157 | 0 | 14 | 17 | 4176.72 | 140889.32 | 1107668.96 | 76071.05 | 6.4903 |
| 2021-08 | 31 | 3 | 0 | 0 | 132 | 0 | 10 | 18 | 2897.15 | 87715.61 | 1195384.61 | 75969.81 | 5.9755 |
| 2021-09 | 30 | 3 | 0 | 0 | 180 | 0 | 9 | 18 | -5472.56 | -130837.58 | 1064547.01 | 171969.48 | 14.0733 |
| 2021-10 | 31 | 3 | 0 | 0 | 180 | 0 | 12 | 16 | -688.52 | 18970.60 | 1083517.61 | 119241.65 | 9.9418 |
| 2021-11 | 30 | 4 | 0 | 0 | 151 | 1 | 9 | 17 | 30.23 | 1529.07 | 1085046.67 | 85629.37 | 7.9029 |
| 2021-12 | 31 | 2 | 0 | 0 | 185 | 0 | 9 | 20 | -4944.41 | -112159.59 | 972887.05 | 191185.66 | 16.9239 |
| 2022-01 | 31 | 2 | 0 | 0 | 195 | 0 | 8 | 21 | -6483.44 | -160364.74 | 812522.38 | 199928.69 | 20.5500 |
| 2022-02 | 28 | 2 | 0 | 0 | 177 | 0 | 12 | 14 | 1381.08 | 53527.21 | 866049.57 | 144520.28 | 15.1076 |
| 2022-03 | 31 | 3 | 0 | 0 | 214 | 0 | 11 | 17 | 1480.67 | 42002.13 | 908051.66 | 124221.37 | 12.0338 |
| 2022-04 | 30 | 4 | 0 | 0 | 154 | 0 | 13 | 13 | 3809.88 | 80974.08 | 989025.78 | 55726.79 | 5.6410 |
| 2022-05 | 31 | 4 | 0 | 0 | 179 | 0 | 12 | 15 | -396.37 | -52247.47 | 936778.35 | 234877.17 | 21.2134 |
| 2022-06 | 30 | 3 | 0 | 0 | 138 | 0 | 14 | 13 | 3992.28 | 130859.44 | 1067637.82 | 119573.31 | 10.2676 |
| 2022-07 | 31 | 0 | 0 | 0 | 155 | 0 | 15 | 16 | 844.00 | 36742.01 | 1104379.78 | 96191.99 | 9.0098 |
| 2022-08 | 31 | 2 | 0 | 0 | 175 | 0 | 9 | 20 | -1210.76 | -64140.28 | 1040239.60 | 94226.44 | 8.3058 |
| 2022-09 | 30 | 2 | 0 | 0 | 175 | 0 | 9 | 19 | -1725.11 | -85667.43 | 954572.15 | 142110.91 | 12.9582 |
| 2022-10 | 31 | 3 | 0 | 0 | 174 | 0 | 12 | 16 | 218.23 | 13223.74 | 967795.93 | 51429.40 | 5.3626 |
| 2022-11 | 30 | 2 | 0 | 0 | 186 | 0 | 8 | 20 | 143.50 | -5818.89 | 961977.01 | 140092.53 | 13.0955 |
| 2022-12 | 31 | 2 | 0 | 0 | 206 | 0 | 11 | 18 | 162.21 | 7839.57 | 969816.59 | 71294.90 | 6.8480 |
| 2023-01 | 31 | 3 | 0 | 0 | 175 | 0 | 12 | 16 | 2663.24 | 162218.46 | 1132035.07 | 100586.86 | 8.4078 |
| 2023-02 | 28 | 2 | 0 | 0 | 125 | 0 | 13 | 13 | 2598.10 | 114272.07 | 1246307.11 | 44621.60 | 3.9417 |
| 2023-03 | 31 | 3 | 0 | 0 | 161 | 1 | 11 | 17 | 5827.63 | 273071.43 | 1519378.51 | 53573.85 | 4.2986 |
| 2023-04 | 30 | 1 | 0 | 0 | 173 | 0 | 10 | 19 | -1711.17 | -62556.56 | 1456821.87 | 117801.00 | 7.4812 |
| 2023-05 | 31 | 5 | 0 | 0 | 147 | 1 | 12 | 14 | 2334.25 | 82467.20 | 1539289.05 | 26858.29 | 1.7680 |
| 2023-06 | 30 | 1 | 0 | 0 | 179 | 0 | 12 | 17 | 869.80 | 41048.94 | 1580338.01 | 82397.72 | 5.1751 |
| 2023-07 | 31 | 1 | 0 | 0 | 191 | 0 | 8 | 22 | -1701.26 | -58228.67 | 1522109.37 | 64708.45 | 4.0779 |
| 2023-08 | 31 | 3 | 0 | 0 | 170 | 0 | 9 | 19 | 1795.66 | 56556.81 | 1578666.16 | 49116.86 | 3.0174 |
| 2023-09 | 30 | 1 | 0 | 0 | 213 | 0 | 9 | 20 | -2112.97 | -81449.98 | 1497216.15 | 140082.56 | 8.6193 |
| 2023-10 | 31 | 3 | 0 | 0 | 181 | 0 | 10 | 18 | 1291.22 | 57047.13 | 1554263.29 | 62667.69 | 3.8757 |
| 2023-11 | 30 | 0 | 0 | 0 | 181 | 0 | 10 | 20 | -1472.58 | -40702.56 | 1513560.76 | 82980.59 | 5.3389 |
| 2023-12 | 31 | 1 | 0 | 0 | 143 | 0 | 18 | 12 | 5357.68 | 135415.77 | 1648976.54 | 29650.06 | 1.7844 |
| 2024-01 | 31 | 2 | 0 | 0 | 207 | 0 | 8 | 21 | -2060.93 | -48092.22 | 1600884.30 | 107050.72 | 6.3012 |
| 2024-02 | 29 | 4 | 0 | 0 | 155 | 1 | 9 | 16 | 9186.64 | 190158.87 | 1791043.15 | 72993.19 | 4.3574 |
| 2024-03 | 31 | 2 | 0 | 0 | 147 | 0 | 13 | 16 | 6083.43 | 93626.60 | 1884669.74 | 39168.46 | 2.1811 |
| 2024-04 | 30 | 0 | 0 | 0 | 165 | 0 | 10 | 20 | -5992.29 | -97428.60 | 1787241.07 | 127169.06 | 6.6499 |
| 2024-05 | 31 | 2 | 0 | 0 | 149 | 1 | 13 | 16 | 6738.08 | 112884.58 | 1900125.65 | 47335.22 | 2.5378 |
| 2024-06 | 30 | 2 | 0 | 0 | 172 | 0 | 9 | 19 | -2546.45 | -35519.32 | 1864606.33 | 87096.08 | 4.5837 |
| 2024-07 | 31 | 6 | 0 | 0 | 137 | 0 | 13 | 12 | 5050.12 | 85891.62 | 1950498.02 | 69333.69 | 3.4976 |
| 2024-08 | 31 | 1 | 0 | 0 | 148 | 0 | 14 | 16 | 2219.24 | 31394.31 | 1981892.35 | 76301.02 | 3.7584 |
| 2024-09 | 30 | 3 | 0 | 0 | 149 | 0 | 11 | 16 | -76.95 | 1183.96 | 1983076.30 | 54814.35 | 2.7203 |
| 2024-10 | 31 | 4 | 0 | 0 | 156 | 1 | 13 | 14 | 2512.24 | 41068.02 | 2024144.37 | 42321.18 | 2.1034 |
| 2024-11 | 30 | 2 | 0 | 0 | 178 | 0 | 12 | 16 | -2370.00 | -4269.36 | 2019874.94 | 137640.69 | 6.5207 |
| 2024-12 | 31 | 0 | 0 | 0 | 176 | 0 | 10 | 21 | -6179.70 | -67092.75 | 1952782.18 | 85597.23 | 4.2377 |
| 2025-01 | 31 | 4 | 0 | 0 | 169 | 0 | 8 | 19 | -10195.72 | -94930.59 | 1857851.62 | 140079.87 | 7.0112 |
| 2025-02 | 28 | 3 | 0 | 0 | 141 | 0 | 9 | 16 | 2672.62 | 27202.96 | 1885054.56 | 105691.07 | 5.5098 |
| 2025-03 | 31 | 2 | 0 | 0 | 169 | 0 | 13 | 16 | -1055.38 | -14746.18 | 1870308.39 | 179696.93 | 8.8926 |
| 2025-04 | 30 | 1 | 0 | 0 | 170 | 0 | 9 | 20 | -570.20 | 2021.46 | 1872329.89 | 77244.07 | 3.9903 |
| 2025-05 | 31 | 4 | 0 | 0 | 158 | 0 | 9 | 18 | -6260.27 | -57243.36 | 1815086.51 | 142915.50 | 7.4634 |
| 2025-06 | 30 | 3 | 0 | 0 | 178 | 0 | 9 | 18 | -5553.59 | -50818.53 | 1764267.93 | 62434.08 | 3.4397 |
| 2025-07 | 31 | 1 | 0 | 0 | 166 | 0 | 12 | 18 | -456.85 | 1751.30 | 1766019.20 | 100601.94 | 5.3895 |
| 2025-08 | 31 | 2 | 0 | 0 | 160 | 0 | 8 | 21 | 4311.39 | 34356.86 | 1800376.07 | 47974.74 | 2.6242 |
| 2025-09 | 30 | 2 | 0 | 0 | 148 | 0 | 11 | 17 | -1648.67 | -15635.94 | 1784740.12 | 79570.54 | 4.4197 |
| 2025-10 | 31 | 3 | 0 | 0 | 145 | 1 | 15 | 13 | 11575.49 | 99595.30 | 1884335.40 | 44627.60 | 2.3740 |
| 2025-11 | 30 | 2 | 0 | 0 | 167 | 0 | 10 | 18 | -715.43 | -18113.76 | 1866221.69 | 84742.04 | 4.3816 |
| 2025-12 | 31 | 1 | 0 | 0 | 146 | 0 | 14 | 16 | 940.72 | 10811.16 | 1877032.81 | 116249.59 | 5.8862 |
| 2026-01 | 31 | 3 | 0 | 0 | 161 | 0 | 11 | 17 | 1290.67 | 11571.80 | 1888604.55 | 71208.86 | 3.7194 |
| 2026-02 | 28 | 4 | 0 | 0 | 124 | 0 | 12 | 12 | 16767.40 | 221634.39 | 2110238.96 | 115943.66 | 5.5494 |
| 2026-03 | 31 | 5 | 0 | 0 | 153 | 0 | 12 | 14 | 4772.23 | 62448.03 | 2172687.03 | 57888.12 | 2.6384 |
| 2026-04 | 30 | 1 | 0 | 0 | 155 | 0 | 11 | 18 | -206.37 | -1041.31 | 2171645.67 | 48848.81 | 2.2249 |
| 2026-05 | 10 | 1 | 0 | 0 | 38 | 1 | 5 | 4 | 588.50 | 8535.26 | 2180180.93 | 22317.95 | 1.0150 |

## Gap Events / Exceptions

- `2021-11-23 23:00:00+00:00` -> `2021-11-24 01:00:00+00:00`: `1` missing candles; active trade = `YES`. Missing 1 candle(s) between 2021-11-23 23:00:00+00:00 and 2021-11-24 01:00:00+00:00; resumed on next available row.
- `2023-03-04 16:00:00+00:00` -> `2023-03-04 22:00:00+00:00`: `5` missing candles; active trade = `YES`. Missing 5 candle(s) between 2023-03-04 16:00:00+00:00 and 2023-03-04 22:00:00+00:00; resumed on next available row.
- `2023-05-19 06:00:00+00:00` -> `2023-05-19 09:00:00+00:00`: `2` missing candles; active trade = `YES`. Missing 2 candle(s) between 2023-05-19 06:00:00+00:00 and 2023-05-19 09:00:00+00:00; resumed on next available row.
- `2024-02-09 20:00:00+00:00` -> `2024-02-09 22:00:00+00:00`: `1` missing candles; active trade = `YES`. Missing 1 candle(s) between 2024-02-09 20:00:00+00:00 and 2024-02-09 22:00:00+00:00; resumed on next available row.
- `2024-05-31 21:00:00+00:00` -> `2024-06-01 00:00:00+00:00`: `2` missing candles; active trade = `YES`. Missing 2 candle(s) between 2024-05-31 21:00:00+00:00 and 2024-06-01 00:00:00+00:00; resumed on next available row.
- `2024-10-26 15:00:00+00:00` -> `2024-10-26 18:00:00+00:00`: `2` missing candles; active trade = `YES`. Missing 2 candle(s) between 2024-10-26 15:00:00+00:00 and 2024-10-26 18:00:00+00:00; resumed on next available row.
- `2025-10-25 14:00:00+00:00` -> `2025-10-25 21:00:00+00:00`: `6` missing candles; active trade = `YES`. Missing 6 candle(s) between 2025-10-25 14:00:00+00:00 and 2025-10-25 21:00:00+00:00; resumed on next available row.
- `2026-05-08 00:00:00+00:00` -> `2026-05-08 08:00:00+00:00`: `7` missing candles; active trade = `YES`. Missing 7 candle(s) between 2026-05-08 00:00:00+00:00 and 2026-05-08 08:00:00+00:00; resumed on next available row.

## Output Files

- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/1h_ma24/trades.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/1h_ma24/gap_events.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/1h_ma24/daywise_summary.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/1h_ma24/monthly_summary.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/1h_ma24/yearly_summary.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/1h_ma24/equity_curve.csv`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/1h_ma24/summary.json`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/1h_ma24/summary.md`
- `btc/results/btc_ma_continuous_multi_timeframe_capital_smoke_full/1h_ma24/backtest.log`

## Remarks

- The one-time activation threshold is applied only on the first candidate UTC date.
- Opposite signals are ignored while a position is live; only the trailing SMA stop or a gap flat can close the trade.
- The entry candle itself cannot stop a newly opened position.
- Daywise results are grouped by realized exit date in UTC; held-only dates are preserved separately.
- Monthly and yearly drawdowns are period-local from day-ending equity; overall drawdown is full-run.
