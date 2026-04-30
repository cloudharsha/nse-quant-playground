# Smart Money Concepts [LuxAlgo] Multi-Timeframe Backtest

## Executive Summary

- **generated_at**: 2026-04-30T11:49:52
- **markets_tested**: equity, derivatives, commodities
- **timeframes_tested**: 5m, 15m, 30m, 1h
- **variants_tested**: internal_all, swing_all, combined_all
- **starting_capital**: 1000000.0
- **best_after_brokerage**: 1h / internal_all = 14118.77
- **best_before_brokerage**: 1h / internal_all = 30430.28
- **pnl_note**: Before Brokerage includes configured slippage; After Brokerage subtracts segment-wise brokerage, taxes, and charges.

## Timeframe And Variant Results

| Timeframe | Variant | Files | Events | Trades | Before Brokerage | Brokerage/Charges | After Brokerage | Win % | Max DD % | PF | Sharpe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5m | internal_all | 20 | 1371 | 851 | -932370.64 | 2177397.49 | -3109768.13 | 29.02 | -313.8492 | 0.302 | -3.2194 |
| 5m | swing_all | 20 | 192 | 181 | -209692.84 | 245878.09 | -455570.93 | 34.25 | -45.5571 | 0.3275 | -12.347 |
| 5m | combined_all | 20 | 1563 | 867 | -927330.78 | 2190863.49 | -3118194.27 | 29.41 | -314.9735 | 0.3036 | -3.2692 |
| 15m | internal_all | 20 | 460 | 356 | -194155.29 | 766010.76 | -960166.05 | 35.96 | -96.8075 | 0.3758 | -14.3313 |
| 15m | swing_all | 20 | 37 | 35 | -24726.29 | 56651.66 | -81377.95 | 37.14 | -8.7253 | 0.1959 | -9.0554 |
| 15m | combined_all | 20 | 497 | 363 | -179685.76 | 765184.25 | -944870.01 | 36.64 | -95.3065 | 0.3824 | -14.9363 |
| 30m | internal_all | 20 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 |  |  |
| 30m | swing_all | 20 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 |  |  |
| 30m | combined_all | 20 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 |  |  |
| 1h | internal_all | 20 | 60 | 57 | 30430.28 | 16311.51 | 14118.77 | 54.39 | -2.0679 | 1.2025 | 2.1422 |
| 1h | swing_all | 20 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 |  |  |
| 1h | combined_all | 20 | 60 | 57 | 30430.28 | 16311.51 | 14118.77 | 54.39 | -2.0679 | 1.2025 | 2.1422 |

## Best Variant Per Timeframe

| Timeframe | Best Variant | Trades | Before Brokerage | Brokerage/Charges | After Brokerage | Win % | PF |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5m | swing_all | 181 | -209692.84 | 245878.09 | -455570.93 | 34.25 | 0.3275 |
| 15m | swing_all | 35 | -24726.29 | 56651.66 | -81377.95 | 37.14 | 0.1959 |
| 30m | internal_all | 0 | 0 | 0 | 0 | 0.0 |  |
| 1h | internal_all | 57 | 30430.28 | 16311.51 | 14118.77 | 54.39 | 1.2025 |

## What Was Traded

