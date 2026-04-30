# Renko Candles Overlay Multi-Timeframe Backtest

## Executive Summary

- **generated_at**: 2026-04-30T12:55:04
- **markets_tested**: derivatives, equity, commodities, usdinr
- **timeframes_tested**: 5m, 15m, 30m, 1h
- **modes_tested**: ATR/2
- **starting_capital**: 1000000.0
- **best_after_brokerage**: 1h / ATR/2 = -68300.63
- **best_before_brokerage**: 1h / ATR/2 = -28352.93
- **pnl_note**: Before Brokerage includes configured slippage; After Brokerage subtracts segment-wise brokerage, taxes, and charges.

## Timeframe And Mode Results

| Timeframe | Mode | Files | Signals | Trades | Before Brokerage | Brokerage/Charges | After Brokerage | Win % | Max DD % | PF | Sharpe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5m | ATR/2 | 21 | 2453 | 2425 | -13789967.47 | 9617748.92 | -23407716.39 | 22.02 | -2342.8674 | 0.0803 | -2.3142 |
| 15m | ATR/2 | 21 | 765 | 744 | -8179149.83 | 3487058.35 | -11666208.17 | 27.02 | -1170.9843 | 0.0847 | 3.8242 |
| 30m | ATR/2 | 21 | 358 | 335 | -5089001.04 | 1722015.78 | -6811016.82 | 27.46 | -681.1017 | 0.0638 | -1.307 |
| 1h | ATR/2 | 21 | 96 | 86 | -28352.93 | 39947.7 | -68300.63 | 40.7 | -9.1303 | 0.709 | -2.9353 |

## Best Mode Per Timeframe

| Timeframe | Best Mode | Trades | Before Brokerage | Brokerage/Charges | After Brokerage | Win % | PF |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5m | ATR/2 | 2425 | -13789967.47 | 9617748.92 | -23407716.39 | 22.02 | 0.0803 |
| 15m | ATR/2 | 744 | -8179149.83 | 3487058.35 | -11666208.17 | 27.02 | 0.0847 |
| 30m | ATR/2 | 335 | -5089001.04 | 1722015.78 | -6811016.82 | 27.46 | 0.0638 |
| 1h | ATR/2 | 86 | -28352.93 | 39947.7 | -68300.63 | 40.7 | 0.709 |

## What Was Traded

