# Squeeze Momentum Indicator [LazyBear] Multi-Timeframe Backtest

## Executive Summary

- **generated_at**: 2026-04-30T13:11:51
- **markets_tested**: derivatives, equity, commodities, usdinr
- **timeframes_tested**: 5m, 15m, 30m, 1h
- **variants_tested**: squeeze_release, momentum_zero_cross
- **starting_capital**: 1000000.0
- **best_after_brokerage**: 1h / momentum_zero_cross = 7106.03
- **best_before_brokerage**: 1h / momentum_zero_cross = 21544.8
- **source_note**: The local Pine file is empty, so this uses the canonical LazyBear formula.
- **pnl_note**: Before Brokerage includes configured slippage; After Brokerage subtracts segment-wise brokerage, taxes, and charges.

## Timeframe And Variant Results

| Timeframe | Variant | Files | Signals | Trades | Before Brokerage | Brokerage/Charges | After Brokerage | Win % | Max DD % | PF | Sharpe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5m | squeeze_release | 21 | 873 | 617 | -7619808.56 | 3187074.25 | -10806882.8 | 28.2 | -1086.9749 | 0.0978 | 2.6568 |
| 5m | momentum_zero_cross | 21 | 1416 | 1399 | -17345085.62 | 7165404.13 | -24510489.77 | 22.37 | -2457.4766 | 0.065 | -1.9389 |
| 15m | squeeze_release | 21 | 272 | 233 | -2695135.07 | 1143625.98 | -3838761.05 | 33.48 | -383.8761 | 0.0863 | -3.1078 |
| 15m | momentum_zero_cross | 21 | 450 | 423 | -5930932.81 | 2400154.72 | -8331087.54 | 28.61 | -833.7714 | 0.0652 | -0.8254 |
| 30m | squeeze_release | 21 | 64 | 56 | -948326.8 | 326374.39 | -1274701.19 | 32.14 | -129.0547 | 0.0654 | -3.7331 |
| 30m | momentum_zero_cross | 21 | 194 | 186 | -2412786.19 | 1028881.41 | -3441667.6 | 31.18 | -344.1668 | 0.0667 | 3.8058 |
| 1h | squeeze_release | 21 | 23 | 17 | 7820.14 | 7412.06 | 408.08 | 52.94 | -2.8507 | 1.0097 | 0.1357 |
| 1h | momentum_zero_cross | 21 | 35 | 32 | 21544.8 | 14438.77 | 7106.03 | 50.0 | -1.541 | 1.1378 | 1.6032 |

## Best Variant Per Timeframe

| Timeframe | Best Variant | Trades | Before Brokerage | Brokerage/Charges | After Brokerage | Win % | PF |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5m | squeeze_release | 617 | -7619808.56 | 3187074.25 | -10806882.8 | 28.2 | 0.0978 |
| 15m | squeeze_release | 233 | -2695135.07 | 1143625.98 | -3838761.05 | 33.48 | 0.0863 |
| 30m | squeeze_release | 56 | -948326.8 | 326374.39 | -1274701.19 | 32.14 | 0.0654 |
| 1h | momentum_zero_cross | 32 | 21544.8 | 14438.77 | 7106.03 | 50.0 | 1.1378 |

## What Was Traded