| Timeframe | Variant | Market | Instrument | Trades | Long | Short | Before Brokerage | Charges | After Brokerage | Win % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5m | combined_all | commodities | CLF | 48 | 26 | 22 | -143956.0 | 394690.6 | -538646.6 | 6.25 |
| 5m | combined_all | commodities | GCF | 52 | 25 | 27 | 469.98 | 815373.47 | -814903.49 | 1.92 |
| 5m | combined_all | commodities | HGF | 49 | 25 | 24 | -447473.45 | 115948.87 | -563422.32 | 0.0 |
| 5m | combined_all | commodities | NGF | 47 | 23 | 24 | -434413.49 | 51949.81 | -486363.3 | 0.0 |
| 5m | combined_all | commodities | SIF | 46 | 23 | 23 | -160099.61 | 542368.73 | -702468.34 | 4.35 |
| 5m | combined_all | derivatives | CNXAUTO | 46 | 23 | 23 | -27320.48 | 25425.12 | -52745.6 | 28.26 |
| 5m | combined_all | derivatives | CNXFMCG | 41 | 25 | 16 | 7561.24 | 23380.97 | -15819.73 | 36.59 |
| 5m | combined_all | derivatives | CNXIT | 38 | 18 | 20 | 19202.17 | 20966.56 | -1764.39 | 39.47 |
| 5m | combined_all | derivatives | NSEBANK | 42 | 25 | 17 | 46829.04 | 23025.21 | 23803.83 | 50.0 |
| 5m | combined_all | derivatives | NSEI | 48 | 24 | 24 | -18780.96 | 27470.33 | -46251.29 | 27.08 |
| 5m | combined_all | equity | BHARTIARTL_NS | 39 | 18 | 21 | 48910.44 | 15093.99 | 33816.45 | 46.15 |
| 5m | combined_all | equity | HDFCBANK_NS | 47 | 23 | 24 | 6338.46 | 17359.02 | -11020.56 | 36.17 |
| 5m | combined_all | equity | ICICIBANK_NS | 36 | 17 | 19 | 55565.36 | 13049.29 | 42516.07 | 50.0 |
| 5m | combined_all | equity | INFY_NS | 44 | 17 | 27 | -21021.5 | 16149.91 | -37171.41 | 36.36 |
| 5m | combined_all | equity | ITC_NS | 34 | 19 | 15 | -7386.63 | 12401.63 | -19788.26 | 32.35 |
| 5m | combined_all | equity | KOTAKBANK_NS | 40 | 19 | 21 | 29101.44 | 14285.14 | 14816.3 | 35.0 |
| 5m | combined_all | equity | LT_NS | 48 | 25 | 23 | -6421.37 | 17509.27 | -23930.64 | 39.58 |
| 5m | combined_all | equity | RELIANCE_NS | 38 | 21 | 17 | 33300.53 | 13913.74 | 19386.79 | 47.37 |
| 5m | combined_all | equity | SBIN_NS | 43 | 22 | 21 | 41935.81 | 15273.75 | 26662.06 | 44.19 |
| 5m | combined_all | equity | TCS_NS | 41 | 22 | 19 | 50328.24 | 15228.08 | 35100.16 | 53.66 |
| 5m | internal_all | commodities | CLF | 46 | 26 | 20 | -138032.11 | 392676.46 | -530708.57 | 6.52 |
| 5m | internal_all | commodities | GCF | 50 | 24 | 26 | 6369.05 | 801219.74 | -794850.69 | 2.0 |
| 5m | internal_all | commodities | HGF | 48 | 23 | 25 | -446284.04 | 115401.54 | -561685.58 | 0.0 |
| 5m | internal_all | commodities | NGF | 47 | 23 | 24 | -440388.85 | 52677.24 | -493066.09 | 0.0 |
| 5m | internal_all | commodities | SIF | 44 | 21 | 23 | -164495.14 | 541646.56 | -706141.7 | 4.55 |
| 5m | internal_all | derivatives | CNXAUTO | 45 | 22 | 23 | -22880.87 | 25160.38 | -48041.25 | 28.89 |
| 5m | internal_all | derivatives | CNXFMCG | 41 | 25 | 16 | 7661.73 | 23685.9 | -16024.17 | 36.59 |
| 5m | internal_all | derivatives | CNXIT | 37 | 17 | 20 | 8918.59 | 20792.75 | -11874.16 | 37.84 |
| 5m | internal_all | derivatives | NSEBANK | 43 | 25 | 18 | 45007.18 | 24286.88 | 20720.3 | 48.84 |
| 5m | internal_all | derivatives | NSEI | 48 | 24 | 24 | -17216.36 | 28064.99 | -45281.35 | 25.0 |
| 5m | internal_all | equity | BHARTIARTL_NS | 39 | 18 | 21 | 43006.47 | 15449.64 | 27556.83 | 46.15 |
| 5m | internal_all | equity | HDFCBANK_NS | 44 | 21 | 23 | 28427.12 | 16775.55 | 11651.57 | 38.64 |
| 5m | internal_all | equity | ICICIBANK_NS | 34 | 15 | 19 | 56125.19 | 12868.13 | 43257.06 | 47.06 |
| 5m | internal_all | equity | INFY_NS | 42 | 17 | 25 | -22045.77 | 15681.59 | -37727.36 | 35.71 |
| 5m | internal_all | equity | ITC_NS | 35 | 20 | 15 | -12808.29 | 13225.85 | -26034.14 | 31.43 |
| 5m | internal_all | equity | KOTAKBANK_NS | 39 | 18 | 21 | 27299.05 | 14535.87 | 12763.18 | 35.9 |
| 5m | internal_all | equity | LT_NS | 48 | 25 | 23 | -7353.18 | 17599.31 | -24952.49 | 39.58 |
| 5m | internal_all | equity | RELIANCE_NS | 39 | 22 | 17 | 37674.67 | 14806.87 | 22867.8 | 46.15 |
| 5m | internal_all | equity | SBIN_NS | 41 | 21 | 20 | 29218.38 | 15198.76 | 14019.62 | 41.46 |
| 5m | internal_all | equity | TCS_NS | 41 | 21 | 20 | 49426.54 | 15643.48 | 33783.06 | 51.22 |
| 5m | swing_all | commodities | CLF | 10 | 6 | 4 | -10179.21 | 21320.17 | -31499.38 | 20.0 |
| 5m | swing_all | commodities | GCF | 9 | 3 | 6 | -7690.54 | 93993.31 | -101683.85 | 0.0 |
| 5m | swing_all | commodities | HGF | 12 | 6 | 6 | -96865.0 | 25605.06 | -122470.06 | 0.0 |
| 5m | swing_all | commodities | NGF | 8 | 4 | 4 | -63468.04 | 7622.72 | -71090.76 | 0.0 |
| 5m | swing_all | commodities | SIF | 11 | 4 | 7 | -16749.17 | 58841.76 | -75590.93 | 0.0 |
| 5m | swing_all | derivatives | CNXAUTO | 7 | 5 | 2 | -22566.67 | 2723.86 | -25290.53 | 0.0 |
| 5m | swing_all | derivatives | CNXFMCG | 6 | 4 | 2 | 14894.86 | 2605.79 | 12289.07 | 66.67 |
| 5m | swing_all | derivatives | CNXIT | 9 | 5 | 4 | -5797.45 | 3613.53 | -9410.98 | 44.44 |
| 5m | swing_all | derivatives | NSEBANK | 9 | 6 | 3 | -2649.45 | 2964.95 | -5614.4 | 55.56 |
| 5m | swing_all | derivatives | NSEI | 9 | 6 | 3 | -141.03 | 4184.32 | -4325.35 | 44.44 |
| 5m | swing_all | equity | BHARTIARTL_NS | 8 | 3 | 5 | -10104.0 | 2122.66 | -12226.66 | 25.0 |
| 5m | swing_all | equity | HDFCBANK_NS | 11 | 6 | 5 | -22696.75 | 2725.91 | -25422.66 | 36.36 |
| 5m | swing_all | equity | ICICIBANK_NS | 9 | 5 | 4 | 8707.69 | 2247.25 | 6460.44 | 66.67 |
| 5m | swing_all | equity | INFY_NS | 8 | 2 | 6 | -9487.47 | 1909.42 | -11396.89 | 50.0 |
| 5m | swing_all | equity | ITC_NS | 9 | 5 | 4 | 14940.7 | 2876.77 | 12063.93 | 44.44 |
| 5m | swing_all | equity | KOTAKBANK_NS | 11 | 8 | 3 | -16247.66 | 2405.46 | -18653.12 | 36.36 |
| 5m | swing_all | equity | LT_NS | 7 | 4 | 3 | -13714.73 | 1504.14 | -15218.87 | 28.57 |
| 5m | swing_all | equity | RELIANCE_NS | 8 | 4 | 4 | 18385.27 | 1954.25 | 16431.02 | 75.0 |
| 5m | swing_all | equity | SBIN_NS | 11 | 5 | 6 | -3463.55 | 2693.0 | -6156.55 | 36.36 |
| 5m | swing_all | equity | TCS_NS | 9 | 5 | 4 | 35199.36 | 1963.76 | 33235.6 | 77.78 |
| 15m | combined_all | commodities | CLF | 20 | 10 | 10 | 3703.01 | 102255.09 | -98552.08 | 15.0 |
| 15m | combined_all | commodities | GCF | 24 | 10 | 14 | 31173.63 | 340779.5 | -309605.87 | 4.17 |
| 15m | combined_all | commodities | HGF | 21 | 11 | 10 | -176971.01 | 47079.06 | -224050.07 | 0.0 |
| 15m | combined_all | commodities | NGF | 23 | 14 | 9 | -209713.64 | 24494.57 | -234208.21 | 0.0 |
| 15m | combined_all | commodities | SIF | 22 | 10 | 12 | -25103.62 | 153296.89 | -178400.51 | 9.09 |
| 15m | combined_all | derivatives | CNXAUTO | 18 | 11 | 7 | -9003.66 | 8998.2 | -18001.86 | 38.89 |
| 15m | combined_all | derivatives | CNXFMCG | 13 | 9 | 4 | 41137.28 | 6961.86 | 34175.42 | 76.92 |
| 15m | combined_all | derivatives | CNXIT | 17 | 9 | 8 | 19836.53 | 7770.14 | 12066.39 | 41.18 |
| 15m | combined_all | derivatives | NSEBANK | 19 | 11 | 8 | 2016.66 | 9720.12 | -7703.46 | 52.63 |
| 15m | combined_all | derivatives | NSEI | 14 | 9 | 5 | 12541.18 | 8008.46 | 4532.72 | 50.0 |
| 15m | combined_all | equity | BHARTIARTL_NS | 17 | 9 | 8 | 14111.01 | 6022.65 | 8088.36 | 52.94 |
| 15m | combined_all | equity | HDFCBANK_NS | 21 | 10 | 11 | -5244.13 | 7175.41 | -12419.54 | 42.86 |
| 15m | combined_all | equity | ICICIBANK_NS | 17 | 7 | 10 | 41463.09 | 5834.71 | 35628.38 | 64.71 |
| 15m | combined_all | equity | INFY_NS | 15 | 6 | 9 | -2639.39 | 4213.06 | -6852.45 | 33.33 |
| 15m | combined_all | equity | ITC_NS | 18 | 13 | 5 | -4476.56 | 5833.89 | -10310.45 | 38.89 |
| 15m | combined_all | equity | KOTAKBANK_NS | 12 | 8 | 4 | 8985.47 | 3554.02 | 5431.45 | 50.0 |
| 15m | combined_all | equity | LT_NS | 21 | 10 | 11 | 36961.77 | 6775.9 | 30185.87 | 52.38 |
| 15m | combined_all | equity | RELIANCE_NS | 17 | 8 | 9 | 20528.48 | 5738.44 | 14790.04 | 52.94 |
| 15m | combined_all | equity | SBIN_NS | 17 | 10 | 7 | 20012.26 | 5460.43 | 14551.83 | 58.82 |
| 15m | combined_all | equity | TCS_NS | 17 | 11 | 6 | 995.88 | 5211.85 | -4215.97 | 52.94 |
| 15m | internal_all | commodities | CLF | 19 | 10 | 9 | 4193.15 | 103143.41 | -98950.26 | 15.79 |
| 15m | internal_all | commodities | GCF | 23 | 9 | 14 | 34170.33 | 338185.8 | -304015.47 | 4.35 |
| 15m | internal_all | commodities | HGF | 21 | 11 | 10 | -177061.28 | 47102.46 | -224163.74 | 0.0 |
| 15m | internal_all | commodities | NGF | 23 | 14 | 9 | -211582.9 | 24692.75 | -236275.65 | 0.0 |
| 15m | internal_all | commodities | SIF | 22 | 10 | 12 | -25518.83 | 156042.47 | -181561.3 | 9.09 |
| 15m | internal_all | derivatives | CNXAUTO | 17 | 11 | 6 | -13018.42 | 8731.51 | -21749.93 | 35.29 |
| 15m | internal_all | derivatives | CNXFMCG | 13 | 9 | 4 | 41137.28 | 6961.86 | 34175.42 | 76.92 |
| 15m | internal_all | derivatives | CNXIT | 16 | 8 | 8 | 21128.33 | 7615.07 | 13513.26 | 43.75 |
| 15m | internal_all | derivatives | NSEBANK | 19 | 11 | 8 | 2016.66 | 9720.12 | -7703.46 | 52.63 |
| 15m | internal_all | derivatives | NSEI | 14 | 9 | 5 | 12541.18 | 8008.46 | 4532.72 | 50.0 |
| 15m | internal_all | equity | BHARTIARTL_NS | 17 | 9 | 8 | 7955.55 | 6276.63 | 1678.92 | 47.06 |
| 15m | internal_all | equity | HDFCBANK_NS | 21 | 10 | 11 | -5244.13 | 7175.41 | -12419.54 | 42.86 |
| 15m | internal_all | equity | ICICIBANK_NS | 17 | 7 | 10 | 41463.09 | 5834.71 | 35628.38 | 64.71 |
| 15m | internal_all | equity | INFY_NS | 15 | 6 | 9 | -2639.39 | 4213.06 | -6852.45 | 33.33 |
| 15m | internal_all | equity | ITC_NS | 17 | 13 | 4 | -906.81 | 5675.7 | -6582.51 | 41.18 |
| 15m | internal_all | equity | KOTAKBANK_NS | 12 | 8 | 4 | 8985.47 | 3554.02 | 5431.45 | 50.0 |
| 15m | internal_all | equity | LT_NS | 21 | 10 | 11 | 37595.37 | 6827.88 | 30767.49 | 52.38 |
| 15m | internal_all | equity | RELIANCE_NS | 16 | 7 | 9 | 20031.88 | 5598.82 | 14433.06 | 50.0 |
| 15m | internal_all | equity | SBIN_NS | 16 | 9 | 7 | 19247.25 | 5313.41 | 13933.84 | 56.25 |
| 15m | internal_all | equity | TCS_NS | 17 | 11 | 6 | -8649.07 | 5337.21 | -13986.28 | 47.06 |
| 15m | swing_all | commodities | CLF | 2 | 1 | 1 | 131.54 | 3791.87 | -3660.33 | 0.0 |
| 15m | swing_all | commodities | GCF | 5 | 3 | 2 | -717.32 | 34343.79 | -35061.11 | 0.0 |
| 15m | swing_all | commodities | HGF | 3 | 2 | 1 | -21531.32 | 5612.78 | -27144.1 | 0.0 |
| 15m | swing_all | commodities | NGF | 1 | 0 | 1 | -7358.4 | 930.37 | -8288.77 | 0.0 |
| 15m | swing_all | commodities | SIF | 3 | 2 | 1 | -4242.66 | 7820.41 | -12063.07 | 0.0 |
| 15m | swing_all | derivatives | CNXAUTO | 2 | 1 | 1 | 1846.83 | 600.07 | 1246.76 | 50.0 |
| 15m | swing_all | derivatives | CNXFMCG | 2 | 2 | 0 | 2773.79 | 766.86 | 2006.93 | 100.0 |
| 15m | swing_all | derivatives | CNXIT | 2 | 1 | 1 | -2259.05 | 288.5 | -2547.55 | 0.0 |
| 15m | swing_all | equity | BHARTIARTL_NS | 2 | 1 | 1 | 2048.92 | 321.01 | 1727.91 | 100.0 |
| 15m | swing_all | equity | HDFCBANK_NS | 1 | 0 | 1 | 964.6 | 148.53 | 816.07 | 100.0 |
| 15m | swing_all | equity | INFY_NS | 1 | 0 | 1 | -884.51 | 112.43 | -996.94 | 0.0 |
| 15m | swing_all | equity | ITC_NS | 3 | 2 | 1 | -477.01 | 573.84 | -1050.85 | 33.33 |
| 15m | swing_all | equity | KOTAKBANK_NS | 2 | 1 | 1 | -905.46 | 329.99 | -1235.45 | 50.0 |
| 15m | swing_all | equity | LT_NS | 1 | 1 | 0 | 1020.8 | 130.95 | 889.85 | 100.0 |
| 15m | swing_all | equity | RELIANCE_NS | 1 | 1 | 0 | 496.6 | 139.62 | 356.98 | 100.0 |
| 15m | swing_all | equity | SBIN_NS | 2 | 2 | 0 | -1613.05 | 270.02 | -1883.07 | 50.0 |
| 15m | swing_all | equity | TCS_NS | 2 | 1 | 1 | 5979.41 | 470.62 | 5508.79 | 100.0 |
| 1h | combined_all | derivatives | CNXAUTO | 3 | 2 | 1 | -3868.63 | 989.51 | -4858.14 | 33.33 |
| 1h | combined_all | derivatives | CNXFMCG | 4 | 3 | 1 | 5873.44 | 1554.25 | 4319.19 | 75.0 |
| 1h | combined_all | derivatives | CNXIT | 3 | 2 | 1 | -2358.73 | 919.78 | -3278.51 | 66.67 |
| 1h | combined_all | derivatives | NSEBANK | 5 | 2 | 3 | 8218.61 | 1729.62 | 6488.99 | 60.0 |
| 1h | combined_all | derivatives | NSEI | 6 | 4 | 2 | -6047.04 | 2845.27 | -8892.31 | 33.33 |
| 1h | combined_all | equity | BHARTIARTL_NS | 5 | 2 | 3 | 4767.3 | 1231.75 | 3535.55 | 40.0 |
| 1h | combined_all | equity | HDFCBANK_NS | 6 | 3 | 3 | -5403.11 | 1342.24 | -6745.35 | 50.0 |
| 1h | combined_all | equity | ICICIBANK_NS | 3 | 1 | 2 | 4090.26 | 889.76 | 3200.5 | 66.67 |
| 1h | combined_all | equity | INFY_NS | 2 | 0 | 2 | 441.6 | 319.89 | 121.71 | 50.0 |
| 1h | combined_all | equity | ITC_NS | 3 | 2 | 1 | 8108.49 | 773.2 | 7335.29 | 66.67 |
| 1h | combined_all | equity | KOTAKBANK_NS | 2 | 1 | 1 | -7801.11 | 499.18 | -8300.29 | 0.0 |
| 1h | combined_all | equity | LT_NS | 4 | 2 | 2 | 1227.54 | 852.81 | 374.73 | 50.0 |
| 1h | combined_all | equity | RELIANCE_NS | 3 | 1 | 2 | 941.11 | 794.28 | 146.83 | 66.67 |
| 1h | combined_all | equity | SBIN_NS | 3 | 2 | 1 | 10454.87 | 637.44 | 9817.43 | 33.33 |
| 1h | combined_all | equity | TCS_NS | 5 | 2 | 3 | 11785.68 | 932.53 | 10853.15 | 100.0 |
| 1h | internal_all | derivatives | CNXAUTO | 3 | 2 | 1 | -3868.63 | 989.51 | -4858.14 | 33.33 |
| 1h | internal_all | derivatives | CNXFMCG | 4 | 3 | 1 | 5873.44 | 1554.25 | 4319.19 | 75.0 |
| 1h | internal_all | derivatives | CNXIT | 3 | 2 | 1 | -2358.73 | 919.78 | -3278.51 | 66.67 |
| 1h | internal_all | derivatives | NSEBANK | 5 | 2 | 3 | 8218.61 | 1729.62 | 6488.99 | 60.0 |
| 1h | internal_all | derivatives | NSEI | 6 | 4 | 2 | -6047.04 | 2845.27 | -8892.31 | 33.33 |
| 1h | internal_all | equity | BHARTIARTL_NS | 5 | 2 | 3 | 4767.3 | 1231.75 | 3535.55 | 40.0 |
| 1h | internal_all | equity | HDFCBANK_NS | 6 | 3 | 3 | -5403.11 | 1342.24 | -6745.35 | 50.0 |
| 1h | internal_all | equity | ICICIBANK_NS | 3 | 1 | 2 | 4090.26 | 889.76 | 3200.5 | 66.67 |
| 1h | internal_all | equity | INFY_NS | 2 | 0 | 2 | 441.6 | 319.89 | 121.71 | 50.0 |
| 1h | internal_all | equity | ITC_NS | 3 | 2 | 1 | 8108.49 | 773.2 | 7335.29 | 66.67 |
| 1h | internal_all | equity | KOTAKBANK_NS | 2 | 1 | 1 | -7801.11 | 499.18 | -8300.29 | 0.0 |
| 1h | internal_all | equity | LT_NS | 4 | 2 | 2 | 1227.54 | 852.81 | 374.73 | 50.0 |
| 1h | internal_all | equity | RELIANCE_NS | 3 | 1 | 2 | 941.11 | 794.28 | 146.83 | 66.67 |
| 1h | internal_all | equity | SBIN_NS | 3 | 2 | 1 | 10454.87 | 637.44 | 9817.43 | 33.33 |
| 1h | internal_all | equity | TCS_NS | 5 | 2 | 3 | 11785.68 | 932.53 | 10853.15 | 100.0 |

