"""
Backtest the Supertrend Pine indicator on intraday candles.

The Pine source is an indicator, not a strategy. This module converts its
alertable buy/sell flips into explicit trades:

- BUY when Supertrend flips from downtrend to uptrend.
- SELL when Supertrend flips from uptrend to downtrend.
- Enter on the next candle open after the signal candle closes.
- Use the Supertrend line as the initial and trailing stop.
- Test TP1 through TP5 as fixed R targets from entry to stop.
- Exit on target, stop, opposite signal, session end, or final bar.
"""

from __future__ import annotations

import argparse
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import time
from pathlib import Path
from typing import Any

import open_low_high_5m_strategy as base


@dataclass(frozen=True)
class SupertrendConfig:
    atr_period: int
    multiplier: float
    change_atr: bool
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


def parse_target_levels(values: list[int]) -> tuple[int, ...]:
    cleaned = sorted({int(value) for value in values})
    invalid = [value for value in cleaned if value <= 0]
    if invalid:
        raise argparse.ArgumentTypeError("Target levels must be positive integers.")
    return tuple(cleaned)


def config_from_args(args: argparse.Namespace) -> SupertrendConfig:
    return SupertrendConfig(
        atr_period=args.atr_period,
        multiplier=args.multiplier,
        change_atr=args.change_atr,
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


def rma_series(values: list[float], period: int) -> list[float | None]:
    result: list[float | None] = []
    running_sum = 0.0
    previous: float | None = None

    for index, value in enumerate(values):
        running_sum += value
        if index < period - 1:
            result.append(None)
            continue
        if index == period - 1:
            previous = running_sum / period
        else:
            assert previous is not None
            previous = ((previous * (period - 1)) + value) / period
        result.append(previous)

    return result


def add_supertrend(candles: list[dict[str, Any]], config: SupertrendConfig) -> None:
    true_ranges = true_range_values(candles)
    atr_values = rma_series(true_ranges, config.atr_period) if config.change_atr else sma_series(
        true_ranges,
        config.atr_period,
    )

    trend = 1
    previous_up: float | None = None
    previous_dn: float | None = None
    previous_close: float | None = None

    for index, candle in enumerate(candles):
        atr = atr_values[index]
        previous_trend = trend
        signal = ""

        if atr is None:
            candle["ATR"] = ""
            candle["SUPER_UP"] = ""
            candle["SUPER_DN"] = ""
            candle["SUPER_TREND"] = trend
            candle["SUPER_SIGNAL"] = ""
            previous_close = float(candle["Close"])
            continue

        source = (float(candle["High"]) + float(candle["Low"])) / 2.0
        raw_up = source - (float(config.multiplier) * float(atr))
        raw_dn = source + (float(config.multiplier) * float(atr))

        up1 = previous_up if previous_up is not None else raw_up
        dn1 = previous_dn if previous_dn is not None else raw_dn
        if previous_close is not None and previous_close > up1:
            up = max(raw_up, up1)
        else:
            up = raw_up
        if previous_close is not None and previous_close < dn1:
            dn = min(raw_dn, dn1)
        else:
            dn = raw_dn

        close = float(candle["Close"])
        if trend == -1 and close > dn1:
            trend = 1
        elif trend == 1 and close < up1:
            trend = -1

        if trend == 1 and previous_trend == -1:
            signal = "BUY"
        elif trend == -1 and previous_trend == 1:
            signal = "SELL"

        candle["ATR"] = atr
        candle["SUPER_UP"] = up
        candle["SUPER_DN"] = dn
        candle["SUPER_TREND"] = trend
        candle["SUPER_SIGNAL"] = signal
        candle["SUPER_STOP"] = up if trend == 1 else dn

        previous_up = up
        previous_dn = dn
        previous_close = close


def session_key(candle: dict[str, Any]) -> str:
    return candle["dt"].date().isoformat()


def load_instrument_candles(
    path: Path,
    config: SupertrendConfig,
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

    add_supertrend(filtered, config)

    return filtered, {
        "market": base.market_name(path),
        "instrument": base.instrument_name(path),
        "file": str(path),
        "candles": len(filtered),
        "sessions": len({session_key(candle) for candle in filtered}),
        "signals": sum(1 for candle in filtered if candle.get("SUPER_SIGNAL")),
        "skipped_partial_sessions": skipped_partial_sessions,
    }


def build_session_last_indexes(candles: list[dict[str, Any]]) -> set[int]:
    last_indexes: set[int] = set()
    for index, candle in enumerate(candles):
        if index == len(candles) - 1 or session_key(candles[index + 1]) != session_key(candle):
            last_indexes.add(index)
    return last_indexes


def next_entry_index_same_session(candles: list[dict[str, Any]], signal_index: int) -> int | None:
    entry_index = signal_index + 1
    if entry_index >= len(candles):
        return None
    if session_key(candles[entry_index]) != session_key(candles[signal_index]):
        return None
    return entry_index


def direction_from_signal(signal: str, invert_signals: bool) -> str:
    if not invert_signals:
        return "LONG" if signal == "BUY" else "SHORT"
    return "SHORT" if signal == "BUY" else "LONG"


def stop_line_for_direction(candle: dict[str, Any], direction: str) -> float | None:
    key = "SUPER_UP" if direction == "LONG" else "SUPER_DN"
    value = candle.get(key)
    if value in (None, ""):
        return None
    return float(value)


def target_price(entry_price: float, risk: float, direction: str, level: int) -> float:
    if direction == "LONG":
        return entry_price + (risk * level)
    return entry_price - (risk * level)


def build_trade_at_entry(
    market: str,
    instrument: str,
    signal_candle: dict[str, Any],
    entry_candle: dict[str, Any],
    target_level: int,
    config: SupertrendConfig,
) -> dict[str, Any] | None:
    original_signal = str(signal_candle["SUPER_SIGNAL"])
    direction = direction_from_signal(original_signal, config.invert_signals)
    stop = stop_line_for_direction(signal_candle, direction)
    if stop is None:
        return None

    slippage_points = base.slippage_points_for_market(market, instrument, config)
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
    risk = abs(entry_price - stop_fill)
    if risk <= 0:
        return None

    risk_budget = config.capital * base.pct_to_decimal(config.risk_per_trade_pct)
    allocation_budget = config.capital * base.pct_to_decimal(config.max_allocation_pct)
    quantity = min(
        math.floor(risk_budget / risk),
        math.floor(allocation_budget / entry_price),
    )
    if quantity <= 0:
        return None

    targets = {
        level: target_price(entry_price, risk, direction, level)
        for level in range(1, max(5, target_level) + 1)
    }
    trade_signal = f"INVERSE_{original_signal}" if config.invert_signals else original_signal
    notional = entry_price * quantity

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
        "pine_entry_price": round(float(signal_candle["Close"]), 6),
        "entry_price": round(entry_price, 6),
        "initial_stop_price": round(stop, 6),
        "stop_price": round(stop, 6),
        "target_price": round(targets[target_level], 6),
        "tp1": round(targets.get(1, ""), 6) if 1 in targets else "",
        "tp2": round(targets.get(2, ""), 6) if 2 in targets else "",
        "tp3": round(targets.get(3, ""), 6) if 3 in targets else "",
        "tp4": round(targets.get(4, ""), 6) if 4 in targets else "",
        "tp5": round(targets.get(5, ""), 6) if 5 in targets else "",
        "atr": round(float(signal_candle["ATR"]), 6) if signal_candle.get("ATR") not in (None, "") else "",
        "supertrend_up": round(float(signal_candle["SUPER_UP"]), 6)
        if signal_candle.get("SUPER_UP") not in (None, "")
        else "",
        "supertrend_down": round(float(signal_candle["SUPER_DN"]), 6)
        if signal_candle.get("SUPER_DN") not in (None, "")
        else "",
        "supertrend_trend": signal_candle.get("SUPER_TREND", ""),
        "quantity": quantity,
        "notional": round(notional, 2),
        "position_risk_amount": round(risk * quantity, 2),
        "risk_per_unit": round(risk, 6),
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


def fill_pnl_values(
    trade: dict[str, Any],
    exit_candle: dict[str, Any],
    raw_exit_price: float,
    exit_reason: str,
    config: SupertrendConfig,
) -> dict[str, Any]:
    direction = str(trade["_direction"])
    slippage_points = float(trade.get("slippage_points", 0.0))
    exit_price = base.apply_exit_slippage(raw_exit_price, direction, slippage_points)
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
        str(trade["market"]),
        str(trade["instrument"]),
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


def target_hit(candle: dict[str, Any], direction: str, target: float) -> bool:
    if direction == "LONG":
        return float(candle["High"]) >= target
    return float(candle["Low"]) <= target


def stop_hit(candle: dict[str, Any], direction: str, stop: float) -> bool:
    if direction == "LONG":
        return float(candle["Low"]) <= stop
    return float(candle["High"]) >= stop


def update_trailing_stop(active: dict[str, Any], candle: dict[str, Any]) -> None:
    direction = str(active["_direction"])
    candidate = stop_line_for_direction(candle, direction)
    if candidate is None:
        return

    if direction == "LONG":
        active["_stop"] = max(float(active["_stop"]), candidate)
    else:
        active["_stop"] = min(float(active["_stop"]), candidate)
    active["stop_price"] = round(float(active["_stop"]), 6)


def manage_active_trade(
    active: dict[str, Any],
    candle: dict[str, Any],
    is_session_last: bool,
    target_level: int,
    config: SupertrendConfig,
) -> dict[str, Any] | None:
    direction = str(active["_direction"])
    update_trailing_stop(active, candle)
    stop = float(active["_stop"])
    target = float(active["_targets"][target_level])

    if target_hit(candle, direction, target):
        active["max_target_hit"] = max(int(active.get("max_target_hit", 0)), target_level)

    did_stop = stop_hit(candle, direction, stop)
    did_target = target_hit(candle, direction, target)
    if did_stop and did_target:
        if config.ambiguous_policy == "target_first":
            return fill_pnl_values(active, candle, target, f"TARGET_{target_level}", config)
        return fill_pnl_values(active, candle, stop, "STOP", config)
    if did_stop:
        return fill_pnl_values(active, candle, stop, "STOP", config)
    if did_target:
        return fill_pnl_values(active, candle, target, f"TARGET_{target_level}", config)
    if config.exit_at_session_end and is_session_last:
        return fill_pnl_values(active, candle, float(candle["Close"]), "SESSION_END", config)
    return None


def backtest_instrument(
    path: Path,
    target_level: int,
    config: SupertrendConfig,
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

        signal = candle.get("SUPER_SIGNAL")
        if signal not in {"BUY", "SELL"}:
            continue

        entry_index = next_entry_index_same_session(candles, index)
        if entry_index is None:
            skip_counts["signal_without_next_session_bar"] += 1
            continue

        candidate_direction = direction_from_signal(str(signal), config.invert_signals)
        if active is not None and candidate_direction != active["_direction"]:
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
    config: SupertrendConfig,
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