| Timeframe | Variant | Market | Instrument | Trades | Long | Short | Before Brokerage | Charges | After Brokerage | Win % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5m | squeeze_release | commodities | CLF | 36 | 19 | 17 | -179938.09 | 620246.47 | -800184.56 | 8.33 |
| 5m | squeeze_release | commodities | GCF | 36 | 16 | 20 | -9304.06 | 619182.14 | -628486.2 | 0.0 |
| 5m | squeeze_release | commodities | HGF | 30 | 16 | 14 | -2007790.49 | 516613.15 | -2524403.64 | 0.0 |
| 5m | squeeze_release | commodities | NGF | 36 | 18 | 18 | -5338905.41 | 623554.16 | -5962459.57 | 0.0 |
| 5m | squeeze_release | commodities | SIF | 35 | 16 | 19 | -166457.81 | 603779.01 | -770236.82 | 0.0 |
| 5m | squeeze_release | derivatives | CNXAUTO | 24 | 14 | 10 | 29827.91 | 14530.52 | 15297.39 | 41.67 |
| 5m | squeeze_release | derivatives | CNXFMCG | 24 | 14 | 10 | 28719.56 | 14353.68 | 14365.88 | 54.17 |
| 5m | squeeze_release | derivatives | CNXIT | 33 | 18 | 15 | 23200.98 | 19920.76 | 3280.23 | 36.36 |
| 5m | squeeze_release | derivatives | NSEBANK | 20 | 11 | 9 | 57784.37 | 11899.2 | 45885.17 | 60.0 |
| 5m | squeeze_release | derivatives | NSEI | 25 | 13 | 12 | 14764.73 | 15137.19 | -372.46 | 44.0 |
| 5m | squeeze_release | equity | BHARTIARTL_NS | 26 | 12 | 14 | 30870.64 | 10452.89 | 20417.75 | 46.15 |
| 5m | squeeze_release | equity | HDFCBANK_NS | 27 | 13 | 14 | -76506.42 | 10866.11 | -87372.53 | 33.33 |
| 5m | squeeze_release | equity | ICICIBANK_NS | 28 | 15 | 13 | 41546.62 | 11246.35 | 30300.27 | 46.43 |
| 5m | squeeze_release | equity | INFY_NS | 31 | 16 | 15 | 49669.24 | 12460.71 | 37208.53 | 41.94 |
| 5m | squeeze_release | equity | ITC_NS | 36 | 19 | 17 | -104942.34 | 14479.9 | -119422.24 | 13.89 |
| 5m | squeeze_release | equity | KOTAKBANK_NS | 31 | 16 | 15 | 7355.09 | 12471.62 | -5116.53 | 38.71 |
| 5m | squeeze_release | equity | LT_NS | 27 | 14 | 13 | 43812.83 | 10847.42 | 32965.41 | 51.85 |
| 5m | squeeze_release | equity | RELIANCE_NS | 32 | 18 | 14 | -18947.63 | 12871.87 | -31819.5 | 37.5 |
| 5m | squeeze_release | equity | SBIN_NS | 29 | 15 | 14 | 1863.23 | 11657.92 | -9794.69 | 37.93 |
| 5m | squeeze_release | equity | TCS_NS | 27 | 16 | 11 | 58102.62 | 10854.34 | 47248.28 | 44.44 |
| 5m | squeeze_release | usdinr | USDINR | 24 | 11 | 13 | -104534.13 | 9648.84 | -114182.97 | 0.0 |
| 5m | momentum_zero_cross | commodities | CLF | 82 | 41 | 41 | -503009.95 | 1414212.91 | -1917222.86 | 6.1 |
| 5m | momentum_zero_cross | commodities | GCF | 71 | 35 | 36 | -7360.06 | 1220889.31 | -1228249.37 | 0.0 |
| 5m | momentum_zero_cross | commodities | HGF | 86 | 42 | 44 | -5867654.39 | 1487070.05 | -7354724.44 | 0.0 |
| 5m | momentum_zero_cross | commodities | NGF | 72 | 37 | 35 | -10566613.84 | 1246031.65 | -11812645.49 | 0.0 |
| 5m | momentum_zero_cross | commodities | SIF | 77 | 38 | 39 | -387891.85 | 1327487.55 | -1715379.4 | 1.3 |
| 5m | momentum_zero_cross | derivatives | CNXAUTO | 59 | 30 | 29 | -12656.05 | 35662.46 | -48318.51 | 37.29 |
| 5m | momentum_zero_cross | derivatives | CNXFMCG | 62 | 31 | 31 | -17866.25 | 37048.14 | -54914.39 | 27.42 |
| 5m | momentum_zero_cross | derivatives | CNXIT | 77 | 38 | 39 | 12880.61 | 46374.63 | -33494.04 | 23.38 |
| 5m | momentum_zero_cross | derivatives | NSEBANK | 58 | 30 | 28 | 59275.16 | 34537.02 | 24738.14 | 31.03 |
| 5m | momentum_zero_cross | derivatives | NSEI | 62 | 31 | 31 | -8727.75 | 37561.49 | -46289.24 | 22.58 |
| 5m | momentum_zero_cross | equity | BHARTIARTL_NS | 76 | 38 | 38 | -29967.08 | 30541.21 | -60508.29 | 31.58 |
| 5m | momentum_zero_cross | equity | HDFCBANK_NS | 58 | 29 | 29 | 20626.27 | 23317.91 | -2691.64 | 39.66 |
| 5m | momentum_zero_cross | equity | ICICIBANK_NS | 62 | 31 | 31 | 77481.81 | 24929.01 | 52552.8 | 38.71 |
| 5m | momentum_zero_cross | equity | INFY_NS | 63 | 31 | 32 | 28115.32 | 25316.12 | 2799.2 | 33.33 |
| 5m | momentum_zero_cross | equity | ITC_NS | 77 | 39 | 38 | -135505.26 | 30959.79 | -166465.05 | 15.58 |
| 5m | momentum_zero_cross | equity | KOTAKBANK_NS | 54 | 27 | 27 | 19265.49 | 21720.72 | -2455.23 | 42.59 |
| 5m | momentum_zero_cross | equity | LT_NS | 69 | 34 | 35 | 3315.96 | 27698.43 | -24382.47 | 33.33 |
| 5m | momentum_zero_cross | equity | RELIANCE_NS | 64 | 33 | 31 | 46879.94 | 25718.22 | 21161.72 | 39.06 |
| 5m | momentum_zero_cross | equity | SBIN_NS | 59 | 30 | 29 | 87949.54 | 23725.01 | 64224.53 | 33.9 |
| 5m | momentum_zero_cross | equity | TCS_NS | 60 | 30 | 30 | 64580.22 | 24104.03 | 40476.19 | 38.33 |
| 5m | momentum_zero_cross | usdinr | USDINR | 51 | 26 | 25 | -228203.46 | 20498.47 | -248701.93 | 0.0 |
| 15m | squeeze_release | commodities | CLF | 10 | 7 | 3 | -41210.21 | 172063.07 | -213273.28 | 10.0 |
| 15m | squeeze_release | commodities | GCF | 14 | 3 | 11 | -8869.38 | 240937.74 | -249807.12 | 0.0 |
| 15m | squeeze_release | commodities | HGF | 13 | 8 | 5 | -924616.11 | 221916.19 | -1146532.3 | 0.0 |
| 15m | squeeze_release | commodities | NGF | 11 | 6 | 5 | -1624552.53 | 188785.57 | -1813338.1 | 0.0 |
| 15m | squeeze_release | commodities | SIF | 14 | 7 | 7 | -76270.3 | 240966.59 | -317236.89 | 0.0 |
| 15m | squeeze_release | derivatives | CNXAUTO | 12 | 6 | 6 | -12228.54 | 7258.69 | -19487.23 | 33.33 |
| 15m | squeeze_release | derivatives | CNXFMCG | 11 | 7 | 4 | 14965.69 | 6593.22 | 8372.47 | 45.45 |
| 15m | squeeze_release | derivatives | CNXIT | 7 | 3 | 4 | 25528.68 | 4258.68 | 21270.0 | 57.14 |
| 15m | squeeze_release | derivatives | NSEBANK | 10 | 6 | 4 | 14254.32 | 5957.65 | 8296.67 | 60.0 |
| 15m | squeeze_release | derivatives | NSEI | 11 | 5 | 6 | 3873.25 | 6664.22 | -2790.97 | 63.64 |
| 15m | squeeze_release | equity | BHARTIARTL_NS | 13 | 7 | 6 | 4228.76 | 5224.87 | -996.11 | 46.15 |
| 15m | squeeze_release | equity | HDFCBANK_NS | 12 | 6 | 6 | 1827.34 | 4818.99 | -2991.65 | 41.67 |
| 15m | squeeze_release | equity | ICICIBANK_NS | 8 | 3 | 5 | -47693.97 | 3225.09 | -50919.06 | 37.5 |
| 15m | squeeze_release | equity | INFY_NS | 11 | 4 | 7 | -12105.8 | 4421.43 | -16527.23 | 54.55 |
| 15m | squeeze_release | equity | ITC_NS | 12 | 7 | 5 | 9086.03 | 4826.65 | 4259.38 | 50.0 |
| 15m | squeeze_release | equity | KOTAKBANK_NS | 12 | 8 | 4 | -29164.17 | 4819.17 | -33983.34 | 16.67 |
| 15m | squeeze_release | equity | LT_NS | 13 | 5 | 8 | 34654.14 | 5216.61 | 29437.53 | 76.92 |
| 15m | squeeze_release | equity | RELIANCE_NS | 9 | 4 | 5 | 32497.37 | 3622.64 | 28874.73 | 66.67 |
| 15m | squeeze_release | equity | SBIN_NS | 10 | 5 | 5 | -4951.87 | 4017.65 | -8969.52 | 40.0 |
| 15m | squeeze_release | equity | TCS_NS | 10 | 7 | 3 | -18017.06 | 4010.16 | -22027.22 | 30.0 |
| 15m | squeeze_release | usdinr | USDINR | 10 | 4 | 6 | -36370.71 | 4021.1 | -40391.81 | 0.0 |
| 15m | momentum_zero_cross | commodities | CLF | 25 | 13 | 12 | -187840.4 | 431477.89 | -619318.29 | 4.0 |
| 15m | momentum_zero_cross | commodities | GCF | 28 | 14 | 14 | 33214.05 | 481429.39 | -448215.34 | 0.0 |
| 15m | momentum_zero_cross | commodities | HGF | 27 | 14 | 13 | -1779846.77 | 465679.41 | -2245526.18 | 0.0 |
| 15m | momentum_zero_cross | commodities | NGF | 25 | 12 | 13 | -3797629.13 | 435778.02 | -4233407.15 | 0.0 |
| 15m | momentum_zero_cross | commodities | SIF | 26 | 13 | 13 | -124450.85 | 448641.18 | -573092.03 | 7.69 |
| 15m | momentum_zero_cross | derivatives | CNXAUTO | 20 | 10 | 10 | -9569.82 | 12109.8 | -21679.62 | 35.0 |
| 15m | momentum_zero_cross | derivatives | CNXFMCG | 19 | 10 | 9 | -1738.12 | 11347.29 | -13085.41 | 47.37 |
| 15m | momentum_zero_cross | derivatives | CNXIT | 27 | 13 | 14 | -6403.4 | 16317.07 | -22720.48 | 37.04 |
| 15m | momentum_zero_cross | derivatives | NSEBANK | 19 | 9 | 10 | -7637.86 | 11317.47 | -18955.33 | 42.11 |
| 15m | momentum_zero_cross | derivatives | NSEI | 14 | 8 | 6 | -12040.32 | 8477.52 | -20517.84 | 35.71 |
| 15m | momentum_zero_cross | equity | BHARTIARTL_NS | 15 | 7 | 8 | 11677.95 | 6032.07 | 5645.88 | 46.67 |
| 15m | momentum_zero_cross | equity | HDFCBANK_NS | 16 | 8 | 8 | 24154.34 | 6422.98 | 17731.36 | 50.0 |
| 15m | momentum_zero_cross | equity | ICICIBANK_NS | 15 | 7 | 8 | -10548.7 | 6042.74 | -16591.44 | 46.67 |
| 15m | momentum_zero_cross | equity | INFY_NS | 26 | 13 | 13 | -41612.66 | 10448.47 | -52061.13 | 23.08 |
| 15m | momentum_zero_cross | equity | ITC_NS | 17 | 10 | 7 | 12240.98 | 6839.27 | 5401.71 | 41.18 |
| 15m | momentum_zero_cross | equity | KOTAKBANK_NS | 21 | 10 | 11 | -41135.87 | 8441.48 | -49577.35 | 38.1 |
| 15m | momentum_zero_cross | equity | LT_NS | 19 | 10 | 9 | -26380.02 | 7620.06 | -34000.08 | 47.37 |
| 15m | momentum_zero_cross | equity | RELIANCE_NS | 16 | 7 | 9 | 36982.82 | 6433.11 | 30549.71 | 56.25 |
| 15m | momentum_zero_cross | equity | SBIN_NS | 20 | 10 | 10 | -5613.3 | 8050.56 | -13663.86 | 40.0 |
| 15m | momentum_zero_cross | equity | TCS_NS | 16 | 7 | 9 | 58178.06 | 6429.33 | 51748.73 | 62.5 |
| 15m | momentum_zero_cross | usdinr | USDINR | 12 | 7 | 5 | -54933.79 | 4819.61 | -59753.4 | 0.0 |
| 30m | squeeze_release | commodities | CLF | 3 | 2 | 1 | -78098.02 | 50866.42 | -128964.44 | 0.0 |
| 30m | squeeze_release | commodities | GCF | 4 | 3 | 1 | -18783.08 | 68550.11 | -87333.19 | 0.0 |
| 30m | squeeze_release | commodities | HGF | 2 | 1 | 1 | -144146.11 | 34532.89 | -178679.0 | 0.0 |
| 30m | squeeze_release | commodities | NGF | 5 | 3 | 2 | -732159.04 | 85019.02 | -817178.06 | 0.0 |
| 30m | squeeze_release | commodities | SIF | 4 | 2 | 2 | -13421.25 | 69518.47 | -82939.72 | 0.0 |
| 30m | squeeze_release | derivatives | CNXAUTO | 2 | 1 | 1 | 5014.31 | 1203.89 | 3810.42 | 50.0 |
| 30m | squeeze_release | derivatives | CNXFMCG | 3 | 2 | 1 | 7080.22 | 1824.38 | 5255.84 | 66.67 |
| 30m | squeeze_release | derivatives | CNXIT | 3 | 1 | 2 | 17554.92 | 1812.05 | 15742.87 | 100.0 |
| 30m | squeeze_release | derivatives | NSEBANK | 3 | 2 | 1 | 6411.02 | 1782.79 | 4628.23 | 33.33 |
| 30m | squeeze_release | derivatives | NSEI | 2 | 1 | 1 | -1172.05 | 1219.77 | -2391.82 | 0.0 |
| 30m | squeeze_release | equity | BHARTIARTL_NS | 5 | 5 | 0 | 1827.72 | 2009.38 | -181.66 | 40.0 |
| 30m | squeeze_release | equity | HDFCBANK_NS | 2 | 2 | 0 | 6619.82 | 805.59 | 5814.23 | 50.0 |
| 30m | squeeze_release | equity | ICICIBANK_NS | 4 | 1 | 3 | -14902.56 | 1606.41 | -16508.97 | 25.0 |
| 30m | squeeze_release | equity | INFY_NS | 1 | 0 | 1 | 6342.3 | 400.18 | 5942.12 | 100.0 |
| 30m | squeeze_release | equity | ITC_NS | 6 | 3 | 3 | 11885.52 | 2413.6 | 9471.92 | 50.0 |
| 30m | squeeze_release | equity | KOTAKBANK_NS | 2 | 1 | 1 | -5013.19 | 802.14 | -5815.33 | 50.0 |
| 30m | squeeze_release | equity | LT_NS | 2 | 1 | 1 | -3475.47 | 802.55 | -4278.02 | 0.0 |
| 30m | squeeze_release | equity | RELIANCE_NS | 1 | 1 | 0 | -3670.1 | 400.61 | -4070.71 | 0.0 |
| 30m | squeeze_release | equity | SBIN_NS | 1 | 0 | 1 | 859.84 | 401.57 | 458.27 | 100.0 |
| 30m | squeeze_release | equity | TCS_NS | 1 | 1 | 0 | 2918.4 | 402.57 | 2515.83 | 100.0 |
| 30m | momentum_zero_cross | commodities | CLF | 11 | 6 | 5 | -94017.98 | 189793.51 | -283811.49 | 18.18 |
| 30m | momentum_zero_cross | commodities | GCF | 13 | 6 | 7 | -10442.7 | 223615.34 | -234058.04 | 0.0 |
| 30m | momentum_zero_cross | commodities | HGF | 9 | 4 | 5 | -614680.04 | 156450.06 | -771130.1 | 0.0 |
| 30m | momentum_zero_cross | commodities | NGF | 10 | 5 | 5 | -1512906.53 | 173454.34 | -1686360.87 | 0.0 |
| 30m | momentum_zero_cross | commodities | SIF | 13 | 6 | 7 | -174534.89 | 224378.28 | -398913.17 | 0.0 |
| 30m | momentum_zero_cross | derivatives | CNXAUTO | 9 | 5 | 4 | 7579.26 | 5431.16 | 2148.1 | 55.56 |
| 30m | momentum_zero_cross | derivatives | CNXFMCG | 10 | 5 | 5 | 22442.38 | 5975.4 | 16466.98 | 60.0 |
| 30m | momentum_zero_cross | derivatives | CNXIT | 7 | 4 | 3 | 801.15 | 4233.44 | -3432.29 | 42.86 |
| 30m | momentum_zero_cross | derivatives | NSEBANK | 9 | 5 | 4 | -15140.65 | 5316.34 | -20456.99 | 44.44 |
| 30m | momentum_zero_cross | derivatives | NSEI | 10 | 5 | 5 | -6462.27 | 6074.68 | -12536.95 | 40.0 |
| 30m | momentum_zero_cross | equity | BHARTIARTL_NS | 8 | 4 | 4 | 3985.94 | 3210.41 | 775.53 | 37.5 |
| 30m | momentum_zero_cross | equity | HDFCBANK_NS | 8 | 3 | 5 | 14816.38 | 3217.76 | 11598.62 | 62.5 |
| 30m | momentum_zero_cross | equity | ICICIBANK_NS | 5 | 2 | 3 | 3108.82 | 2012.39 | 1096.43 | 60.0 |
| 30m | momentum_zero_cross | equity | INFY_NS | 8 | 4 | 4 | -23327.76 | 3211.48 | -26539.24 | 12.5 |
| 30m | momentum_zero_cross | equity | ITC_NS | 7 | 4 | 3 | -29358.53 | 2815.38 | -32173.91 | 14.29 |
| 30m | momentum_zero_cross | equity | KOTAKBANK_NS | 8 | 4 | 4 | -29093.88 | 3217.48 | -32311.36 | 25.0 |
| 30m | momentum_zero_cross | equity | LT_NS | 8 | 4 | 4 | -6942.94 | 3207.73 | -10150.67 | 37.5 |
| 30m | momentum_zero_cross | equity | RELIANCE_NS | 10 | 5 | 5 | 36882.99 | 4027.74 | 32855.25 | 80.0 |
| 30m | momentum_zero_cross | equity | SBIN_NS | 9 | 4 | 5 | 4811.87 | 3622.21 | 1189.66 | 55.56 |
| 30m | momentum_zero_cross | equity | TCS_NS | 8 | 4 | 4 | 30296.5 | 3205.0 | 27091.5 | 37.5 |
| 30m | momentum_zero_cross | usdinr | USDINR | 6 | 3 | 3 | -20603.31 | 2411.28 | -23014.59 | 0.0 |
| 1h | squeeze_release | derivatives | CNXAUTO | 1 | 1 | 0 | -3259.76 | 604.45 | -3864.21 | 0.0 |
| 1h | squeeze_release | derivatives | CNXIT | 1 | 0 | 1 | 5044.81 | 599.54 | 4445.27 | 100.0 |
| 1h | squeeze_release | derivatives | NSEBANK | 1 | 0 | 1 | 3129.66 | 580.16 | 2549.5 | 100.0 |
| 1h | squeeze_release | equity | BHARTIARTL_NS | 2 | 1 | 1 | -3187.27 | 801.43 | -3988.7 | 50.0 |
| 1h | squeeze_release | equity | HDFCBANK_NS | 2 | 1 | 1 | -15264.82 | 799.95 | -16064.77 | 0.0 |
| 1h | squeeze_release | equity | ICICIBANK_NS | 1 | 1 | 0 | 7152.0 | 404.05 | 6747.95 | 100.0 |
| 1h | squeeze_release | equity | INFY_NS | 1 | 0 | 1 | 1886.34 | 401.23 | 1485.11 | 100.0 |
| 1h | squeeze_release | equity | ITC_NS | 1 | 0 | 1 | -654.66 | 402.11 | -1056.77 | 0.0 |
| 1h | squeeze_release | equity | KOTAKBANK_NS | 1 | 0 | 1 | 1057.17 | 401.65 | 655.52 | 100.0 |
| 1h | squeeze_release | equity | LT_NS | 2 | 1 | 1 | -6658.25 | 801.64 | -7459.89 | 0.0 |
| 1h | squeeze_release | equity | RELIANCE_NS | 1 | 0 | 1 | 1409.75 | 401.29 | 1008.46 | 100.0 |
| 1h | squeeze_release | equity | SBIN_NS | 2 | 1 | 1 | 14246.77 | 811.99 | 13434.78 | 50.0 |
| 1h | squeeze_release | equity | TCS_NS | 1 | 1 | 0 | 2918.4 | 402.57 | 2515.83 | 100.0 |
| 1h | momentum_zero_cross | derivatives | CNXAUTO | 1 | 0 | 1 | 8793.21 | 603.18 | 8190.03 | 100.0 |
| 1h | momentum_zero_cross | derivatives | CNXFMCG | 2 | 1 | 1 | -1817.32 | 1186.29 | -3003.61 | 0.0 |
| 1h | momentum_zero_cross | derivatives | CNXIT | 2 | 1 | 1 | -1046.86 | 1208.12 | -2254.98 | 50.0 |
| 1h | momentum_zero_cross | derivatives | NSEBANK | 1 | 0 | 1 | 1213.77 | 588.74 | 625.03 | 100.0 |
| 1h | momentum_zero_cross | derivatives | NSEI | 2 | 1 | 1 | -1277.17 | 1211.84 | -2489.01 | 50.0 |
| 1h | momentum_zero_cross | equity | BHARTIARTL_NS | 3 | 2 | 1 | 4661.07 | 1207.21 | 3453.86 | 33.33 |
| 1h | momentum_zero_cross | equity | HDFCBANK_NS | 5 | 2 | 3 | 15626.22 | 2005.18 | 13621.04 | 60.0 |
| 1h | momentum_zero_cross | equity | ICICIBANK_NS | 3 | 1 | 2 | -4820.08 | 1209.18 | -6029.26 | 33.33 |
| 1h | momentum_zero_cross | equity | INFY_NS | 2 | 1 | 1 | -9523.3 | 801.48 | -10324.78 | 0.0 |
| 1h | momentum_zero_cross | equity | ITC_NS | 2 | 1 | 1 | -3115.33 | 802.37 | -3917.7 | 50.0 |
| 1h | momentum_zero_cross | equity | KOTAKBANK_NS | 2 | 1 | 1 | -2754.65 | 804.63 | -3559.28 | 0.0 |
| 1h | momentum_zero_cross | equity | LT_NS | 1 | 1 | 0 | -3969.01 | 399.95 | -4368.96 | 0.0 |
| 1h | momentum_zero_cross | equity | RELIANCE_NS | 2 | 1 | 1 | 4246.38 | 804.37 | 3442.01 | 100.0 |
| 1h | momentum_zero_cross | equity | SBIN_NS | 2 | 1 | 1 | 3796.95 | 804.25 | 2992.7 | 100.0 |
| 1h | momentum_zero_cross | equity | TCS_NS | 2 | 1 | 1 | 11530.92 | 801.98 | 10728.94 | 100.0 |