## Brokerage And Charges

| Timeframe | Variant | Segment | Trades | Turnover | Brokerage | STT | CTT | Exchange | GST | SEBI | Stamp | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5m | combined_all | Commodity futures MCX | 242 | 222112961.11 | 9502.18 | 0.0 | 1110359.63 | 466437.17 | 89667.17 | 22211.21 | 222153.98 | 1920331.48 |
| 5m | combined_all | F&O futures NSE | 215 | 389278542.17 | 8600.0 | 97363.58 | 0.0 | 7123.84 | 2900.36 | 389.29 | 3891.05 | 120268.19 |
| 5m | combined_all | Intraday equity NSE | 410 | 737763733.89 | 16400.0 | 92252.36 | 0.0 | 22649.33 | 7161.68 | 737.8 | 11062.65 | 150263.82 |
| 5m | internal_all | Commodity futures MCX | 235 | 220179895.6 | 9262.94 | 0.0 | 1100930.5 | 462377.77 | 88858.58 | 22017.9 | 220173.68 | 1903621.54 |
| 5m | internal_all | F&O futures NSE | 214 | 395541422.26 | 8560.0 | 98928.23 | 0.0 | 7238.44 | 2914.93 | 395.57 | 3953.73 | 121990.9 |
| 5m | internal_all | Intraday equity NSE | 402 | 748466424.6 | 16080.0 | 93590.31 | 0.0 | 22977.88 | 7165.19 | 748.51 | 11223.13 | 151785.05 |
| 5m | swing_all | Commodity futures MCX | 50 | 23861217.0 | 1918.29 | 0.0 | 119316.58 | 50108.55 | 9794.37 | 2386.12 | 23859.11 | 207383.02 |
| 5m | swing_all | F&O futures NSE | 40 | 50213262.4 | 1600.0 | 12558.95 | 0.0 | 918.89 | 462.42 | 50.22 | 501.91 | 16092.45 |
| 5m | swing_all | Intraday equity NSE | 91 | 102056035.93 | 3640.0 | 12759.32 | 0.0 | 3133.11 | 1237.54 | 102.0 | 1530.57 | 22402.62 |
| 15m | combined_all | Commodity futures MCX | 110 | 77134885.53 | 4305.56 | 0.0 | 385390.79 | 161983.24 | 31320.41 | 7713.5 | 77191.6 | 667905.11 |
| 15m | combined_all | F&O futures NSE | 81 | 133042865.8 | 3240.0 | 33275.87 | 0.0 | 2434.65 | 1045.38 | 133.02 | 1329.79 | 41458.78 |
| 15m | combined_all | Intraday equity NSE | 172 | 268826325.13 | 6880.0 | 33615.27 | 0.0 | 8253.01 | 2772.36 | 268.86 | 4030.99 | 55820.36 |
| 15m | internal_all | Commodity futures MCX | 108 | 77288468.54 | 4231.95 | 0.0 | 386194.23 | 162305.77 | 31367.98 | 7728.86 | 77338.07 | 669166.89 |
| 15m | internal_all | F&O futures NSE | 79 | 131880712.77 | 3160.0 | 32986.66 | 0.0 | 2413.38 | 1026.94 | 131.86 | 1318.11 | 41037.02 |
| 15m | internal_all | Intraday equity NSE | 169 | 269560526.65 | 6760.0 | 33704.61 | 0.0 | 8275.55 | 2754.96 | 269.6 | 4042.29 | 55806.85 |
| 15m | swing_all | Commodity futures MCX | 14 | 6031980.36 | 550.2 | 0.0 | 30158.75 | 12667.15 | 2487.7 | 603.2 | 6032.22 | 52499.22 |
| 15m | swing_all | F&O futures NSE | 6 | 4855891.45 | 240.0 | 1213.05 | 0.0 | 88.86 | 60.07 | 4.84 | 48.6 | 1655.43 |
| 15m | swing_all | Intraday equity NSE | 15 | 10079110.99 | 600.0 | 1260.91 | 0.0 | 309.42 | 165.51 | 10.07 | 151.08 | 2497.01 |
| 1h | combined_all | F&O futures NSE | 21 | 24946232.62 | 840.0 | 6229.35 | 0.0 | 456.48 | 237.87 | 24.95 | 249.75 | 8038.43 |
| 1h | combined_all | Intraday equity NSE | 36 | 37062306.23 | 1440.0 | 4631.42 | 0.0 | 1137.81 | 470.68 | 37.04 | 556.09 | 8273.08 |
| 1h | internal_all | F&O futures NSE | 21 | 24946232.62 | 840.0 | 6229.35 | 0.0 | 456.48 | 237.87 | 24.95 | 249.75 | 8038.43 |
| 1h | internal_all | Intraday equity NSE | 36 | 37062306.23 | 1440.0 | 4631.42 | 0.0 | 1137.81 | 470.68 | 37.04 | 556.09 | 8273.08 |