| Timeframe | Mode | Market | Instrument | Trades | Long | Short | Before Brokerage | Charges | After Brokerage | Win % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5m | ATR/2 | commodities | CLF | 135 | 67 | 68 | -558851.78 | 2327121.51 | -2885973.29 | 5.93 |
| 5m | ATR/2 | commodities | GCF | 139 | 70 | 69 | -52201.81 | 2390306.31 | -2442508.12 | 0.0 |
| 5m | ATR/2 | commodities | HGF | 46 | 23 | 23 | -3158337.88 | 794658.68 | -3952996.56 | 0.0 |
| 5m | ATR/2 | commodities | NGF | 55 | 27 | 28 | -8206812.68 | 955963.27 | -9162775.95 | 0.0 |
| 5m | ATR/2 | commodities | SIF | 131 | 66 | 65 | -683731.72 | 2258882.22 | -2942613.94 | 0.76 |
| 5m | ATR/2 | derivatives | CNXAUTO | 115 | 57 | 58 | -45196.72 | 69578.31 | -114775.03 | 26.96 |
| 5m | ATR/2 | derivatives | CNXFMCG | 114 | 57 | 57 | 2189.48 | 68104.71 | -65915.23 | 27.19 |
| 5m | ATR/2 | derivatives | CNXIT | 113 | 56 | 57 | -18880.76 | 68143.37 | -87024.13 | 28.32 |
| 5m | ATR/2 | derivatives | NSEBANK | 120 | 60 | 60 | -9196.85 | 71397.34 | -80594.19 | 28.33 |
| 5m | ATR/2 | derivatives | NSEI | 138 | 69 | 69 | -83708.03 | 83581.38 | -167289.41 | 21.01 |
| 5m | ATR/2 | equity | BHARTIARTL_NS | 134 | 67 | 67 | -59773.61 | 53840.07 | -113613.68 | 31.34 |
| 5m | ATR/2 | equity | HDFCBANK_NS | 122 | 60 | 62 | -67590.23 | 49035.43 | -116625.66 | 28.69 |
| 5m | ATR/2 | equity | ICICIBANK_NS | 136 | 69 | 67 | -75316.49 | 54642.77 | -129959.26 | 27.94 |
| 5m | ATR/2 | equity | INFY_NS | 122 | 61 | 61 | -65161.01 | 49018.39 | -114179.4 | 27.87 |
| 5m | ATR/2 | equity | ITC_NS | 124 | 63 | 61 | -150834.56 | 49849.13 | -200683.69 | 18.55 |
| 5m | ATR/2 | equity | KOTAKBANK_NS | 99 | 50 | 49 | -71363.52 | 39804.35 | -111167.87 | 31.31 |
| 5m | ATR/2 | equity | LT_NS | 137 | 68 | 69 | -35361.61 | 54997.21 | -90358.82 | 34.31 |
| 5m | ATR/2 | equity | RELIANCE_NS | 123 | 62 | 61 | -3317.7 | 49428.93 | -52746.63 | 31.71 |
| 5m | ATR/2 | equity | SBIN_NS | 109 | 54 | 55 | -6588.36 | 43805.94 | -50394.3 | 33.94 |
| 5m | ATR/2 | equity | TCS_NS | 119 | 59 | 60 | -31691.94 | 47803.1 | -79495.04 | 35.29 |
| 5m | ATR/2 | usdinr | USDINR | 94 | 47 | 47 | -408239.69 | 37786.5 | -446026.19 | 0.0 |
| 15m | ATR/2 | commodities | CLF | 40 | 20 | 20 | -178577.01 | 688953.57 | -867530.58 | 12.5 |
| 15m | ATR/2 | commodities | GCF | 38 | 18 | 20 | 35576.59 | 653614.43 | -618037.84 | 2.63 |
| 15m | ATR/2 | commodities | HGF | 36 | 18 | 18 | -2441606.46 | 622111.5 | -3063717.96 | 0.0 |
| 15m | ATR/2 | commodities | NGF | 35 | 17 | 18 | -5185299.24 | 608654.61 | -5793953.85 | 0.0 |
| 15m | ATR/2 | commodities | SIF | 38 | 19 | 19 | -220820.85 | 655537.19 | -876358.04 | 2.63 |
| 15m | ATR/2 | derivatives | CNXAUTO | 36 | 17 | 19 | -15289.66 | 21769.05 | -37058.71 | 36.11 |
| 15m | ATR/2 | derivatives | CNXFMCG | 37 | 19 | 18 | -1030.84 | 22031.89 | -23062.73 | 37.84 |
| 15m | ATR/2 | derivatives | CNXIT | 37 | 18 | 19 | -19169.31 | 22357.47 | -41526.77 | 37.84 |
| 15m | ATR/2 | derivatives | NSEBANK | 29 | 14 | 15 | 27412.57 | 17252.13 | 10160.44 | 41.38 |
| 15m | ATR/2 | derivatives | NSEI | 33 | 16 | 17 | -23996.86 | 20010.87 | -44007.73 | 21.21 |
| 15m | ATR/2 | equity | BHARTIARTL_NS | 36 | 18 | 18 | -60814.75 | 14471.16 | -75285.91 | 33.33 |
| 15m | ATR/2 | equity | HDFCBANK_NS | 43 | 21 | 22 | -14465.5 | 17288.64 | -31754.14 | 32.56 |
| 15m | ATR/2 | equity | ICICIBANK_NS | 31 | 15 | 16 | 71644.61 | 12473.56 | 59171.05 | 45.16 |
| 15m | ATR/2 | equity | INFY_NS | 30 | 14 | 16 | 23156.68 | 12054.75 | 11101.93 | 46.67 |
| 15m | ATR/2 | equity | ITC_NS | 39 | 20 | 19 | -63782.23 | 15683.72 | -79465.95 | 23.08 |
| 15m | ATR/2 | equity | KOTAKBANK_NS | 34 | 16 | 18 | -8959.79 | 13678.73 | -22638.52 | 38.24 |
| 15m | ATR/2 | equity | LT_NS | 40 | 20 | 20 | 38212.74 | 16052.12 | 22160.62 | 47.5 |
| 15m | ATR/2 | equity | RELIANCE_NS | 39 | 20 | 19 | -13518.27 | 15684.15 | -29202.42 | 35.9 |
| 15m | ATR/2 | equity | SBIN_NS | 32 | 15 | 17 | 13543.11 | 12868.9 | 674.21 | 37.5 |
| 15m | ATR/2 | equity | TCS_NS | 34 | 17 | 17 | -18072.12 | 13658.57 | -31730.69 | 38.24 |
| 15m | ATR/2 | usdinr | USDINR | 27 | 14 | 13 | -123293.24 | 10851.34 | -134144.58 | 0.0 |
| 30m | ATR/2 | commodities | CLF | 19 | 9 | 10 | -209073.68 | 327069.81 | -536143.49 | 0.0 |
| 30m | ATR/2 | commodities | GCF | 15 | 8 | 7 | 281.26 | 257889.81 | -257608.55 | 0.0 |
| 30m | ATR/2 | commodities | HGF | 22 | 10 | 12 | -1512248.71 | 381974.33 | -1894223.04 | 0.0 |
| 30m | ATR/2 | commodities | NGF | 21 | 10 | 11 | -3160450.11 | 365896.4 | -3526346.51 | 0.0 |
| 30m | ATR/2 | commodities | SIF | 16 | 7 | 9 | -84541.0 | 276156.92 | -360697.92 | 0.0 |
| 30m | ATR/2 | derivatives | CNXAUTO | 19 | 9 | 10 | -10596.79 | 11469.45 | -22066.24 | 42.11 |
| 30m | ATR/2 | derivatives | CNXFMCG | 16 | 9 | 7 | -15525.08 | 9549.04 | -25074.12 | 31.25 |
| 30m | ATR/2 | derivatives | CNXIT | 14 | 7 | 7 | -1675.16 | 8463.83 | -10138.99 | 42.86 |
| 30m | ATR/2 | derivatives | NSEBANK | 16 | 8 | 8 | -13399.29 | 9545.84 | -22945.13 | 37.5 |
| 30m | ATR/2 | derivatives | NSEI | 14 | 7 | 7 | -17776.3 | 8495.53 | -26271.83 | 28.57 |
| 30m | ATR/2 | equity | BHARTIARTL_NS | 12 | 5 | 7 | -24871.58 | 4827.14 | -29698.72 | 16.67 |
| 30m | ATR/2 | equity | HDFCBANK_NS | 18 | 9 | 9 | 3956.79 | 7231.75 | -3274.96 | 44.44 |
| 30m | ATR/2 | equity | ICICIBANK_NS | 11 | 5 | 6 | 3579.06 | 4428.14 | -849.08 | 45.45 |
| 30m | ATR/2 | equity | INFY_NS | 18 | 9 | 9 | -13652.53 | 7227.65 | -20880.18 | 33.33 |
| 30m | ATR/2 | equity | ITC_NS | 13 | 7 | 6 | -6561.68 | 5230.48 | -11792.16 | 30.77 |
| 30m | ATR/2 | equity | KOTAKBANK_NS | 18 | 9 | 9 | -10134.5 | 7230.7 | -17365.2 | 33.33 |
| 30m | ATR/2 | equity | LT_NS | 17 | 9 | 8 | -24185.91 | 6819.65 | -31005.56 | 47.06 |
| 30m | ATR/2 | equity | RELIANCE_NS | 14 | 7 | 7 | 28379.99 | 5635.84 | 22744.15 | 64.29 |
| 30m | ATR/2 | equity | SBIN_NS | 17 | 8 | 9 | -8655.13 | 6834.97 | -15490.1 | 41.18 |
| 30m | ATR/2 | equity | TCS_NS | 15 | 7 | 8 | 31039.98 | 6021.52 | 25018.46 | 53.33 |
| 30m | ATR/2 | usdinr | USDINR | 10 | 6 | 4 | -42890.67 | 4016.98 | -46907.65 | 0.0 |
| 1h | ATR/2 | derivatives | CNXAUTO | 5 | 2 | 3 | -2659.14 | 3017.89 | -5677.03 | 40.0 |
| 1h | ATR/2 | derivatives | CNXFMCG | 2 | 1 | 1 | -3953.43 | 1207.12 | -5160.55 | 0.0 |
| 1h | ATR/2 | derivatives | CNXIT | 5 | 3 | 2 | -2214.92 | 3012.22 | -5227.14 | 40.0 |
| 1h | ATR/2 | derivatives | NSEBANK | 6 | 2 | 4 | 8361.43 | 3542.1 | 4819.33 | 66.67 |
| 1h | ATR/2 | derivatives | NSEI | 9 | 4 | 5 | -7112.73 | 5480.23 | -12592.96 | 33.33 |
| 1h | ATR/2 | equity | BHARTIARTL_NS | 6 | 3 | 3 | 6781.1 | 2408.87 | 4372.23 | 50.0 |
| 1h | ATR/2 | equity | HDFCBANK_NS | 5 | 2 | 3 | -13135.0 | 2005.93 | -15140.93 | 20.0 |
| 1h | ATR/2 | equity | ICICIBANK_NS | 4 | 1 | 3 | 11696.36 | 1609.82 | 10086.54 | 50.0 |
| 1h | ATR/2 | equity | INFY_NS | 6 | 4 | 2 | -12781.94 | 2400.87 | -15182.81 | 33.33 |
| 1h | ATR/2 | equity | ITC_NS | 4 | 3 | 1 | 802.67 | 1607.01 | -804.34 | 50.0 |
| 1h | ATR/2 | equity | KOTAKBANK_NS | 7 | 4 | 3 | -17234.33 | 2812.28 | -20046.61 | 14.29 |
| 1h | ATR/2 | equity | LT_NS | 8 | 4 | 4 | -20978.18 | 3210.82 | -24189.0 | 12.5 |
| 1h | ATR/2 | equity | RELIANCE_NS | 6 | 3 | 3 | 34257.84 | 2414.14 | 31843.7 | 83.33 |
| 1h | ATR/2 | equity | SBIN_NS | 6 | 2 | 4 | -25836.9 | 2408.86 | -28245.76 | 50.0 |
| 1h | ATR/2 | equity | TCS_NS | 7 | 4 | 3 | 15654.24 | 2809.54 | 12844.7 | 57.14 |