## Brokerage And Charges

| Timeframe | Variant | Segment | Trades | Turnover | Brokerage | STT | CTT | Exchange | GST | SEBI | Stamp | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5m | squeeze_release | Commodity futures MCX | 173 | 346020627.61 | 6920.0 | 0.0 | 1731123.12 | 726643.36 | 138269.78 | 34602.05 | 345816.68 | 2983374.93 |
| 5m | squeeze_release | F&O futures NSE | 126 | 247068883.43 | 5040.0 | 61798.0 | 0.0 | 4521.33 | 1765.53 | 247.06 | 2469.45 | 75841.35 |
| 5m | squeeze_release | Intraday equity NSE | 318 | 635904714.15 | 12720.0 | 79527.9 | 0.0 | 19522.24 | 5918.15 | 635.84 | 9533.83 | 127857.97 |
| 5m | momentum_zero_cross | Commodity futures MCX | 388 | 776431458.99 | 15520.0 | 0.0 | 3886123.6 | 1630506.12 | 310260.34 | 77643.29 | 775638.35 | 6695691.47 |
| 5m | momentum_zero_cross | F&O futures NSE | 318 | 622852146.01 | 12720.0 | 155762.69 | 0.0 | 11398.32 | 4453.37 | 622.88 | 6226.52 | 191183.74 |
| 5m | momentum_zero_cross | Intraday equity NSE | 693 | 1385407555.64 | 27720.0 | 173220.94 | 0.0 | 42531.98 | 12894.71 | 1385.5 | 20775.62 | 278528.92 |
| 15m | squeeze_release | Commodity futures MCX | 62 | 123650172.44 | 2480.0 | 0.0 | 616808.12 | 259665.37 | 49411.87 | 12365.0 | 123938.75 | 1064669.16 |
| 15m | squeeze_release | F&O futures NSE | 51 | 100080625.17 | 2040.0 | 25046.27 | 0.0 | 1831.47 | 714.86 | 100.11 | 999.75 | 30732.46 |
| 15m | squeeze_release | Intraday equity NSE | 120 | 239873870.57 | 4800.0 | 29990.26 | 0.0 | 7364.14 | 2232.73 | 239.88 | 3597.41 | 48224.36 |
| 15m | momentum_zero_cross | Commodity futures MCX | 131 | 262322947.36 | 5240.0 | 0.0 | 1313982.98 | 550878.21 | 104823.14 | 26232.27 | 261849.33 | 2263005.89 |
| 15m | momentum_zero_cross | F&O futures NSE | 99 | 194054224.39 | 3960.0 | 48537.45 | 0.0 | 3551.17 | 1386.96 | 194.04 | 1939.58 | 59569.15 |
| 15m | momentum_zero_cross | Intraday equity NSE | 193 | 385868378.81 | 7720.0 | 48250.25 | 0.0 | 11846.14 | 3591.29 | 385.87 | 5786.06 | 77579.68 |
| 30m | squeeze_release | Commodity futures MCX | 18 | 35849434.74 | 720.0 | 0.0 | 178591.63 | 75283.83 | 14325.98 | 3584.94 | 35980.55 | 308486.91 |
| 30m | squeeze_release | F&O futures NSE | 13 | 25575958.31 | 520.0 | 6390.9 | 0.0 | 468.03 | 182.45 | 25.56 | 255.89 | 7842.88 |
| 30m | squeeze_release | Intraday equity NSE | 25 | 49967102.53 | 1000.0 | 6246.04 | 0.0 | 1533.97 | 465.11 | 49.97 | 749.48 | 10044.6 |
| 30m | momentum_zero_cross | Commodity futures MCX | 56 | 112155836.05 | 2240.0 | 0.0 | 561975.15 | 235527.26 | 44816.92 | 11215.61 | 111916.64 | 967691.53 |
| 30m | momentum_zero_cross | F&O futures NSE | 45 | 88080363.13 | 1800.0 | 22020.29 | 0.0 | 1611.87 | 629.98 | 88.06 | 880.81 | 27031.02 |
| 30m | momentum_zero_cross | Intraday equity NSE | 85 | 169911768.28 | 3400.0 | 21242.9 | 0.0 | 5216.25 | 1581.51 | 169.94 | 2548.2 | 34158.86 |
| 1h | squeeze_release | F&O futures NSE | 3 | 5818407.92 | 120.0 | 1451.74 | 0.0 | 106.47 | 41.82 | 5.82 | 58.31 | 1784.15 |
| 1h | squeeze_release | Intraday equity NSE | 14 | 27990463.23 | 560.0 | 3500.44 | 0.0 | 859.31 | 260.5 | 28.01 | 419.67 | 5627.91 |
| 1h | momentum_zero_cross | F&O futures NSE | 8 | 15647162.57 | 320.0 | 3907.6 | 0.0 | 286.35 | 111.96 | 15.65 | 156.64 | 4798.17 |
| 1h | momentum_zero_cross | Intraday equity NSE | 24 | 47960163.15 | 960.0 | 5994.31 | 0.0 | 1472.37 | 446.48 | 47.96 | 719.5 | 9640.6 |