## Direction And Exit Summary

| Timeframe | Variant | Direction | Exit | Trades | Before Brokerage | Charges | After Brokerage |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5m | combined_all | LONG | OPPOSITE_STRUCTURE | 154 | -324985.81 | 311867.93 | -636853.74 |
| 5m | combined_all | LONG | SESSION_END | 158 | 47259.86 | 403869.29 | -356609.43 |
| 5m | combined_all | LONG | STOP_LOSS | 82 | -495723.33 | 321509.82 | -817233.15 |
| 5m | combined_all | LONG | TARGET | 46 | 504682.84 | 64723.83 | 439959.01 |
| 5m | combined_all | SHORT | OPPOSITE_STRUCTURE | 172 | -419008.91 | 401607.22 | -820616.13 |
| 5m | combined_all | SHORT | SESSION_END | 149 | 27102.65 | 437756.45 | -410653.8 |
| 5m | combined_all | SHORT | STOP_LOSS | 80 | -491893.59 | 214649.8 | -706543.39 |
| 5m | combined_all | SHORT | TARGET | 26 | 225235.51 | 34879.15 | 190356.36 |
| 5m | internal_all | LONG | OPPOSITE_STRUCTURE | 138 | -272287.56 | 299928.44 | -572216.0 |
| 5m | internal_all | LONG | SESSION_END | 156 | 30092.87 | 405743.79 | -375650.92 |
| 5m | internal_all | LONG | STOP_LOSS | 87 | -521701.98 | 310695.08 | -832397.06 |
| 5m | internal_all | LONG | TARGET | 47 | 514435.76 | 65205.98 | 449229.78 |
| 5m | internal_all | SHORT | OPPOSITE_STRUCTURE | 161 | -422124.2 | 380809.38 | -802933.58 |
| 5m | internal_all | SHORT | SESSION_END | 144 | 8074.85 | 444949.52 | -436874.67 |
| 5m | internal_all | SHORT | STOP_LOSS | 87 | -540764.52 | 232804.47 | -773568.99 |
| 5m | internal_all | SHORT | TARGET | 31 | 271904.14 | 37260.83 | 234643.31 |
| 5m | swing_all | LONG | SESSION_END | 91 | -62929.56 | 87189.98 | -150119.54 |
| 5m | swing_all | LONG | STOP_LOSS | 4 | -39102.38 | 1752.1 | -40854.48 |
| 5m | swing_all | LONG | TARGET | 1 | 18762.24 | 277.06 | 18485.18 |
| 5m | swing_all | SHORT | SESSION_END | 76 | -37366.23 | 140921.88 | -178288.11 |
| 5m | swing_all | SHORT | STOP_LOSS | 9 | -89056.91 | 15737.07 | -104793.98 |
| 15m | combined_all | LONG | OPPOSITE_STRUCTURE | 21 | -78567.36 | 42776.87 | -121344.23 |
| 15m | combined_all | LONG | SESSION_END | 151 | 45696.93 | 257419.82 | -211722.89 |
| 15m | combined_all | LONG | STOP_LOSS | 16 | -129201.36 | 37443.56 | -166644.92 |
| 15m | combined_all | LONG | TARGET | 8 | 121784.63 | 11386.53 | 110398.1 |
| 15m | combined_all | SHORT | OPPOSITE_STRUCTURE | 13 | -58102.74 | 33752.93 | -91855.67 |
| 15m | combined_all | SHORT | SESSION_END | 133 | -15479.25 | 335668.5 | -351147.75 |
| 15m | combined_all | SHORT | STOP_LOSS | 16 | -130604.07 | 14882.08 | -145486.15 |
| 15m | combined_all | SHORT | TARGET | 5 | 64787.46 | 31853.96 | 32933.5 |
| 15m | internal_all | LONG | OPPOSITE_STRUCTURE | 20 | -75878.58 | 38340.68 | -114219.26 |
| 15m | internal_all | LONG | SESSION_END | 147 | 38992.89 | 260623.35 | -221630.46 |
| 15m | internal_all | LONG | STOP_LOSS | 17 | -136004.31 | 37842.79 | -173847.1 |
| 15m | internal_all | LONG | TARGET | 8 | 121784.63 | 11386.53 | 110398.1 |
| 15m | internal_all | SHORT | OPPOSITE_STRUCTURE | 12 | -54742.78 | 33478.07 | -88220.85 |
| 15m | internal_all | SHORT | SESSION_END | 131 | -22490.53 | 337603.3 | -360093.83 |
| 15m | internal_all | SHORT | STOP_LOSS | 16 | -130604.07 | 14882.08 | -145486.15 |
| 15m | internal_all | SHORT | TARGET | 5 | 64787.46 | 31853.96 | 32933.5 |
| 15m | swing_all | LONG | SESSION_END | 21 | -10224.98 | 37077.74 | -47302.72 |
| 15m | swing_all | SHORT | SESSION_END | 14 | -14501.31 | 19573.92 | -34075.23 |
| 1h | combined_all | LONG | SESSION_END | 27 | 11372.89 | 7436.24 | 3936.65 |
| 1h | combined_all | LONG | STOP_LOSS | 2 | -16003.65 | 964.61 | -16968.26 |
| 1h | combined_all | SHORT | SESSION_END | 28 | 35061.04 | 7910.66 | 27150.38 |
| 1h | internal_all | LONG | SESSION_END | 27 | 11372.89 | 7436.24 | 3936.65 |
| 1h | internal_all | LONG | STOP_LOSS | 2 | -16003.65 | 964.61 | -16968.26 |
| 1h | internal_all | SHORT | SESSION_END | 28 | 35061.04 | 7910.66 | 27150.38 |