## Brokerage And Charges

| Timeframe | Mode | Segment | Trades | Turnover | Brokerage | STT | CTT | Exchange | GST | SEBI | Stamp | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5m | ATR/2 | Commodity futures MCX | 506 | 1012083377.04 | 20240.0 | 0.0 | 5064391.91 | 2125375.18 | 404428.26 | 101208.41 | 1011288.57 | 8726931.99 |
| 5m | ATR/2 | F&O futures NSE | 600 | 1175592997.83 | 24000.0 | 293958.65 | 0.0 | 21513.41 | 8403.96 | 1175.58 | 11753.55 | 360805.11 |
| 5m | ATR/2 | Intraday equity NSE | 1319 | 2636447143.11 | 52760.0 | 329594.14 | 0.0 | 80938.97 | 24540.33 | 2636.69 | 39542.29 | 530011.82 |
| 15m | ATR/2 | Commodity futures MCX | 187 | 374348514.06 | 7480.0 | 0.0 | 1874423.85 | 786131.88 | 149588.37 | 37434.88 | 373812.37 | 3228871.3 |
| 15m | ATR/2 | F&O futures NSE | 172 | 336906095.02 | 6880.0 | 84262.69 | 0.0 | 6165.41 | 2408.84 | 336.9 | 3367.61 | 103421.41 |
| 15m | ATR/2 | Intraday equity NSE | 385 | 769765576.89 | 15400.0 | 96257.8 | 0.0 | 23631.78 | 7164.33 | 769.82 | 11542.07 | 154765.64 |
| 30m | ATR/2 | Commodity futures MCX | 93 | 186433709.03 | 3720.0 | 0.0 | 934685.42 | 391510.81 | 74497.33 | 18643.42 | 185930.38 | 1608987.27 |
| 30m | ATR/2 | F&O futures NSE | 79 | 154816064.66 | 3160.0 | 38721.66 | 0.0 | 2833.12 | 1106.64 | 154.86 | 1547.48 | 47523.69 |
| 30m | ATR/2 | Intraday equity NSE | 163 | 325839979.41 | 6520.0 | 40735.97 | 0.0 | 10003.23 | 3032.87 | 325.83 | 4886.93 | 65504.82 |
| 1h | ATR/2 | F&O futures NSE | 27 | 53003308.5 | 1080.0 | 13247.96 | 0.0 | 969.96 | 378.52 | 52.99 | 530.15 | 16259.56 |
| 1h | ATR/2 | Intraday equity NSE | 59 | 117853421.71 | 2360.0 | 14726.49 | 0.0 | 3618.1 | 1097.25 | 117.86 | 1768.42 | 23688.14 |