## Direction And Exit Summary

| Timeframe | Variant | Direction | Exit | Trades | Before Brokerage | Charges | After Brokerage |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5m | squeeze_release | LONG | OPPOSITE_SIGNAL | 115 | -1549369.45 | 621493.26 | -2170862.71 |
| 5m | squeeze_release | LONG | SESSION_END | 205 | -1937851.9 | 904417.49 | -2842269.39 |
| 5m | squeeze_release | SHORT | OPPOSITE_SIGNAL | 122 | -1880972.8 | 596295.72 | -2477268.51 |
| 5m | squeeze_release | SHORT | SESSION_END | 175 | -2251614.41 | 1064867.78 | -3316482.19 |
| 5m | momentum_zero_cross | LONG | OPPOSITE_SIGNAL | 486 | -6176755.51 | 2466291.99 | -8643047.5 |
| 5m | momentum_zero_cross | LONG | SESSION_END | 215 | -1819799.41 | 991272.43 | -2811071.84 |
| 5m | momentum_zero_cross | SHORT | OPPOSITE_SIGNAL | 511 | -7565518.84 | 2675119.37 | -10240638.21 |
| 5m | momentum_zero_cross | SHORT | SESSION_END | 187 | -1783011.86 | 1032720.34 | -2815732.22 |
| 15m | squeeze_release | LONG | OPPOSITE_SIGNAL | 9 | -50363.87 | 20400.19 | -70764.06 |
| 15m | squeeze_release | LONG | SESSION_END | 109 | -1365148.73 | 535574.18 | -1900722.91 |
| 15m | squeeze_release | SHORT | OPPOSITE_SIGNAL | 10 | -133187.23 | 72890.83 | -206078.06 |
| 15m | squeeze_release | SHORT | SESSION_END | 105 | -1146435.24 | 514760.78 | -1661196.02 |
| 15m | momentum_zero_cross | LONG | OPPOSITE_SIGNAL | 63 | -1317180.57 | 368124.1 | -1685304.67 |
| 15m | momentum_zero_cross | LONG | SESSION_END | 149 | -1297050.07 | 803735.41 | -2100785.49 |
| 15m | momentum_zero_cross | SHORT | OPPOSITE_SIGNAL | 70 | -1244943.89 | 363874.67 | -1608818.56 |
| 15m | momentum_zero_cross | SHORT | SESSION_END | 141 | -2071758.28 | 864420.54 | -2936178.82 |
| 30m | squeeze_release | LONG | OPPOSITE_SIGNAL | 1 | -7907.25 | 399.38 | -8306.63 |
| 30m | squeeze_release | LONG | SESSION_END | 32 | -537416.44 | 192353.14 | -729769.58 |
| 30m | squeeze_release | SHORT | SESSION_END | 23 | -403003.11 | 133621.87 | -536624.98 |
| 30m | momentum_zero_cross | LONG | OPPOSITE_SIGNAL | 2 | -143707.48 | 15871.14 | -159578.62 |
| 30m | momentum_zero_cross | LONG | SESSION_END | 90 | -927023.71 | 466443.3 | -1393467.01 |
| 30m | momentum_zero_cross | SHORT | OPPOSITE_SIGNAL | 3 | -189592.44 | 37159.88 | -226752.32 |
| 30m | momentum_zero_cross | SHORT | SESSION_END | 91 | -1152462.56 | 509407.09 | -1661869.65 |
| 1h | squeeze_release | LONG | SESSION_END | 7 | 4725.79 | 3017.17 | 1708.62 |
| 1h | squeeze_release | SHORT | SESSION_END | 10 | 3094.35 | 4394.89 | -1300.54 |
| 1h | momentum_zero_cross | LONG | SESSION_END | 15 | -504.37 | 6624.77 | -7129.14 |
| 1h | momentum_zero_cross | SHORT | SESSION_END | 17 | 22049.17 | 7814.0 | 14235.17 |

