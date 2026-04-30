"""
Backtest a Pine-style Sniper Entry/Exit strategy on existing 5-minute data.

The original TradingView script is an indicator, so this file translates its
tradeable parts into explicit backtest rules:

- Signal: EMA 9 crossing EMA 21.
- Entry: next candle open after the signal candle closes.
- Stop: signal close +/- ATR(14) * ATR multiplier.
- Targets: TP1..TP5 at 1R..5R, tested as separate full-exit variants.
- Exit: selected target hit, stop hit, opposite EMA signal, or session end.

The dashboard indicators from the Pine script are also calculated and stored
with each trade for later analysis.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, time
from pathlib import Path
from typing import Any

import open_low_high_5m_strategy as base


@dataclass(frozen=True)
class SniperConfig:
    ema_fast: int
    ema_slow: int
    atr_period: int
    atr_multiplier: float
    rsi_period: int
    macd_fast: int
    macd_slow: int
    macd_signal: int
    adx_period: int
    adx_smoothing: int
    volume_sma_period: int
    capital: float
    risk_per_trade_pct: float
    max_allocation_pct: float
    cost_multiplier: float
    equity_slippage: float
    derivatives_slippage: float
    commodities_slippage: float
    session_start: time | None
    exit_time: time | None
    require_session_open: bool
    exit_at_session_end: bool
    ambiguous_policy: str
    target_levels: tuple[int, ...]
    invert_signals: bool
    top_trade_count: int


def ema_series(values: list[float], period: int) -> list[float | None]:
    if not values:
        return []

    alpha = 2.0 / (period + 1.0)
    result: list[float | None] = []
    prev = values[0]
    for value in values:
        prev = (value * alpha) + (prev * (1.0 - alpha))
        result.append(prev)
    return result


def sma_series(values: list[float], period: int) -> list[float | None]:
    result: list[float | None] = []
    running_sum = 0.0
    for index, value in enumerate(values):
        running_sum += value
        if index >= period:
            running_sum -= values[index - period]
        if index >= period - 1:
            result.append(running_sum / period)
        else:
            result.append(None)
    return result


def rma_series(values: list[float | None], period: int) -> list[float | None]:
    result: list[float | None] = []
    seed_values: list[float] = []
    prev: float | None = None

    for value in values:
        if value is None:
            result.append(None)
            continue

        if prev is None:
            seed_values.append(value)
            if len(seed_values) == period:
                prev = sum(seed_values) / period
                result.append(prev)
            else:
                result.append(None)
            continue

        prev = ((prev * (period - 1)) + value) / period
        result.append(prev)

    return result


def true_range_values(candles: list[dict[str, Any]]) -> list[float]:
    values: list[float] = []
    previous_close: float | None = None

    for candle in candles:
        high = float(candle["High"])
        low = float(candle["Low"])
        if previous_close is None:
            true_range = high - low
        else:
            true_range = max(
                high - low,
                abs(high - previous_close),
                abs(low - previous_close),
            )
        values.append(true_range)
        previous_close = float(candle["Close"])

    return values


def rsi_series(closes: list[float], period: int) -> list[float | None]:
    gains: list[float | None] = [None]
    losses: list[float | None] = [None]

    for index in range(1, len(closes)):
        change = closes[index] - closes[index - 1]
        gains.append(max(change, 0.0))
        losses.append(max(-change, 0.0))

    avg_gain = rma_series(gains, period)
    avg_loss = rma_series(losses, period)
    result: list[float | None] = []

    for gain, loss in zip(avg_gain, avg_loss):
        if gain is None or loss is None:
            result.append(None)
        elif loss == 0:
            result.append(100.0)
        else:
            rs = gain / loss
            result.append(100.0 - (100.0 / (1.0 + rs)))

    return result


def macd_series(
    closes: list[float],
    fast_period: int,
    slow_period: int,
    signal_period: int,
) -> tuple[list[float | None], list[float | None]]:
    fast = ema_series(closes, fast_period)
    slow = ema_series(closes, slow_period)
    macd_values: list[float] = [
        (fast_value or 0.0) - (slow_value or 0.0)
        for fast_value, slow_value in zip(fast, slow)
    ]
    signal_values = ema_series(macd_values, signal_period)
    return macd_values, signal_values


def adx_series(
    candles: list[dict[str, Any]],
    di_period: int,
    adx_smoothing: int,
) -> list[float | None]:
    true_ranges = true_range_values(candles)
    plus_dm: list[float | None] = [None]
    minus_dm: list[float | None] = [None]

    for index in range(1, len(candles)):
        current = candles[index]
        previous = candles[index - 1]
        up_move = float(current["High"]) - float(previous["High"])
        down_move = float(previous["Low"]) - float(current["Low"])
        plus_dm.append(up_move if up_move > down_move and up_move > 0 else 0.0)
        minus_dm.append(down_move if down_move > up_move and down_move > 0 else 0.0)

    atr = rma_series(true_ranges, di_period)
    plus_smoothed = rma_series(plus_dm, di_period)
    minus_smoothed = rma_series(minus_dm, di_period)
    dx_values: list[float | None] = []

    for atr_value, plus_value, minus_value in zip(atr, plus_smoothed, minus_smoothed):
        if (
            atr_value is None
            or plus_value is None
            or minus_value is None
            or atr_value == 0
        ):
            dx_values.append(None)
            continue

        plus_di = 100.0 * plus_value / atr_value
        minus_di = 100.0 * minus_value / atr_value
        total = plus_di + minus_di
        if total == 0:
            dx_values.append(0.0)
        else:
            dx_values.append(100.0 * abs(plus_di - minus_di) / total)

    return rma_series(dx_values, adx_smoothing)


def vwap_series(candles: list[dict[str, Any]]) -> list[float | None]:
    result: list[float | None] = []
    current_date: str | None = None
    cumulative_price_volume = 0.0
    cumulative_volume = 0.0
    cumulative_typical = 0.0
    count = 0

    for candle in candles:
        candle_date = candle["dt"].date().isoformat()
        if candle_date != current_date:
            current_date = candle_date
            cumulative_price_volume = 0.0
            cumulative_volume = 0.0
            cumulative_typical = 0.0
            count = 0

        typical = (float(candle["High"]) + float(candle["Low"]) + float(candle["Close"])) / 3.0
        volume = float(candle["Volume"])
        cumulative_price_volume += typical * volume
        cumulative_volume += volume
        cumulative_typical += typical
        count += 1

        if cumulative_volume > 0:
            result.append(cumulative_price_volume / cumulative_volume)
        else:
            result.append(cumulative_typical / count)

    return result


def add_sniper_indicators(candles: list[dict[str, Any]], config: SniperConfig) -> None:
    closes = [float(candle["Close"]) for candle in candles]
    volumes = [float(candle["Volume"]) for candle in candles]
    ema_fast = ema_series(closes, config.ema_fast)
    ema_slow = ema_series(closes, config.ema_slow)
    vwap = vwap_series(candles)
    atr = rma_series(true_range_values(candles), config.atr_period)
    rsi = rsi_series(closes, config.rsi_period)
    macd, macd_signal = macd_series(
        closes,
        config.macd_fast,
        config.macd_slow,
        config.macd_signal,
    )
    adx = adx_series(candles, config.adx_period, config.adx_smoothing)
    volume_sma = sma_series(volumes, config.volume_sma_period)

    for index, candle in enumerate(candles):
        close = float(candle["Close"])
        open_price = float(candle["Open"])
        volume = float(candle["Volume"])
        ema_fast_value = ema_fast[index]
        ema_slow_value = ema_slow[index]
        vwap_value = vwap[index]
        atr_value = atr[index]
        rsi_value = rsi[index]
        macd_value = macd[index]
        macd_signal_value = macd_signal[index]
        adx_value = adx[index]
        volume_avg = volume_sma[index]

        bull_score = 0
        bear_score = 0
        if vwap_value is not None:
            bull_score += 1 if close > vwap_value else 0
            bear_score += 1 if close < vwap_value else 0
        if rsi_value is not None:
            bull_score += 1 if rsi_value > 50 else 0
            bear_score += 1 if rsi_value < 50 else 0
        if macd_value is not None and macd_signal_value is not None:
            bull_score += 1 if macd_value > macd_signal_value else 0
            bear_score += 1 if macd_value < macd_signal_value else 0
        if ema_fast_value is not None and ema_slow_value is not None:
            bull_score += 1 if ema_fast_value > ema_slow_value else 0
            bear_score += 1 if ema_fast_value < ema_slow_value else 0
        if adx_value is not None and ema_fast_value is not None:
            bull_score += 1 if adx_value > 25 and close > ema_fast_value else 0
            bear_score += 1 if adx_value > 25 and close < ema_fast_value else 0
        if volume_avg is not None:
            bull_score += 1 if volume > volume_avg and close > open_price else 0
            bear_score += 1 if volume > volume_avg and close < open_price else 0
        if rsi_value is not None:
            bull_score += 1 if rsi_value > 50 else 0
            bear_score += 1 if rsi_value < 50 else 0

        bull_pct = (bull_score / 7.0) * 100.0
        bear_pct = (bear_score / 7.0) * 100.0
        if (bull_pct - bear_pct) >= 40:
            bias = "STRONG BULL"
        elif (bear_pct - bull_pct) >= 40:
            bias = "STRONG BEAR"
        elif bull_pct > bear_pct:
            bias = "MILD BULL"
        else:
            bias = "MILD BEAR"

        candle["EMA_FAST"] = ema_fast_value
        candle["EMA_SLOW"] = ema_slow_value
        candle["VWAP"] = vwap_value
        candle["ATR"] = atr_value
        candle["RSI"] = rsi_value
        candle["RSI_5M"] = rsi_value
        candle["MACD"] = macd_value
        candle["MACD_SIGNAL"] = macd_signal_value
        candle["ADX"] = adx_value
        candle["VOLUME_SMA"] = volume_avg
        candle["BULL_SCORE"] = bull_pct
        candle["BEAR_SCORE"] = bear_pct
        candle["BIAS"] = bias


def add_signal_state(candles: list[dict[str, Any]]) -> None:
    last_signal_state = 0

    for index, candle in enumerate(candles):
        candle["SIGNAL"] = ""
        if index == 0:
            continue

        previous = candles[index - 1]
        prev_fast = previous.get("EMA_FAST")
        prev_slow = previous.get("EMA_SLOW")
        fast = candle.get("EMA_FAST")
        slow = candle.get("EMA_SLOW")
        if None in (prev_fast, prev_slow, fast, slow):
            continue

        buy_cond = prev_fast <= prev_slow and fast > slow
        sell_cond = prev_fast >= prev_slow and fast < slow
        trigger_buy = buy_cond and last_signal_state <= 0
        trigger_sell = sell_cond and last_signal_state >= 0

        if trigger_buy:
            candle["SIGNAL"] = "BUY"
            last_signal_state = 1
        elif trigger_sell:
            candle["SIGNAL"] = "SELL"
            last_signal_state = -1


def session_key(candle: dict[str, Any]) -> str:
    return candle["dt"].date().isoformat()


def load_instrument_candles(
    path: Path,
    config: SniperConfig,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    raw_candles = base.load_candles(path)
    sessions = base.group_sessions(raw_candles, config.session_start, config.exit_time)
    filtered: list[dict[str, Any]] = []
    skipped_partial_sessions = 0

    for date_key in sorted(sessions):
        session = sessions[date_key]
        if (
            config.session_start is not None
            and config.require_session_open
            and session[0]["dt"].time() != config.session_start
        ):
            skipped_partial_sessions += 1
            continue
        filtered.extend(session)

    add_sniper_indicators(filtered, config)
    add_signal_state(filtered)

    return filtered, {
        "market": base.market_name(path),
        "instrument": base.instrument_name(path),
        "file": str(path),
        "candles": len(filtered),
        "sessions": len({session_key(candle) for candle in filtered}),
        "signals": sum(1 for candle in filtered if candle.get("SIGNAL")),
        "skipped_partial_sessions": skipped_partial_sessions,
    }


def target_price(entry_reference: float, risk: float, direction: str, level: int) -> float:
    if direction == "LONG":
        return entry_reference + (risk * level)
    return entry_reference - (risk * level)


def stop_price(entry_reference: float, risk: float, direction: str) -> float:
    if direction == "LONG":
        return entry_reference - risk
    return entry_reference + risk


def target_hit(candle: dict[str, Any], direction: str, price: float) -> bool:
    if direction == "LONG":
        return float(candle["High"]) >= price
    return float(candle["Low"]) <= price


def stop_hit(candle: dict[str, Any], direction: str, price: float) -> bool:
    if direction == "LONG":
        return float(candle["Low"]) <= price
    return float(candle["High"]) >= price


def direction_from_signal(signal: str, invert_signals: bool = False) -> str:
    if invert_signals:
        return "SHORT" if signal == "BUY" else "LONG"
    return "LONG" if signal == "BUY" else "SHORT"


def opposite_signal_for(direction: str) -> str:
    return "SELL" if direction == "LONG" else "BUY"


def fill_pnl_values(
    trade: dict[str, Any],
    exit_candle: dict[str, Any],
    raw_exit_price: float,
    exit_reason: str,
    config: SniperConfig,
) -> dict[str, Any]:
    direction = trade["direction"]
    slippage_points = float(trade.get("slippage_points", 0.0))
    exit_price = base.apply_exit_slippage(
        raw_exit_price,
        direction,
        slippage_points,
    )
    entry_price = float(trade["entry_price"])
    quantity = int(trade["quantity"])
    if direction == "LONG":
        gross_pnl = (exit_price - entry_price) * quantity
    else:
        gross_pnl = (entry_price - exit_price) * quantity

    costs = base.brokerage_cost(
        entry_price,
        exit_price,
        quantity,
        trade["market"],
        trade["instrument"],
        config,
    )
    net_pnl = gross_pnl - costs
    risk_amount = float(trade["position_risk_amount"])
    notional = float(trade["notional"])

    trade.update(
        {
            "exit_time": exit_candle["dt"].isoformat(),
            "exit_price": round(exit_price, 6),
            "exit_reason": exit_reason,
            "gross_pnl": round(gross_pnl, 2),
            "costs": round(costs, 2),
            "net_pnl": round(net_pnl, 2),
            "return_pct_on_notional": round((net_pnl / notional) * 100.0, 4)
            if notional > 0
            else 0.0,
            "r_multiple": round(net_pnl / risk_amount, 4) if risk_amount > 0 else 0.0,
        }
    )
    return trade


def build_trade_at_entry(
    market: str,
    instrument: str,
    signal_candle: dict[str, Any],
    entry_candle: dict[str, Any],
    target_level: int,
    config: SniperConfig,
) -> dict[str, Any] | None:
    original_signal = signal_candle["SIGNAL"]
    direction = direction_from_signal(original_signal, config.invert_signals)
    trade_signal = (
        f"INVERSE_{original_signal}"
        if config.invert_signals
        else original_signal
    )
    entry_reference = float(signal_candle["Close"])
    atr = signal_candle.get("ATR")
    if atr is None or atr <= 0:
        return None

    slippage_points = base.slippage_points_for_market(market, instrument, config)
    risk = float(atr) * config.atr_multiplier
    stop = stop_price(entry_reference, risk, direction)
    targets = {
        level: target_price(entry_reference, risk, direction, level)
        for level in range(1, 6)
    }
    entry_price = base.apply_entry_slippage(
        float(entry_candle["Open"]),
        direction,
        slippage_points,
    )

    if direction == "LONG" and entry_price <= stop:
        return None
    if direction == "SHORT" and entry_price >= stop:
        return None

    stop_fill = base.apply_exit_slippage(stop, direction, slippage_points)
    stop_distance = abs(entry_price - stop_fill)
    if stop_distance <= 0:
        return None

    risk_budget = config.capital * base.pct_to_decimal(config.risk_per_trade_pct)
    allocation_budget = config.capital * base.pct_to_decimal(config.max_allocation_pct)
    quantity = min(
        math.floor(risk_budget / stop_distance),
        math.floor(allocation_budget / entry_price),
    )
    if quantity <= 0:
        return None

    position_risk = stop_distance * quantity
    notional = entry_price * quantity
    bull_pct = signal_candle.get("BULL_SCORE")
    bear_pct = signal_candle.get("BEAR_SCORE")

    return {
        "target_level": target_level,
        "market": market,
        "instrument": instrument,
        "session_date": session_key(signal_candle),
        "signal": trade_signal,
        "original_signal": original_signal,
        "direction": direction,
        "signal_time": signal_candle["dt"].isoformat(),
        "entry_time": entry_candle["dt"].isoformat(),
        "pine_entry_price": round(entry_reference, 6),
        "entry_price": round(entry_price, 6),
        "stop_price": round(stop, 6),
        "target_price": round(targets[target_level], 6),
        "tp1": round(targets[1], 6),
        "tp2": round(targets[2], 6),
        "tp3": round(targets[3], 6),
        "tp4": round(targets[4], 6),
        "tp5": round(targets[5], 6),
        "atr": round(float(atr), 6),
        "risk_per_unit_reference": round(risk, 6),
        "ema_fast": round(float(signal_candle["EMA_FAST"]), 6),
        "ema_slow": round(float(signal_candle["EMA_SLOW"]), 6),
        "vwap": round(float(signal_candle["VWAP"]), 6)
        if signal_candle.get("VWAP") is not None
        else "",
        "rsi": round(float(signal_candle["RSI"]), 4)
        if signal_candle.get("RSI") is not None
        else "",
        "macd": round(float(signal_candle["MACD"]), 6)
        if signal_candle.get("MACD") is not None
        else "",
        "macd_signal": round(float(signal_candle["MACD_SIGNAL"]), 6)
        if signal_candle.get("MACD_SIGNAL") is not None
        else "",
        "adx": round(float(signal_candle["ADX"]), 4)
        if signal_candle.get("ADX") is not None
        else "",
        "volume": round(float(signal_candle["Volume"]), 2),
        "volume_sma": round(float(signal_candle["VOLUME_SMA"]), 2)
        if signal_candle.get("VOLUME_SMA") is not None
        else "",
        "bull_score_pct": round(float(bull_pct), 2) if bull_pct is not None else "",
        "bear_score_pct": round(float(bear_pct), 2) if bear_pct is not None else "",
        "bias": signal_candle.get("BIAS", ""),
        "quantity": quantity,
        "notional": round(notional, 2),
        "position_risk_amount": round(position_risk, 2),
        "slippage_points": round(slippage_points, 6),
        "max_target_hit": 0,
        "holding_candles": 0,
        "_entry_index": entry_candle["_index"],
        "_direction": direction,
        "_original_signal": original_signal,
        "_stop": stop,
        "_targets": targets,
    }


def public_trade(trade: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in trade.items() if not key.startswith("_")}


def manage_active_trade(
    active: dict[str, Any],
    candle: dict[str, Any],
    is_session_last: bool,
    target_level: int,
    config: SniperConfig,
) -> dict[str, Any] | None:
    direction = active["_direction"]
    stop = active["_stop"]
    target = active["_targets"][target_level]

    for level, price in active["_targets"].items():
        if target_hit(candle, direction, price):
            active["max_target_hit"] = max(int(active["max_target_hit"]), level)

    did_stop = stop_hit(candle, direction, stop)
    did_target = target_hit(candle, direction, target)

    if did_stop and did_target:
        if config.ambiguous_policy == "target_first":
            return fill_pnl_values(
                active,
                candle,
                target,
                "TARGET_AND_STOP_SAME_CANDLE_TARGET_FIRST",
                config,
            )
        return fill_pnl_values(
            active,
            candle,
            stop,
            "TARGET_AND_STOP_SAME_CANDLE_STOP_FIRST",
            config,
        )

    if did_stop:
        return fill_pnl_values(active, candle, stop, "STOP_LOSS", config)

    if did_target:
        return fill_pnl_values(active, candle, target, f"TP{target_level}", config)

    if config.exit_at_session_end and is_session_last:
        return fill_pnl_values(
            active,
            candle,
            float(candle["Close"]),
            "SESSION_END",
            config,
        )

    return None


def build_session_last_indexes(candles: list[dict[str, Any]]) -> set[int]:
    last_by_session: dict[str, int] = {}
    for candle in candles:
        last_by_session[session_key(candle)] = candle["_index"]
    return set(last_by_session.values())


def next_entry_index_same_session(candles: list[dict[str, Any]], signal_index: int) -> int | None:
    entry_index = signal_index + 1
    if entry_index >= len(candles):
        return None
    if session_key(candles[entry_index]) != session_key(candles[signal_index]):
        return None
    return entry_index


def backtest_instrument(
    path: Path,
    target_level: int,
    config: SniperConfig,
    skip_counts: dict[str, int],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    market = base.market_name(path)
    instrument = base.instrument_name(path)
    candles, stats = load_instrument_candles(path, config)
    for index, candle in enumerate(candles):
        candle["_index"] = index

    session_last_indexes = build_session_last_indexes(candles)
    trades: list[dict[str, Any]] = []
    active: dict[str, Any] | None = None
    pending_signal_index: int | None = None

    for index, candle in enumerate(candles):
        if pending_signal_index == index - 1:
            candidate = build_trade_at_entry(
                market=market,
                instrument=instrument,
                signal_candle=candles[pending_signal_index],
                entry_candle=candle,
                target_level=target_level,
                config=config,
            )
            if candidate is None:
                skip_counts["invalid_or_unsized_entry"] += 1
            else:
                active = candidate
            pending_signal_index = None

        if active is not None:
            active["holding_candles"] = index - int(active["_entry_index"]) + 1
            closed = manage_active_trade(
                active,
                candle,
                index in session_last_indexes,
                target_level,
                config,
            )
            if closed is not None:
                trades.append(public_trade(closed))
                active = None

        signal = candle.get("SIGNAL")
        if signal not in {"BUY", "SELL"}:
            continue

        entry_index = next_entry_index_same_session(candles, index)
        if entry_index is None:
            skip_counts["signal_without_next_session_bar"] += 1
            continue

        if active is not None and signal != active["_original_signal"]:
            exit_candle = candles[entry_index]
            closed = fill_pnl_values(
                active,
                exit_candle,
                float(exit_candle["Open"]),
                "OPPOSITE_SIGNAL",
                config,
            )
            closed["holding_candles"] = entry_index - int(closed["_entry_index"]) + 1
            trades.append(public_trade(closed))
            active = None

        if active is None:
            pending_signal_index = index

    if active is not None and candles:
        closed = fill_pnl_values(
            active,
            candles[-1],
            float(candles[-1]["Close"]),
            "FINAL_BAR",
            config,
        )
        trades.append(public_trade(closed))

    stats["trades"] = len(trades)
    return trades, stats


def backtest_target_level(
    data_files: list[Path],
    target_level: int,
    config: SniperConfig,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    all_trades: list[dict[str, Any]] = []
    all_stats: list[dict[str, Any]] = []
    skip_counts: dict[str, int] = defaultdict(int)

    for path in data_files:
        trades, stats = backtest_instrument(path, target_level, config, skip_counts)
        all_trades.extend(trades)
        all_stats.append(stats)
        print(
            f"TP{target_level} {stats['market']}/{stats['instrument']}: "
            f"{stats['signals']} signals, {stats['trades']} trades"
        )

    return all_trades, all_stats, dict(sorted(skip_counts.items()))


def summary_for_target(
    target_level: int,
    trades: list[dict[str, Any]],
    file_stats: list[dict[str, Any]],
    skip_counts: dict[str, int],
    config: SniperConfig,
) -> dict[str, Any]:
    datewise_rows = base.build_datewise_pnl(trades, config.capital)
    equity_rows = base.build_equity_curve(trades, config.capital)
    strategy_config = base.StrategyConfig(
        tolerance_pct=0.0,
        stop_buffer_pct=0.0,
        target_type=f"tp{target_level}",
        risk_reward=float(target_level),
        target_pct=0.0,
        trailing_stop_pct=0.0,
        capital=config.capital,
        risk_per_trade_pct=config.risk_per_trade_pct,
        max_allocation_pct=config.max_allocation_pct,
        min_first_candle_volume=0.0,
        min_average_volume=0.0,
        max_gap_pct=0.0,
        cost_multiplier=config.cost_multiplier,
        equity_slippage=config.equity_slippage,
        derivatives_slippage=config.derivatives_slippage,
        commodities_slippage=config.commodities_slippage,
        session_start=config.session_start,
        exit_time=config.exit_time,
        require_session_open=config.require_session_open,
        ambiguous_policy=config.ambiguous_policy,
        top_trade_count=config.top_trade_count,
    )
    summary = base.build_summary(
        trades=trades,
        datewise_rows=datewise_rows,
        equity_rows=equity_rows,
        file_stats=file_stats,
        skip_counts=defaultdict(int, skip_counts),
        config=strategy_config,
    )
    summary["strategy"] = (
        "Inverse Sniper Entry/Exit with ATR SL and TP levels"
        if config.invert_signals
        else "Sniper Entry/Exit with ATR SL and TP levels"
    )
    summary["signal_mode"] = "inverse" if config.invert_signals else "normal"
    summary["target_level"] = target_level
    return summary


def comparison_row(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "target_level": summary["target_level"],
        "total_trades": summary["total_trades"],
        "win_rate_pct": summary["win_rate_pct"],
        "net_pnl": summary["net_pnl"],
        "ending_equity": summary["ending_equity"],
        "average_profit_loss": summary["average_profit_loss"],
        "max_drawdown": summary["max_drawdown"],
        "max_drawdown_pct": summary["max_drawdown_pct"],
        "profit_factor": summary["profit_factor"],
        "sharpe_ratio": summary["sharpe_ratio"],
    }


def build_market_metrics(trades: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for trade in trades:
        grouped[str(trade["market"])].append(trade)

    rows: list[dict[str, Any]] = []
    for market, market_trades in sorted(grouped.items()):
        net_values = [float(trade["net_pnl"]) for trade in market_trades]
        wins = [value for value in net_values if value > 0]
        losses = [value for value in net_values if value <= 0]
        pf = base.profit_factor(market_trades)
        rows.append(
            {
                "market": market,
                "trades": len(market_trades),
                "wins": len(wins),
                "losses": len(losses),
                "win_rate_pct": round((len(wins) / len(market_trades)) * 100.0, 2)
                if market_trades
                else 0.0,
                "net_pnl": round(sum(net_values), 2),
                "avg_pnl": round(statistics.mean(net_values), 2) if net_values else 0.0,
                "best_trade": round(max(net_values), 2) if net_values else 0.0,
                "worst_trade": round(min(net_values), 2) if net_values else 0.0,
                "profit_factor": round(pf, 4) if isinstance(pf, float) else pf,
            }
        )

    return rows


def build_markdown_summary(
    comparison_rows: list[dict[str, Any]],
    summaries: dict[str, dict[str, Any]],
    config: SniperConfig,
    output_files: list[Path],
) -> str:
    lines = [
        "# Inverse Sniper Entry/Exit 5m Backtest"
        if config.invert_signals
        else "# Sniper Entry/Exit 5m Backtest",
        "",
        "## Target Comparison",
        "",
        "| Target | Trades | Win Rate % | Net P&L | Ending Equity | Max DD % | Profit Factor | Sharpe |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for row in comparison_rows:
        lines.append(
            "| TP{target_level} | {total_trades} | {win_rate_pct} | {net_pnl} | "
            "{ending_equity} | {max_drawdown_pct} | {profit_factor} | "
            "{sharpe_ratio} |".format(**row)
        )

    first_summary = next(iter(summaries.values()), {})
    lines.extend(
        [
            "",
            "## Testing Scope",
            "",
            f"- **markets_tested**: {first_summary.get('markets_tested', '')}",
            "- **timeframe**: 5-minute candles",
            f"- **files_tested**: {first_summary.get('files_tested', '')}",
            f"- **sessions_tested**: {first_summary.get('sessions_tested', '')}",
            f"- **candles_tested**: {first_summary.get('candles_tested', '')}",
            f"- **trade_variants_tested**: TP{', TP'.join(str(row['target_level']) for row in comparison_rows)}",
            "",
            "## Cost Model",
            "",
        ]
    )
    for key, value in base.cost_model_summary(config).items():
        lines.append(f"- **{key}**: {value}")

    lines.extend(
        [
            "",
            "## Backtest Rules",
            "",
            "- Signal uses EMA 9 / EMA 21 crossovers from 5-minute candles.",
            "- In inverse mode, original BUY signals are traded as SHORT and original SELL signals are traded as LONG."
            if config.invert_signals
            else "- Original BUY signals are traded as LONG and original SELL signals are traded as SHORT.",
            "- Entry is the next candle open after signal close to avoid lookahead.",
            "- Stop and TP levels are anchored to the signal candle close, matching the indicator's plotted entry lines.",
            "- TP1 through TP5 are tested as separate full-position exits.",
            "- Trades also exit on stop, opposite signal, session end, or final bar.",
            "",
            "## Skip Counts",
            "",
        ]
    )

    for key in sorted(summaries):
        lines.append(f"### TP{key}")
        skips = summaries[key].get("skip_counts", {})
        if skips:
            for skip_name, value in skips.items():
                lines.append(f"- **{skip_name}**: {value}")
        else:
            lines.append("- None")
        lines.append("")

    lines.extend(["## Parameters", ""])
    for key, value in config.__dict__.items():
        if isinstance(value, time):
            value = value.strftime("%H:%M")
        lines.append(f"- **{key}**: {value}")

    lines.extend(["", "## Output Files", ""])
    for output_file in output_files:
        lines.append(f"- `{output_file.name}`")

    return "\n".join(lines) + "\n"


def parse_target_levels(values: list[int]) -> tuple[int, ...]:
    cleaned = sorted(set(values))
    invalid = [value for value in cleaned if value < 1 or value > 5]
    if invalid:
        raise argparse.ArgumentTypeError("Target levels must be between 1 and 5.")
    return tuple(cleaned)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backtest Pine-style Sniper Entry/Exit strategy on 5m data.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--markets",
        nargs="+",
        choices=base.MARKETS,
        default=list(base.MARKETS),
    )
    parser.add_argument("--ema-fast", type=int, default=9)
    parser.add_argument("--ema-slow", type=int, default=21)
    parser.add_argument("--atr-period", type=int, default=14)
    parser.add_argument("--atr-multiplier", type=float, default=1.5)
    parser.add_argument("--rsi-period", type=int, default=14)
    parser.add_argument("--macd-fast", type=int, default=12)
    parser.add_argument("--macd-slow", type=int, default=26)
    parser.add_argument("--macd-signal", type=int, default=9)
    parser.add_argument("--adx-period", type=int, default=14)
    parser.add_argument("--adx-smoothing", type=int, default=14)
    parser.add_argument("--volume-sma-period", type=int, default=20)
    parser.add_argument("--capital", type=float, default=1000000.0)
    parser.add_argument("--risk-per-trade-pct", type=float, default=1.0)
    parser.add_argument("--max-allocation-pct", type=float, default=100.0)
    parser.add_argument(
        "--cost-multiplier",
        type=float,
        default=1.0,
        help="1 uses brokerage.md calculator charges; 0 disables all charges.",
    )
    parser.add_argument("--equity-slippage", type=float, default=0.2)
    parser.add_argument("--derivatives-slippage", type=float, default=5.0)
    parser.add_argument("--commodities-slippage", type=float, default=0.2)
    parser.add_argument("--session-start", type=base.parse_clock, default=base.parse_clock("09:15"))
    parser.add_argument("--exit-time", type=base.parse_clock, default=base.parse_clock("15:20"))
    parser.add_argument("--allow-missing-session-open", action="store_true")
    parser.add_argument("--allow-overnight", action="store_true")
    parser.add_argument(
        "--ambiguous-policy",
        choices=("stop_first", "target_first"),
        default="stop_first",
    )
    parser.add_argument("--target-levels", nargs="+", type=int, default=[1, 2, 3, 4, 5])
    parser.add_argument(
        "--invert-signals",
        action="store_true",
        help="Trade the opposite side of each Pine signal: BUY as short, SELL as long.",
    )
    parser.add_argument("--top-trade-count", type=int, default=10)
    parser.add_argument("--run-name", default="")
    return parser.parse_args()


def config_from_args(args: argparse.Namespace) -> SniperConfig:
    return SniperConfig(
        ema_fast=args.ema_fast,
        ema_slow=args.ema_slow,
        atr_period=args.atr_period,
        atr_multiplier=args.atr_multiplier,
        rsi_period=args.rsi_period,
        macd_fast=args.macd_fast,
        macd_slow=args.macd_slow,
        macd_signal=args.macd_signal,
        adx_period=args.adx_period,
        adx_smoothing=args.adx_smoothing,
        volume_sma_period=args.volume_sma_period,
        capital=args.capital,
        risk_per_trade_pct=args.risk_per_trade_pct,
        max_allocation_pct=args.max_allocation_pct,
        cost_multiplier=args.cost_multiplier,
        equity_slippage=args.equity_slippage,
        derivatives_slippage=args.derivatives_slippage,
        commodities_slippage=args.commodities_slippage,
        session_start=args.session_start,
        exit_time=args.exit_time,
        require_session_open=not args.allow_missing_session_open,
        exit_at_session_end=not args.allow_overnight,
        ambiguous_policy=args.ambiguous_policy,
        target_levels=parse_target_levels(args.target_levels),
        invert_signals=args.invert_signals,
        top_trade_count=args.top_trade_count,
    )


def json_ready(value: Any) -> Any:
    if isinstance(value, time):
        return value.strftime("%H:%M")
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {key: json_ready(item) for key, item in value.items()}
    if isinstance(value, list) or isinstance(value, tuple):
        return [json_ready(item) for item in value]
    return value


def main() -> None:
    args = parse_args()
    config = config_from_args(args)

    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[2]
    common_root = script_path.parents[1]
    results_root = common_root / "results"
    default_prefix = (
        "sniper_entry_exit_inverse_5m"
        if config.invert_signals
        else "sniper_entry_exit_5m"
    )
    run_name = args.run_name.strip() or f"{default_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_dir = results_root / run_name
    output_dir.mkdir(parents=True, exist_ok=True)

    data_files = base.discover_data_files(repo_root, args.markets)
    if not data_files:
        raise SystemExit("No *_5m.csv files found in selected market data folders.")

    strategy_label = "Inverse Sniper Entry/Exit" if config.invert_signals else "Sniper Entry/Exit"
    print(f"Running {strategy_label} backtest on {len(data_files)} files...")
    summaries: dict[str, dict[str, Any]] = {}
    comparison_rows: list[dict[str, Any]] = []
    output_files: list[Path] = []

    for target_level in config.target_levels:
        print(f"\nTesting TP{target_level} full-exit variant")
        trades, file_stats, skip_counts = backtest_target_level(
            data_files,
            target_level,
            config,
        )
        datewise_rows = base.build_datewise_pnl(trades, config.capital)
        equity_rows = base.build_equity_curve(trades, config.capital)
        market_rows = build_market_metrics(trades)
        instrument_rows = base.build_instrument_metrics(trades)
        best_worst_rows = base.build_best_worst_trades(trades, config.top_trade_count)
        summary = summary_for_target(target_level, trades, file_stats, skip_counts, config)
        summaries[str(target_level)] = summary
        comparison_rows.append(comparison_row(summary))

        target_outputs = {
            "trades": output_dir / f"trades_tp{target_level}.csv",
            "datewise_pnl": output_dir / f"datewise_pnl_tp{target_level}.csv",
            "equity_curve": output_dir / f"equity_curve_tp{target_level}.csv",
            "market_metrics": output_dir / f"market_metrics_tp{target_level}.csv",
            "instrument_metrics": output_dir / f"instrument_metrics_tp{target_level}.csv",
            "best_worst_trades": output_dir / f"best_worst_trades_tp{target_level}.csv",
        }
        base.write_csv(target_outputs["trades"], trades)
        base.write_csv(target_outputs["datewise_pnl"], datewise_rows)
        base.write_csv(target_outputs["equity_curve"], equity_rows)
        base.write_csv(target_outputs["market_metrics"], market_rows)
        base.write_csv(target_outputs["instrument_metrics"], instrument_rows)
        base.write_csv(target_outputs["best_worst_trades"], best_worst_rows)
        output_files.extend(target_outputs.values())

        print(
            f"TP{target_level}: trades={summary['total_trades']}, "
            f"net_pnl={summary['net_pnl']}, "
            f"win_rate={summary['win_rate_pct']}%, "
            f"max_dd={summary['max_drawdown_pct']}%, "
            f"pf={summary['profit_factor']}"
        )

    comparison_path = output_dir / "target_comparison.csv"
    summary_path = output_dir / "summary.json"
    config_path = output_dir / "run_config.json"
    markdown_path = output_dir / "summary.md"
    base.write_csv(comparison_path, comparison_rows)
    summary_path.write_text(json.dumps(json_ready(summaries), indent=2), encoding="utf-8")
    config_path.write_text(
        json.dumps(
            {
                "markets": args.markets,
                "config": json_ready(config.__dict__),
                "data_files": [str(path) for path in data_files],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    output_files.extend([comparison_path, summary_path, config_path, markdown_path])
    markdown_path.write_text(
        build_markdown_summary(comparison_rows, summaries, config, output_files),
        encoding="utf-8",
    )

    print("")
    print(f"Results written to: {output_dir}")
    print("Target comparison:")
    for row in comparison_rows:
        print(
            f"  TP{row['target_level']}: "
            f"trades={row['total_trades']}, "
            f"net_pnl={row['net_pnl']}, "
            f"win_rate={row['win_rate_pct']}%, "
            f"max_dd={row['max_drawdown_pct']}%, "
            f"pf={row['profit_factor']}"
        )


if __name__ == "__main__":
    main()