## Direction And Exit Summary

| Timeframe | Mode | Direction | Exit | Trades | Before Brokerage | Charges | After Brokerage |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5m | ATR/2 | LONG | OPPOSITE_RENKO_FLIP | 1016 | -4515939.12 | 3724330.79 | -8240269.91 |
| 5m | ATR/2 | LONG | SESSION_END | 196 | -1708225.03 | 1004339.86 | -2712564.89 |
| 5m | ATR/2 | SHORT | OPPOSITE_RENKO_FLIP | 1003 | -5106646.7 | 3887847.78 | -8994494.48 |
| 5m | ATR/2 | SHORT | SESSION_END | 210 | -2459156.62 | 1001230.49 | -3460387.11 |
| 15m | ATR/2 | LONG | OPPOSITE_RENKO_FLIP | 190 | -2598990.88 | 947358.99 | -3546349.87 |
| 15m | ATR/2 | LONG | SESSION_END | 176 | -1001611.28 | 717847.5 | -1719458.78 |
| 15m | ATR/2 | SHORT | OPPOSITE_RENKO_FLIP | 227 | -2255712.63 | 882381.05 | -3138093.67 |
| 15m | ATR/2 | SHORT | SESSION_END | 151 | -2322835.04 | 939470.81 | -3262305.85 |
| 30m | ATR/2 | LONG | OPPOSITE_RENKO_FLIP | 43 | -1266540.76 | 274711.93 | -1541252.69 |
| 30m | ATR/2 | LONG | SESSION_END | 122 | -967016.4 | 511903.45 | -1478919.85 |
| 30m | ATR/2 | SHORT | OPPOSITE_RENKO_FLIP | 44 | -828750.83 | 196745.78 | -1025496.61 |
| 30m | ATR/2 | SHORT | SESSION_END | 126 | -2026693.05 | 738654.62 | -2765347.67 |
| 1h | ATR/2 | LONG | OPPOSITE_RENKO_FLIP | 5 | -35379.51 | 2582.93 | -37962.44 |
| 1h | ATR/2 | LONG | SESSION_END | 37 | -5254.71 | 16672.31 | -21927.02 |
| 1h | ATR/2 | SHORT | OPPOSITE_RENKO_FLIP | 1 | 7974.46 | 398.89 | 7575.57 |
| 1h | ATR/2 | SHORT | SESSION_END | 43 | 4306.83 | 20293.57 | -15986.74 |