## Best And Worst Trades

| Rank Type | Rank | Timeframe | Variant | Market | Instrument | Date | Direction | Exit | Before Brokerage | Charges | After Brokerage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| best | 1 | 5m | momentum_zero_cross | equity | SBIN_NS | 2026-04-02 | LONG | SESSION_END | 37207.91 | 412.7 | 36795.21 |
| best | 2 | 5m | squeeze_release | equity | LT_NS | 2026-04-06 | LONG | SESSION_END | 36640.45 | 412.2 | 36228.25 |
| best | 3 | 5m | squeeze_release | equity | SBIN_NS | 2026-04-02 | LONG | SESSION_END | 31877.96 | 410.89 | 31467.07 |
| best | 4 | 5m | momentum_zero_cross | equity | LT_NS | 2026-04-02 | LONG | SESSION_END | 31431.41 | 410.59 | 31020.82 |
| best | 5 | 5m | squeeze_release | equity | LT_NS | 2026-04-02 | LONG | SESSION_END | 31002.41 | 410.62 | 30591.79 |
| best | 6 | 5m | momentum_zero_cross | equity | LT_NS | 2026-04-06 | LONG | SESSION_END | 30580.85 | 409.96 | 30170.89 |
| best | 7 | 5m | squeeze_release | equity | ITC_NS | 2026-04-29 | LONG | SESSION_END | 27795.99 | 409.95 | 27386.04 |
| best | 8 | 5m | momentum_zero_cross | equity | RELIANCE_NS | 2026-04-06 | SHORT | OPPOSITE_SIGNAL | 26930.6 | 393.93 | 26536.67 |
| best | 9 | 5m | momentum_zero_cross | derivatives | NSEBANK | 2026-04-02 | LONG | SESSION_END | 26839.43 | 599.7 | 26239.73 |
| best | 10 | 30m | momentum_zero_cross | equity | TCS_NS | 2026-04-24 | SHORT | SESSION_END | 25677.02 | 393.98 | 25283.04 |
| worst | 1 | 5m | momentum_zero_cross | commodities | NGF | 2026-04-15 | SHORT | OPPOSITE_SIGNAL | -177601.14 | 19476.24 | -197077.38 |
| worst | 2 | 15m | momentum_zero_cross | commodities | NGF | 2026-04-20 | SHORT | OPPOSITE_SIGNAL | -176019.33 | 19456.33 | -195475.66 |
| worst | 3 | 30m | momentum_zero_cross | commodities | NGF | 2026-04-21 | SHORT | OPPOSITE_SIGNAL | -174686.51 | 19439.54 | -194126.05 |
| worst | 4 | 15m | momentum_zero_cross | commodities | NGF | 2026-04-15 | SHORT | OPPOSITE_SIGNAL | -174094.06 | 19432.08 | -193526.14 |
| worst | 5 | 5m | momentum_zero_cross | commodities | NGF | 2026-04-15 | SHORT | OPPOSITE_SIGNAL | -174058.54 | 19431.64 | -193490.18 |
| worst | 6 | 15m | squeeze_release | commodities | NGF | 2026-04-14 | SHORT | SESSION_END | -173584.81 | 19425.67 | -193010.48 |
| worst | 7 | 15m | momentum_zero_cross | commodities | NGF | 2026-04-23 | SHORT | SESSION_END | -171246.18 | 19396.19 | -190642.37 |
| worst | 8 | 30m | momentum_zero_cross | commodities | NGF | 2026-04-23 | SHORT | SESSION_END | -170314.01 | 19384.44 | -189698.45 |
| worst | 9 | 5m | momentum_zero_cross | commodities | NGF | 2026-04-17 | SHORT | OPPOSITE_SIGNAL | -170212.68 | 19383.19 | -189595.87 |
| worst | 10 | 5m | momentum_zero_cross | commodities | NGF | 2026-04-10 | SHORT | OPPOSITE_SIGNAL | -169918.66 | 19379.49 | -189298.15 |

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