## Best And Worst Trades

| Rank Type | Rank | Timeframe | Variant | Market | Instrument | Date | Direction | Exit | Before Brokerage | Charges | After Brokerage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BEST | 1 | 5m | internal_all | equity | TCS_NS | 2026-04-24 | SHORT | TARGET | 19754.35 | 392.21 | 19362.14 |
| BEST | 2 | 5m | internal_all | equity | RELIANCE_NS | 2026-04-27 | LONG | TARGET | 19369.62 | 407.13 | 18962.49 |
| BEST | 3 | 5m | combined_all | equity | RELIANCE_NS | 2026-04-27 | LONG | TARGET | 19369.62 | 407.13 | 18962.49 |
| BEST | 4 | 5m | internal_all | equity | HDFCBANK_NS | 2026-04-02 | LONG | TARGET | 19186.92 | 405.75 | 18781.17 |
| BEST | 5 | 5m | combined_all | equity | HDFCBANK_NS | 2026-04-02 | LONG | TARGET | 19186.92 | 405.75 | 18781.17 |
| BEST | 6 | 15m | internal_all | equity | HDFCBANK_NS | 2026-04-02 | LONG | TARGET | 19186.92 | 405.75 | 18781.17 |
| BEST | 7 | 15m | combined_all | equity | HDFCBANK_NS | 2026-04-02 | LONG | TARGET | 19186.92 | 405.75 | 18781.17 |
| BEST | 8 | 5m | internal_all | derivatives | CNXIT | 2026-04-02 | LONG | TARGET | 19192.36 | 594.72 | 18597.64 |
| BEST | 9 | 5m | combined_all | derivatives | CNXIT | 2026-04-02 | LONG | TARGET | 19192.36 | 594.72 | 18597.64 |
| BEST | 10 | 5m | swing_all | equity | ITC_NS | 2026-04-29 | LONG | TARGET | 18762.24 | 277.06 | 18485.18 |
| WORST | 1 | 5m | internal_all | commodities | SIF | 2026-04-07 | SHORT | STOP_LOSS | -9101.67 | 17353.55 | -26455.22 |
| WORST | 2 | 5m | combined_all | commodities | SIF | 2026-04-07 | SHORT | STOP_LOSS | -9101.67 | 17353.55 | -26455.22 |
| WORST | 3 | 5m | internal_all | commodities | CLF | 2026-04-28 | SHORT | STOP_LOSS | -9999.5 | 16441.95 | -26441.45 |
| WORST | 4 | 5m | combined_all | commodities | CLF | 2026-04-28 | SHORT | STOP_LOSS | -9999.5 | 16441.95 | -26441.45 |
| WORST | 5 | 5m | internal_all | commodities | SIF | 2026-04-24 | SHORT | STOP_LOSS | -9999.38 | 16003.31 | -26002.69 |
| WORST | 6 | 5m | combined_all | commodities | SIF | 2026-04-24 | SHORT | STOP_LOSS | -9999.38 | 16003.31 | -26002.69 |
| WORST | 7 | 5m | internal_all | commodities | CLF | 2026-04-15 | LONG | STOP_LOSS | -9999.37 | 15664.58 | -25663.95 |
| WORST | 8 | 5m | combined_all | commodities | CLF | 2026-04-15 | LONG | STOP_LOSS | -9999.37 | 15664.58 | -25663.95 |
| WORST | 9 | 5m | internal_all | commodities | SIF | 2026-04-20 | LONG | STOP_LOSS | -8236.16 | 17134.3 | -25370.46 |
| WORST | 10 | 5m | combined_all | commodities | SIF | 2026-04-20 | LONG | STOP_LOSS | -8236.16 | 17134.3 | -25370.46 |

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