## Best And Worst Trades

| Rank Type | Rank | Timeframe | Mode | Market | Instrument | Date | Direction | Exit | Before Brokerage | Charges | After Brokerage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| best | 1 | 15m | ATR/2 | equity | LT_NS | 2026-04-06 | LONG | SESSION_END | 31684.79 | 409.92 | 31274.87 |
| best | 2 | 5m | ATR/2 | equity | LT_NS | 2026-04-02 | LONG | OPPOSITE_RENKO_FLIP | 30773.6 | 409.73 | 30363.87 |
| best | 3 | 15m | ATR/2 | equity | ICICIBANK_NS | 2026-04-13 | LONG | SESSION_END | 30443.64 | 410.49 | 30033.15 |
| best | 4 | 5m | ATR/2 | equity | RELIANCE_NS | 2026-04-06 | SHORT | OPPOSITE_RENKO_FLIP | 26930.6 | 393.93 | 26536.67 |
| best | 5 | 5m | ATR/2 | equity | SBIN_NS | 2026-04-02 | LONG | OPPOSITE_RENKO_FLIP | 26416.02 | 409.53 | 26006.49 |
| best | 6 | 5m | ATR/2 | commodities | CLF | 2026-04-13 | SHORT | SESSION_END | 40584.35 | 16726.38 | 23857.97 |
| best | 7 | 1h | ATR/2 | equity | RELIANCE_NS | 2026-04-27 | LONG | SESSION_END | 23200.6 | 408.34 | 22792.26 |
| best | 8 | 5m | ATR/2 | equity | INFY_NS | 2026-04-02 | LONG | SESSION_END | 21985.24 | 408.26 | 21576.98 |
| best | 9 | 30m | ATR/2 | equity | INFY_NS | 2026-04-23 | SHORT | SESSION_END | 21755.64 | 395.41 | 21360.23 |
| best | 10 | 15m | ATR/2 | equity | LT_NS | 2026-04-09 | SHORT | SESSION_END | 21560.91 | 395.28 | 21165.63 |
| worst | 1 | 5m | ATR/2 | commodities | NGF | 2026-04-17 | SHORT | OPPOSITE_RENKO_FLIP | -180395.07 | 19511.43 | -199906.5 |
| worst | 2 | 5m | ATR/2 | commodities | NGF | 2026-04-15 | SHORT | OPPOSITE_RENKO_FLIP | -179916.25 | 19505.42 | -199421.67 |
| worst | 3 | 5m | ATR/2 | commodities | NGF | 2026-04-16 | SHORT | OPPOSITE_RENKO_FLIP | -175503.44 | 19449.83 | -194953.27 |
| worst | 4 | 15m | ATR/2 | commodities | NGF | 2026-04-17 | SHORT | OPPOSITE_RENKO_FLIP | -175503.44 | 19449.83 | -194953.27 |
| worst | 5 | 5m | ATR/2 | commodities | NGF | 2026-04-10 | SHORT | OPPOSITE_RENKO_FLIP | -170186.48 | 19382.83 | -189569.31 |
| worst | 6 | 5m | ATR/2 | commodities | NGF | 2026-04-29 | SHORT | SESSION_END | -168516.1 | 19361.82 | -187877.92 |
| worst | 7 | 15m | ATR/2 | commodities | NGF | 2026-04-02 | SHORT | OPPOSITE_RENKO_FLIP | -165957.32 | 19329.59 | -185286.91 |
| worst | 8 | 5m | ATR/2 | commodities | NGF | 2026-04-14 | SHORT | OPPOSITE_RENKO_FLIP | -165360.74 | 19322.08 | -184682.82 |
| worst | 9 | 30m | ATR/2 | commodities | NGF | 2026-04-23 | SHORT | OPPOSITE_RENKO_FLIP | -165288.87 | 19321.14 | -184610.01 |
| worst | 10 | 15m | ATR/2 | commodities | NGF | 2026-04-21 | SHORT | SESSION_END | -163987.07 | 19304.77 | -183291.84 |

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