## Timeframe Session Policy

| Timeframe | Session Start | Exit Time | Require Session Open | Note |
| --- | --- | --- | --- | --- |
| 5m | 09:15 | 15:20 | True | Uses configured session-open rule. |
| 15m | 09:15 | 15:20 | True | Uses configured session-open rule. |
| 30m | 09:15 | 15:20 | False | 30m Yahoo candles are aligned to 09:00/09:30, so the first available session candle is accepted. |
| 1h | 09:15 | 15:20 | True | Uses configured session-open rule. |

## Backtest Rules

- Bollinger Bands use configured `bb_length` and `bb_mult`.
- Keltner Channels use configured `kc_length`, `kc_mult`, and true range by default.
- Momentum is `linreg(close - avg(avg(highest, lowest), sma(close)), kc_length, 0)`.
- `squeeze_release`: long when squeeze turns off with positive momentum; short when it turns off with negative momentum.
- `momentum_zero_cross`: long when momentum crosses above zero; short when it crosses below zero.
- Entry is the next candle open after signal close.
- Existing positions exit/reverse on the next opposite signal.
- Positions also exit at session end unless overnight holding is enabled.

## Skipped Signals

| Timeframe | Variant | Reason | Count |
| --- | --- | --- | --- |
| 5m | squeeze_release | partial_session_missing_configured_open | 22 |
| 5m | squeeze_release | signal_without_next_session_bar | 4 |
| 5m | momentum_zero_cross | partial_session_missing_configured_open | 22 |
| 5m | momentum_zero_cross | signal_without_next_session_bar | 17 |
| 15m | squeeze_release | partial_session_missing_configured_open | 21 |
| 15m | squeeze_release | signal_without_next_session_bar | 8 |
| 15m | momentum_zero_cross | partial_session_missing_configured_open | 21 |
| 15m | momentum_zero_cross | signal_without_next_session_bar | 26 |
| 30m | squeeze_release | signal_without_next_session_bar | 7 |
| 30m | momentum_zero_cross | signal_without_next_session_bar | 8 |
| 1h | squeeze_release | partial_session_missing_configured_open | 126 |
| 1h | squeeze_release | signal_without_next_session_bar | 5 |
| 1h | momentum_zero_cross | partial_session_missing_configured_open | 126 |
| 1h | momentum_zero_cross | signal_without_next_session_bar | 3 |

## Parameters

- **bb_length**: 20
- **bb_mult**: 2.0
- **kc_length**: 20
- **kc_mult**: 1.5
- **use_true_range**: True
- **capital**: 1000000.0
- **max_allocation_pct**: 100.0
- **cost_multiplier**: 1.0
- **equity_slippage**: 0.2
- **derivatives_slippage**: 5.0
- **commodities_slippage**: 0.2
- **session_start**: 09:15
- **exit_time**: 15:20
- **require_session_open**: True
- **exit_at_session_end**: True
- **variants**: ('squeeze_release', 'momentum_zero_cross')
- **top_trade_count**: 10

## Output Files

- `summary.md`
- `summary.json`
- `timeframe_variant_summary.csv`