## Backtest Rules

- Structure events are based on the LuxAlgo SMC BOS/CHoCH alert logic.
- Internal structure uses the configured internal leg length; swing structure uses the configured swing leg length.
- Entry happens at the next candle open after a signal candle closes.
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

## Skipped Signals

| Timeframe | Variant | Reason | Count |
| --- | --- | --- | --- |
| 5m | internal_all | signal_without_next_session_bar | 4 |
| 5m | swing_all | signal_without_next_session_bar | 2 |
| 5m | combined_all | signal_without_next_session_bar | 5 |
| 15m | internal_all | signal_without_next_session_bar | 7 |
| 15m | swing_all | signal_without_next_session_bar | 2 |
| 15m | combined_all | signal_without_next_session_bar | 7 |
| 1h | internal_all | signal_without_next_session_bar | 3 |
| 1h | combined_all | signal_without_next_session_bar | 3 |

## Parameters

- **internal_length**: 5
- **swing_length**: 50
- **atr_period**: 14
- **order_block_atr_period**: 200
- **atr_multiplier**: 1.5
- **stop_buffer_pct**: 0.02
- **risk_reward**: 2.0
- **capital**: 1000000.0
- **risk_per_trade_pct**: 1.0
- **max_allocation_pct**: 100.0
- **cost_multiplier**: 1.0
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

- `summary.md`
- `summary.json`
- `timeframe_variant_summary.csv`