- Brick size follows the Pine input mode. Default mode is `ATR/2` with ATR period 14.
- Renko state is updated from each selected timeframe candle close.
- `Trend is UP` alerts are traded as long entries; `Trend is DOWN` alerts are traded as short entries.
- Entry happens at the next candle open after the signal candle closes.
- Existing positions exit/reverse on the next opposite Renko flip.
- Positions also exit at session end unless overnight holding is enabled.
- Position size uses configured max capital allocation per trade.

## Skipped Signals

| Timeframe | Mode | Reason | Count |
| --- | --- | --- | --- |
| 5m | ATR/2 | partial_session_missing_configured_open | 22 |
| 5m | ATR/2 | signal_without_next_session_bar | 27 |
| 15m | ATR/2 | partial_session_missing_configured_open | 21 |
| 15m | ATR/2 | signal_without_next_session_bar | 21 |
| 30m | ATR/2 | signal_without_next_session_bar | 20 |
| 1h | ATR/2 | partial_session_missing_configured_open | 126 |
| 1h | ATR/2 | signal_without_next_session_bar | 8 |

## Parameters

- **modes**: ('ATR/2',)
- **atr_period**: 14
- **traditional_brick_size**: 10.0
- **percentage_pct**: 0.1
- **min_tick**: 0.0
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
- **top_trade_count**: 10

## Output Files

- `summary.md`
- `summary.json`
- `timeframe_mode_summary.csv`
