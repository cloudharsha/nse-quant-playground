"""
Backtest a practical Smart Money Concepts strategy inspired by LuxAlgo SMC.

The source Pine file is an indicator, not a strategy, so this script converts
its actionable alerts into explicit backtest rules:

- Detect internal structure using a 5-bar SMC leg.
- Detect swing structure using a 50-bar SMC leg.
- Trade bullish/bearish BOS and CHoCH events.
- Use the event order block as stop when valid, otherwise ATR fallback.
- Enter on the next candle open after the signal candle closes.
- Exit on target, stop, opposite structure event, session end, or final bar.

The script runs the same signals across all selected timeframes in commodities,
derivatives, and equity, then writes a compact detailed summary into
common-strategies/results.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from dataclasses import dataclass, replace
from datetime import datetime, time
from pathlib import Path
from typing import Any

import open_low_high_5m_strategy as base


DEFAULT_TIMEFRAMES = ("5m", "15m", "30m", "1h")
AUTO_ALLOW_MISSING_SESSION_OPEN_TIMEFRAMES = frozenset({"30m"})
TIMEFRAME_ALIASES = {
    "5": "5m",
    "5m": "5m",
    "5min": "5m",
    "5minute": "5m",
    "5minutes": "5m",
    "15": "15m",
    "15m": "15m",
    "15min": "15m",
    "15minute": "15m",
    "15minutes": "15m",
    "30": "30m",
    "30m": "30m",
    "30min": "30m",
    "30minute": "30m",
    "30minutes": "30m",
    "60": "1h",
    "60m": "1h",
    "1h": "1h",
    "1hr": "1h",
    "1hour": "1h",
    "1hours": "1h",
}
TIMEFRAME_LABELS = {
    "5m": "5-minute candles",
    "15m": "15-minute candles",
    "30m": "30-minute candles",
    "1h": "1-hour candles",
}

BULLISH = 1
BEARISH = -1
NO_TREND = 0


@dataclass
class PivotState:
    current_level: float | None = None
    last_level: float | None = None
    crossed: bool = False
    bar_index: int = -1
    bar_time: str = ""


@dataclass
class StructureState:
    high: PivotState
    low: PivotState
    trend_bias: int = NO_TREND
    leg: int | None = None


@dataclass(frozen=True)
class SMCConfig:
    internal_length: int
    swing_length: int
    atr_period: int
    order_block_atr_period: int
    atr_multiplier: float
    stop_buffer_pct: float
    risk_reward: float
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
    variants: tuple[str, ...]
    top_trade_count: int


def normalize_timeframe(value: str) -> str:
    cleaned = value.strip().lower().replace("-", "").replace("_", "")
    cleaned = cleaned.replace(" ", "")
    timeframe = TIMEFRAME_ALIASES.get(cleaned)
    if timeframe is None:
        valid = ", ".join(DEFAULT_TIMEFRAMES)
        raise argparse.ArgumentTypeError(f"Unsupported timeframe {value!r}. Use one of: {valid}")
    return timeframe


def parse_timeframes(values: list[str]) -> tuple[str, ...]:
    seen: list[str] = []
    for value in values:
        timeframe = normalize_timeframe(value)
        if timeframe not in seen:
            seen.append(timeframe)
    return tuple(seen)


def timeframe_label(timeframe: str) -> str:
    return TIMEFRAME_LABELS.get(timeframe, timeframe)


def timeframe_sort_key(timeframe: str) -> tuple[int, str]:
    try:
        return DEFAULT_TIMEFRAMES.index(timeframe), timeframe
    except ValueError:
        return len(DEFAULT_TIMEFRAMES), timeframe


def config_for_timeframe(config: SMCConfig, timeframe: str) -> SMCConfig:
    if timeframe in AUTO_ALLOW_MISSING_SESSION_OPEN_TIMEFRAMES and config.require_session_open:
        return replace(config, require_session_open=False)
    return config


def build_timeframe_session_policy(
    timeframes: tuple[str, ...],
    base_config: SMCConfig,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for timeframe in timeframes:
        timeframe_config = config_for_timeframe(base_config, timeframe)
        rows.append(
            {
                "timeframe": timeframe,
                "session_start": (
                    timeframe_config.session_start.strftime("%H:%M")
                    if timeframe_config.session_start
                    else ""
                ),
                "exit_time": (
                    timeframe_config.exit_time.strftime("%H:%M")
                    if timeframe_config.exit_time
                    else ""
                ),
                "require_session_open": timeframe_config.require_session_open,
                "note": (
                    "30m Yahoo candles are aligned to 09:00/09:30, so the first available session candle is accepted."
                    if timeframe_config.require_session_open != base_config.require_session_open
                    else "Uses configured session-open rule."
                ),
            }
        )
    return rows


def discover_data_files_for_timeframe(
    repo_root: Path,
    markets: list[str],
    timeframe: str,
) -> list[Path]:
    files: list[Path] = []
    for market in markets:
        data_dir = repo_root / market / "data"
        if data_dir.exists():
            files.extend(sorted(data_dir.glob(f"*_{timeframe}.csv")))
    return sorted(files)


def instrument_name_for_timeframe(path: Path, timeframe: str) -> str:
    stem = path.stem
    for suffix in (
        f"_equity_data_{timeframe}",
        f"_data_{timeframe}",
        f"_{timeframe}",
    ):
        if stem.endswith(suffix):
            return stem[: -len(suffix)]
    return base.instrument_name(path)


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


def rolling_mean(values: list[float], period: int) -> list[float | None]:
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


def annotate_indicators(candles: list[dict[str, Any]], config: SMCConfig) -> None:
    true_ranges = true_range_values(candles)
    atr = rolling_mean(true_ranges, config.atr_period)
    order_block_atr = rolling_mean(true_ranges, config.order_block_atr_period)
    cumulative_range = 0.0

    for index, candle in enumerate(candles):
        cumulative_range += true_ranges[index]
        volatility_measure = order_block_atr[index]
        if volatility_measure is None:
            volatility_measure = cumulative_range / (index + 1)
        high_volatility = (float(candle["High"]) - float(candle["Low"])) >= (
            2.0 * volatility_measure
        )

        candle["ATR"] = atr[index]
        candle["ORDER_BLOCK_ATR"] = order_block_atr[index]
        candle["TRUE_RANGE"] = true_ranges[index]
        candle["PARSED_HIGH"] = float(candle["Low"]) if high_volatility else float(candle["High"])
        candle["PARSED_LOW"] = float(candle["High"]) if high_volatility else float(candle["Low"])
        candle["HIGH_VOLATILITY_BAR"] = high_volatility


def new_leg_for_index(
    candles: list[dict[str, Any]],
    index: int,
    size: int,
    previous_leg: int | None,
) -> int | None:
    if index < size:
        return previous_leg

    pivot_index = index - size
    candidate_high = float(candles[pivot_index]["High"])
    candidate_low = float(candles[pivot_index]["Low"])
    recent_high = max(float(candle["High"]) for candle in candles[pivot_index + 1 : index + 1])
    recent_low = min(float(candle["Low"]) for candle in candles[pivot_index + 1 : index + 1])

    if candidate_high > recent_high:
        return BEARISH
    if candidate_low < recent_low:
        return BULLISH
    return previous_leg


def update_structure_pivots(
    candles: list[dict[str, Any]],
    index: int,
    size: int,
    state: StructureState,
) -> None:
    current_leg = new_leg_for_index(candles, index, size, state.leg)
    if current_leg is None or state.leg is None:
        state.leg = current_leg
        return
    if current_leg == state.leg:
        return

    pivot_index = index - size
    pivot_candle = candles[pivot_index]
    if current_leg == BULLISH:
        pivot = state.low
        pivot.last_level = pivot.current_level
        pivot.current_level = float(pivot_candle["Low"])
        pivot.crossed = False
        pivot.bar_index = pivot_index
        pivot.bar_time = pivot_candle["dt"].isoformat()
    else:
        pivot = state.high
        pivot.last_level = pivot.current_level
        pivot.current_level = float(pivot_candle["High"])
        pivot.crossed = False
        pivot.bar_index = pivot_index
        pivot.bar_time = pivot_candle["dt"].isoformat()

    state.leg = current_leg


def crossed_above(previous_close: float, close: float, level: float) -> bool:
    return previous_close <= level and close > level


def crossed_below(previous_close: float, close: float, level: float) -> bool:
    return previous_close >= level and close < level


def order_block_from_range(
    candles: list[dict[str, Any]],
    start_index: int,
    end_index: int,
    direction: str,
) -> dict[str, Any] | None:
    if start_index < 0 or end_index <= start_index:
        return None

    segment = candles[start_index : end_index + 1]
    if not segment:
        return None

    if direction == "LONG":
        parsed_index, candle = min(
            enumerate(segment, start=start_index),
            key=lambda item: float(item[1]["PARSED_LOW"]),
        )
    else:
        parsed_index, candle = max(
            enumerate(segment, start=start_index),
            key=lambda item: float(item[1]["PARSED_HIGH"]),
        )

    summary = {
        "index": parsed_index,
        "time": candle["dt"].isoformat(),
        "high": float(candle["PARSED_HIGH"]),
        "low": float(candle["PARSED_LOW"]),
    }
    return summary


def structure_event(
    candles: list[dict[str, Any]],
    index: int,
    previous_close: float,
    state: StructureState,
    scope: str,
) -> dict[str, Any] | None:
    candle = candles[index]
    close = float(candle["Close"])

    high_pivot = state.high
    if (
        high_pivot.current_level is not None
        and not high_pivot.crossed
        and crossed_above(previous_close, close, high_pivot.current_level)
    ):
        tag = "CHoCH" if state.trend_bias == BEARISH else "BOS"
        state.trend_bias = BULLISH
        high_pivot.crossed = True
        order_block = order_block_from_range(
            candles,
            high_pivot.bar_index,
            index,
            "LONG",
        )
        return {
            "scope": scope,
            "tag": tag,
            "direction": "LONG",
            "signal": f"{scope.upper()}_BULLISH_{tag}",
            "pivot_level": high_pivot.current_level,
            "pivot_time": high_pivot.bar_time,
            "order_block": order_block,
        }

    low_pivot = state.low
    if (
        low_pivot.current_level is not None
        and not low_pivot.crossed
        and crossed_below(previous_close, close, low_pivot.current_level)
    ):
        tag = "CHoCH" if state.trend_bias == BULLISH else "BOS"
        state.trend_bias = BEARISH
        low_pivot.crossed = True
        order_block = order_block_from_range(
            candles,
            low_pivot.bar_index,
            index,
            "SHORT",
        )
        return {
            "scope": scope,
            "tag": tag,
            "direction": "SHORT",
            "signal": f"{scope.upper()}_BEARISH_{tag}",
            "pivot_level": low_pivot.current_level,
            "pivot_time": low_pivot.bar_time,
            "order_block": order_block,
        }

    return None


def detect_smc_events(
    candles: list[dict[str, Any]],
    config: SMCConfig,
) -> list[dict[str, Any]]:
    internal_state = StructureState(high=PivotState(), low=PivotState())
    swing_state = StructureState(high=PivotState(), low=PivotState())
    events: list[dict[str, Any]] = []

    for index, candle in enumerate(candles):
        update_structure_pivots(candles, index, config.internal_length, internal_state)
        update_structure_pivots(candles, index, config.swing_length, swing_state)

        if index == 0:
            continue

        previous_close = float(candles[index - 1]["Close"])
        for scope, state in (("internal", internal_state), ("swing", swing_state)):
            event = structure_event(candles, index, previous_close, state, scope)
            if event is not None:
                event.update(
                    {
                        "index": index,
                        "time": candle["dt"].isoformat(),
                        "session_date": candle["dt"].date().isoformat(),
                        "close": float(candle["Close"]),
                        "atr": candle.get("ATR"),
                    }
                )
                events.append(event)

    return events


def variant_accepts_event(variant: str, event: dict[str, Any]) -> bool:
    if variant == "internal_all":
        return event["scope"] == "internal"
    if variant == "internal_choch":
        return event["scope"] == "internal" and event["tag"] == "CHoCH"
    if variant == "swing_all":
        return event["scope"] == "swing"
    if variant == "swing_choch":
        return event["scope"] == "swing" and event["tag"] == "CHoCH"
    if variant == "combined_all":
        return event["scope"] in {"internal", "swing"}
    raise ValueError(f"Unknown variant: {variant}")


def apply_entry_slippage(price: float, direction: str, slippage_points: float) -> float:
    return base.apply_entry_slippage(price, direction, slippage_points)


def apply_exit_slippage(price: float, direction: str, slippage_points: float) -> float:
    return base.apply_exit_slippage(price, direction, slippage_points)


def stop_from_event(
    event: dict[str, Any],
    entry_price: float,
    direction: str,
    config: SMCConfig,
) -> tuple[float, str]:
    buffer = base.pct_to_decimal(config.stop_buffer_pct)
    order_block = event.get("order_block")
    if order_block:
        if direction == "LONG":
            stop = float(order_block["low"]) * (1.0 - buffer)
            if stop < entry_price:
                return stop, "order_block_low"
        else:
            stop = float(order_block["high"]) * (1.0 + buffer)
            if stop > entry_price:
                return stop, "order_block_high"

    atr = event.get("atr")
    if atr is None or atr <= 0:
        atr = abs(entry_price - float(event["pivot_level"]))
    risk = max(float(atr) * config.atr_multiplier, entry_price * 0.001)
    if direction == "LONG":
        return entry_price - risk, "atr_fallback"
    return entry_price + risk, "atr_fallback"


def target_from_stop(entry_price: float, stop_price: float, direction: str, risk_reward: float) -> float:
    risk = abs(entry_price - stop_price)
    if direction == "LONG":
        return entry_price + risk * risk_reward
    return entry_price - risk * risk_reward


def quantity_for_trade(
    entry_price: float,
    stop_price: float,
    direction: str,
    config: SMCConfig,
    slippage_points: float,
) -> int:
    stop_fill = apply_exit_slippage(stop_price, direction, slippage_points)
    risk_per_unit = abs(entry_price - stop_fill)
    if risk_per_unit <= 0:
        return 0

    risk_budget = config.capital * base.pct_to_decimal(config.risk_per_trade_pct)
    allocation_budget = config.capital * base.pct_to_decimal(config.max_allocation_pct)
    risk_qty = math.floor(risk_budget / risk_per_unit)
    allocation_qty = math.floor(allocation_budget / entry_price)
    return max(0, min(risk_qty, allocation_qty))


def hit_stop(candle: dict[str, Any], direction: str, stop_price: float) -> bool:
    if direction == "LONG":
        return float(candle["Low"]) <= stop_price
    return float(candle["High"]) >= stop_price


def hit_target(candle: dict[str, Any], direction: str, target_price: float) -> bool:
    if direction == "LONG":
        return float(candle["High"]) >= target_price
    return float(candle["Low"]) <= target_price


def opposite_direction(direction: str) -> str:
    return "SHORT" if direction == "LONG" else "LONG"


def charge_breakdown_for_trade(
    entry_price: float,
    exit_price: float,
    quantity: int,
    market: str,
    instrument: str,
    config: SMCConfig,
) -> dict[str, Any]:
    segment = base.charge_segment_for_market(market, instrument)
    return base.charge_breakdown_for_segment(
        abs(entry_price) * quantity,
        abs(exit_price) * quantity,
        segment,
        float(config.cost_multiplier),
    )


def close_trade(
    trade: dict[str, Any],
    candle: dict[str, Any],
    raw_exit_price: float,
    exit_reason: str,
    config: SMCConfig,
) -> dict[str, Any]:
    direction = trade["direction"]
    entry_price = float(trade["entry_price"])
    slippage_points = float(trade.get("slippage_points", 0.0))
    exit_price = apply_exit_slippage(raw_exit_price, direction, slippage_points)
    quantity = int(trade["quantity"])

    if direction == "LONG":
        gross_pnl = (exit_price - entry_price) * quantity
    else:
        gross_pnl = (entry_price - exit_price) * quantity

    charges = charge_breakdown_for_trade(
        entry_price,
        exit_price,
        quantity,
        trade["market"],
        trade["instrument"],
        config,
    )
    costs = float(charges["total"])
    net_pnl = gross_pnl - costs
    risk_amount = float(trade["position_risk_amount"])
    notional = float(trade["notional"])

    trade.update(
        {
            "exit_time": candle["dt"].isoformat(),
            "exit_price": round(exit_price, 6),
            "exit_reason": exit_reason,
            "gross_pnl": round(gross_pnl, 2),
            "costs": round(costs, 2),
            "charge_segment": charges["segment"],
            "charge_segment_label": charges["segment_label"],
            "turnover": charges["turnover"],
            "brokerage": charges["brokerage"],
            "stt": charges.get("stt", 0.0),
            "ctt": charges.get("ctt", 0.0),
            "exchange_charge": charges["exchange_charge"],
            "gst": charges["gst"],
            "sebi_charges": charges["sebi_charges"],
            "stamp_duty": charges["stamp_duty"],
            "net_pnl": round(net_pnl, 2),
            "return_pct_on_notional": round((net_pnl / notional) * 100.0, 4)
            if notional > 0
            else 0.0,
            "r_multiple": round(net_pnl / risk_amount, 4) if risk_amount > 0 else 0.0,
        }
    )
    return trade


def is_session_last(candles: list[dict[str, Any]], index: int) -> bool:
    if index >= len(candles) - 1:
        return True
    return candles[index]["dt"].date() != candles[index + 1]["dt"].date()


def event_by_index(events: list[dict[str, Any]], variant: str) -> dict[int, list[dict[str, Any]]]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        if variant_accepts_event(variant, event):
            grouped[int(event["index"])].append(event)
    return grouped


def build_trade(
    market: str,
    instrument: str,
    timeframe: str,
    variant: str,
    event: dict[str, Any],
    entry_candle: dict[str, Any],
    config: SMCConfig,
) -> dict[str, Any] | None:
    direction = event["direction"]
    slippage_points = base.slippage_points_for_market(market, instrument, config)
    entry_price = apply_entry_slippage(
        float(entry_candle["Open"]),
        direction,
        slippage_points,
    )
    stop_price, stop_source = stop_from_event(event, entry_price, direction, config)
    if direction == "LONG" and stop_price >= entry_price:
        return None
    if direction == "SHORT" and stop_price <= entry_price:
        return None

    quantity = quantity_for_trade(entry_price, stop_price, direction, config, slippage_points)
    if quantity <= 0:
        return None

    target_price = target_from_stop(entry_price, stop_price, direction, config.risk_reward)
    stop_fill = apply_exit_slippage(stop_price, direction, slippage_points)
    position_risk = abs(entry_price - stop_fill) * quantity
    notional = entry_price * quantity
    order_block = event.get("order_block") or {}

    return {
        "variant": variant,
        "timeframe": timeframe,
        "market": market,
        "instrument": instrument,
        "session_date": entry_candle["dt"].date().isoformat(),
        "signal": event["signal"],
        "scope": event["scope"],
        "structure_tag": event["tag"],
        "direction": direction,
        "signal_time": event["time"],
        "entry_time": entry_candle["dt"].isoformat(),
        "entry_price": round(entry_price, 6),
        "pivot_level": round(float(event["pivot_level"]), 6),
        "pivot_time": event["pivot_time"],
        "stop_price": round(stop_price, 6),
        "stop_source": stop_source,
        "target_price": round(target_price, 6),
        "risk_reward": config.risk_reward,
        "atr_at_signal": round(float(event["atr"]), 6) if event.get("atr") else "",
        "order_block_high": round(float(order_block["high"]), 6) if order_block else "",
        "order_block_low": round(float(order_block["low"]), 6) if order_block else "",
        "order_block_time": order_block.get("time", "") if order_block else "",
        "quantity": quantity,
        "notional": round(notional, 2),
        "position_risk_amount": round(position_risk, 2),
        "slippage_points": round(slippage_points, 6),
        "holding_candles": 0,
        "_entry_index": int(entry_candle["_index"]),
    }


def public_trade(trade: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in trade.items() if not key.startswith("_")}


def backtest_instrument_variant(
    path: Path,
    timeframe: str,
    variant: str,
    config: SMCConfig,
    skip_counts: dict[str, int],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    market = base.market_name(path)
    instrument = instrument_name_for_timeframe(path, timeframe)
    raw_candles = base.load_candles(path)
    sessions = base.group_sessions(raw_candles, config.session_start, config.exit_time)

    candles: list[dict[str, Any]] = []
    skipped_partial_sessions = 0
    for session_date in sorted(sessions):
        session = sessions[session_date]
        if (
            config.session_start is not None
            and config.require_session_open
            and session[0]["dt"].time() != config.session_start
        ):
            skipped_partial_sessions += 1
            continue
        candles.extend(session)

    for index, candle in enumerate(candles):
        candle["_index"] = index

    annotate_indicators(candles, config)
    events = detect_smc_events(candles, config)
    events_for_variant = event_by_index(events, variant)
    trades: list[dict[str, Any]] = []
    active_trade: dict[str, Any] | None = None
    pending_event: dict[str, Any] | None = None

    for index, candle in enumerate(candles):
        if pending_event is not None and int(pending_event["index"]) == index - 1:
            if candle["dt"].date().isoformat() != pending_event["session_date"]:
                skip_counts["signal_without_next_session_bar"] += 1
            else:
                active_trade = build_trade(
                    market,
                    instrument,
                    timeframe,
                    variant,
                    pending_event,
                    candle,
                    config,
                )
                if active_trade is None:
                    skip_counts["invalid_or_unsized_entry"] += 1
            pending_event = None

        if active_trade is not None:
            active_trade["holding_candles"] = index - int(active_trade["_entry_index"]) + 1
            did_stop = hit_stop(candle, active_trade["direction"], float(active_trade["stop_price"]))
            did_target = hit_target(
                candle,
                active_trade["direction"],
                float(active_trade["target_price"]),
            )

            if did_stop and did_target:
                if config.ambiguous_policy == "target_first":
                    trades.append(
                        public_trade(
                            close_trade(
                                active_trade,
                                candle,
                                float(active_trade["target_price"]),
                                "TARGET_AND_STOP_SAME_CANDLE_TARGET_FIRST",
                                config,
                            )
                        )
                    )
                else:
                    trades.append(
                        public_trade(
                            close_trade(
                                active_trade,
                                candle,
                                float(active_trade["stop_price"]),
                                "TARGET_AND_STOP_SAME_CANDLE_STOP_FIRST",
                                config,
                            )
                        )
                    )
                active_trade = None
                continue

            if did_stop:
                trades.append(
                    public_trade(
                        close_trade(
                            active_trade,
                            candle,
                            float(active_trade["stop_price"]),
                            "STOP_LOSS",
                            config,
                        )
                    )
                )
                active_trade = None
                continue

            if did_target:
                trades.append(
                    public_trade(
                        close_trade(
                            active_trade,
                            candle,
                            float(active_trade["target_price"]),
                            "TARGET",
                            config,
                        )
                    )
                )
                active_trade = None
                continue

            if config.exit_at_session_end and is_session_last(candles, index):
                trades.append(
                    public_trade(
                        close_trade(
                            active_trade,
                            candle,
                            float(candle["Close"]),
                            "SESSION_END",
                            config,
                        )
                    )
                )
                active_trade = None
                continue

        current_events = events_for_variant.get(index, [])
        if not current_events:
            continue

        event = current_events[-1]
        if active_trade is not None and event["direction"] == opposite_direction(active_trade["direction"]):
            next_index = index + 1
            if next_index < len(candles) and candles[next_index]["dt"].date() == candle["dt"].date():
                exit_candle = candles[next_index]
                trades.append(
                    public_trade(
                        close_trade(
                            active_trade,
                            exit_candle,
                            float(exit_candle["Open"]),
                            "OPPOSITE_STRUCTURE",
                            config,
                        )
                    )
                )
                active_trade = None
            else:
                skip_counts["opposite_signal_without_next_session_bar"] += 1

        if active_trade is None:
            pending_event = event

    if active_trade is not None and candles:
        trades.append(
            public_trade(
                close_trade(
                    active_trade,
                    candles[-1],
                    float(candles[-1]["Close"]),
                    "FINAL_BAR",
                    config,
                )
            )
        )

    stats = {
        "timeframe": timeframe,
        "market": market,
        "instrument": instrument,
        "file": str(path),
        "candles": len(candles),
        "sessions": len({candle["dt"].date().isoformat() for candle in candles}),
        "events": sum(1 for event in events if variant_accepts_event(variant, event)),
        "trades": len(trades),
        "skipped_partial_sessions": skipped_partial_sessions,
    }
    return trades, stats


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


def sharpe_ratio(datewise_rows: list[dict[str, Any]]) -> float | None:
    return base.sharpe_ratio(datewise_rows)


def max_drawdown(equity_rows: list[dict[str, Any]], starting_capital: float) -> tuple[float, float]:
    equity_values = [starting_capital] + [float(row["equity"]) for row in equity_rows]
    return base.max_drawdown_from_equity(equity_values)


def profit_factor_from_values(values: list[float]) -> float | str:
    gross_profit = sum(max(value, 0.0) for value in values)
    gross_loss = abs(sum(min(value, 0.0) for value in values))
    if gross_loss == 0:
        return "inf" if gross_profit > 0 else ""
    return gross_profit / gross_loss


def build_summary(
    timeframe: str,
    variant: str,
    trades: list[dict[str, Any]],
    file_stats: list[dict[str, Any]],
    skip_counts: dict[str, int],
    config: SMCConfig,
) -> dict[str, Any]:
    datewise_rows = base.build_datewise_pnl(trades, config.capital)
    equity_rows = base.build_equity_curve(trades, config.capital)
    gross_values = [float(trade["gross_pnl"]) for trade in trades]
    net_values = [float(trade["net_pnl"]) for trade in trades]
    wins = [value for value in net_values if value > 0]
    losses = [value for value in net_values if value <= 0]
    gross_wins = [value for value in gross_values if value > 0]
    gross_losses = [value for value in gross_values if value <= 0]
    pf = base.profit_factor(trades)
    gross_pf = profit_factor_from_values(gross_values)
    max_dd, max_dd_pct = max_drawdown(equity_rows, config.capital)
    sharpe = sharpe_ratio(datewise_rows)
    trade_dates = sorted({trade["session_date"] for trade in trades})
    traded_instruments = sorted(
        {f"{trade['market']}:{trade['instrument']}:{timeframe}" for trade in trades}
    )
    tested_instruments = sorted(
        {f"{item['market']}:{item['instrument']}:{timeframe}" for item in file_stats}
    )
    total_costs = sum(float(trade["costs"]) for trade in trades)
    total_turnover = sum(float(trade.get("turnover", 0.0)) for trade in trades)
    total_notional = sum(float(trade.get("notional", 0.0)) for trade in trades)

    summary = {
        "strategy": "Smart Money Concepts [LuxAlgo] inspired multi-timeframe backtest",
        "timeframe": timeframe,
        "timeframe_label": timeframe_label(timeframe),
        "variant": variant,
        "starting_capital": round(config.capital, 2),
        "ending_equity_without_brokerage": round(config.capital + sum(gross_values), 2),
        "ending_equity_with_brokerage": round(config.capital + sum(net_values), 2),
        "ending_equity": round(config.capital + sum(net_values), 2),
        "gross_pnl_before_brokerage": round(sum(gross_values), 2),
        "brokerage_and_charges": round(total_costs, 2),
        "total_costs": round(total_costs, 2),
        "net_pnl_after_brokerage": round(sum(net_values), 2),
        "total_profit_loss": round(sum(net_values), 2),
        "net_pnl": round(sum(net_values), 2),
        "total_trades": len(trades),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate_pct": round((len(wins) / len(trades)) * 100.0, 2) if trades else 0.0,
        "gross_wins": len(gross_wins),
        "gross_losses": len(gross_losses),
        "gross_win_rate_pct": round((len(gross_wins) / len(trades)) * 100.0, 2)
        if trades
        else 0.0,
        "average_profit_loss": round(statistics.mean(net_values), 2) if net_values else 0.0,
        "average_gross_profit_loss": round(statistics.mean(gross_values), 2)
        if gross_values
        else 0.0,
        "average_cost_per_trade": round(total_costs / len(trades), 2) if trades else 0.0,
        "average_win": round(statistics.mean(wins), 2) if wins else 0.0,
        "average_loss": round(statistics.mean(losses), 2) if losses else 0.0,
        "max_drawdown": round(max_dd, 2),
        "max_drawdown_pct": round(max_dd_pct, 4),
        "profit_factor": round(pf, 4) if isinstance(pf, float) else pf,
        "gross_profit_factor": round(gross_pf, 4) if isinstance(gross_pf, float) else gross_pf,
        "sharpe_ratio": round(sharpe, 4) if sharpe is not None else "",
        "total_turnover": round(total_turnover, 2),
        "total_entry_notional": round(total_notional, 2),
        "markets_tested": ",".join(sorted({item["market"] for item in file_stats})),
        "files_tested": len(file_stats),
        "sessions_tested": sum(int(item["sessions"]) for item in file_stats),
        "candles_tested": sum(int(item["candles"]) for item in file_stats),
        "events_tested": sum(int(item["events"]) for item in file_stats),
        "trade_start_date": trade_dates[0] if trade_dates else "",
        "trade_end_date": trade_dates[-1] if trade_dates else "",
        "trade_timeframe": timeframe_label(timeframe),
        "traded_instrument_count": len(traded_instruments),
        "tested_instrument_count": len(tested_instruments),
        "traded_instruments": ",".join(traded_instruments),
        "tested_instruments": ",".join(tested_instruments),
        "skip_counts": dict(sorted(skip_counts.items())),
    }
    summary.update(base.cost_model_summary(config))
    return summary


def comparison_row(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "timeframe": summary["timeframe"],
        "variant": summary["variant"],
        "files_tested": summary["files_tested"],
        "sessions_tested": summary["sessions_tested"],
        "candles_tested": summary["candles_tested"],
        "events_tested": summary["events_tested"],
        "total_trades": summary["total_trades"],
        "gross_pnl_before_brokerage": summary["gross_pnl_before_brokerage"],
        "brokerage_and_charges": summary["brokerage_and_charges"],
        "net_pnl_after_brokerage": summary["net_pnl_after_brokerage"],
        "win_rate_pct": summary["win_rate_pct"],
        "net_pnl": summary["net_pnl"],
        "ending_equity": summary["ending_equity"],
        "total_costs": summary["total_costs"],
        "max_drawdown": summary["max_drawdown"],
        "max_drawdown_pct": summary["max_drawdown_pct"],
        "profit_factor": summary["profit_factor"],
        "sharpe_ratio": summary["sharpe_ratio"],
    }


def sum_trade_value(trades: list[dict[str, Any]], key: str) -> float:
    return sum(float(trade.get(key, 0.0) or 0.0) for trade in trades)


def build_instrument_rows(trades: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for trade in trades:
        grouped[
            (
                str(trade["timeframe"]),
                str(trade["variant"]),
                str(trade["market"]),
                str(trade["instrument"]),
            )
        ].append(trade)

    rows: list[dict[str, Any]] = []
    for (timeframe, variant, market, instrument), group_trades in sorted(
        grouped.items(),
        key=lambda item: (timeframe_sort_key(item[0][0]), item[0][1], item[0][2], item[0][3]),
    ):
        net_values = [float(trade["net_pnl"]) for trade in group_trades]
        wins = [value for value in net_values if value > 0]
        rows.append(
            {
                "timeframe": timeframe,
                "variant": variant,
                "market": market,
                "instrument": instrument,
                "trades": len(group_trades),
                "long_trades": sum(1 for trade in group_trades if trade["direction"] == "LONG"),
                "short_trades": sum(1 for trade in group_trades if trade["direction"] == "SHORT"),
                "gross_pnl_before_brokerage": round(sum_trade_value(group_trades, "gross_pnl"), 2),
                "brokerage_and_charges": round(sum_trade_value(group_trades, "costs"), 2),
                "net_pnl_after_brokerage": round(sum(net_values), 2),
                "win_rate_pct": round((len(wins) / len(group_trades)) * 100.0, 2)
                if group_trades
                else 0.0,
                "average_net_pnl": round(statistics.mean(net_values), 2) if net_values else 0.0,
                "best_trade": round(max(net_values), 2) if net_values else 0.0,
                "worst_trade": round(min(net_values), 2) if net_values else 0.0,
                "turnover": round(sum_trade_value(group_trades, "turnover"), 2),
                "entry_notional": round(sum_trade_value(group_trades, "notional"), 2),
            }
        )
    return rows


def build_charge_rows(trades: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for trade in trades:
        grouped[
            (
                str(trade["timeframe"]),
                str(trade["variant"]),
                str(trade.get("charge_segment", "")),
                str(trade.get("charge_segment_label", "")),
            )
        ].append(trade)

    rows: list[dict[str, Any]] = []
    for (timeframe, variant, segment, label), group_trades in sorted(
        grouped.items(),
        key=lambda item: (timeframe_sort_key(item[0][0]), item[0][1], item[0][2], item[0][3]),
    ):
        turnover = sum_trade_value(group_trades, "turnover")
        total = sum_trade_value(group_trades, "costs")
        rows.append(
            {
                "timeframe": timeframe,
                "variant": variant,
                "segment": segment,
                "segment_label": label,
                "trades": len(group_trades),
                "turnover": round(turnover, 2),
                "brokerage": round(sum_trade_value(group_trades, "brokerage"), 2),
                "stt": round(sum_trade_value(group_trades, "stt"), 2),
                "ctt": round(sum_trade_value(group_trades, "ctt"), 2),
                "exchange_charge": round(sum_trade_value(group_trades, "exchange_charge"), 2),
                "gst": round(sum_trade_value(group_trades, "gst"), 2),
                "sebi_charges": round(sum_trade_value(group_trades, "sebi_charges"), 2),
                "stamp_duty": round(sum_trade_value(group_trades, "stamp_duty"), 2),
                "total_charges": round(total, 2),
                "charge_pct_of_turnover": round((total / turnover) * 100.0, 4)
                if turnover
                else 0.0,
            }
        )
    return rows


def build_direction_exit_rows(trades: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for trade in trades:
        grouped[
            (
                str(trade["timeframe"]),
                str(trade["variant"]),
                str(trade["direction"]),
                str(trade["exit_reason"]),
            )
        ].append(trade)

    rows: list[dict[str, Any]] = []
    for (timeframe, variant, direction, exit_reason), group_trades in sorted(
        grouped.items(),
        key=lambda item: (timeframe_sort_key(item[0][0]), item[0][1], item[0][2], item[0][3]),
    ):
        rows.append(
            {
                "timeframe": timeframe,
                "variant": variant,
                "direction": direction,
                "exit_reason": exit_reason,
                "trades": len(group_trades),
                "gross_pnl_before_brokerage": round(sum_trade_value(group_trades, "gross_pnl"), 2),
                "brokerage_and_charges": round(sum_trade_value(group_trades, "costs"), 2),
                "net_pnl_after_brokerage": round(sum_trade_value(group_trades, "net_pnl"), 2),
            }
        )
    return rows


def build_skip_rows(run_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for result in run_results:
        if not result.get("success"):
            rows.append(
                {
                    "timeframe": result["timeframe"],
                    "variant": result.get("variant", ""),
                    "reason": "run_failed",
                    "count": result.get("error", ""),
                }
            )
            continue
        summary = result["summary"]
        for reason, count in summary.get("skip_counts", {}).items():
            rows.append(
                {
                    "timeframe": result["timeframe"],
                    "variant": result["variant"],
                    "reason": reason,
                    "count": count,
                }
            )
    return rows


def build_best_worst_trade_rows(
    trades: list[dict[str, Any]],
    count: int,
) -> list[dict[str, Any]]:
    if not trades or count <= 0:
        return []

    rows: list[dict[str, Any]] = []
    for rank_type, ordered in (
        ("BEST", sorted(trades, key=lambda trade: float(trade["net_pnl"]), reverse=True)),
        ("WORST", sorted(trades, key=lambda trade: float(trade["net_pnl"]))),
    ):
        for rank, trade in enumerate(ordered[:count], start=1):
            rows.append(
                {
                    "rank_type": rank_type,
                    "rank": rank,
                    "timeframe": trade["timeframe"],
                    "variant": trade["variant"],
                    "market": trade["market"],
                    "instrument": trade["instrument"],
                    "session_date": trade["session_date"],
                    "direction": trade["direction"],
                    "signal": trade["signal"],
                    "exit_reason": trade["exit_reason"],
                    "quantity": trade["quantity"],
                    "entry_price": trade["entry_price"],
                    "exit_price": trade["exit_price"],
                    "gross_pnl_before_brokerage": trade["gross_pnl"],
                    "brokerage_and_charges": trade["costs"],
                    "net_pnl_after_brokerage": trade["net_pnl"],
                }
            )
    return rows


def build_best_by_timeframe_rows(comparison_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in comparison_rows:
        grouped[str(row["timeframe"])].append(row)

    rows: list[dict[str, Any]] = []
    for timeframe, timeframe_rows in sorted(
        grouped.items(),
        key=lambda item: timeframe_sort_key(item[0]),
    ):
        best = max(timeframe_rows, key=lambda row: float(row["net_pnl_after_brokerage"]))
        rows.append(
            {
                "timeframe": timeframe,
                "best_variant": best["variant"],
                "trades": best["total_trades"],
                "gross_pnl_before_brokerage": best["gross_pnl_before_brokerage"],
                "brokerage_and_charges": best["brokerage_and_charges"],
                "net_pnl_after_brokerage": best["net_pnl_after_brokerage"],
                "win_rate_pct": best["win_rate_pct"],
                "profit_factor": best["profit_factor"],
            }
        )
    return rows


def markdown_cell(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|")


def append_markdown_table(
    lines: list[str],
    rows: list[dict[str, Any]],
    columns: list[tuple[str, str]],
) -> None:
    if not rows:
        lines.append("_None._")
        return

    lines.append("| " + " | ".join(label for label, _ in columns) + " |")
    lines.append("| " + " | ".join("---" for _ in columns) + " |")
    for row in rows:
        lines.append(
            "| "
            + " | ".join(markdown_cell(row.get(key, "")) for _, key in columns)
            + " |"
        )


def write_summary_markdown(
    path: Path,
    payload: dict[str, Any],
    config: SMCConfig,
    output_files: list[Path],
) -> None:
    comparison_rows = payload["timeframe_variant_summary"]
    best_by_timeframe_rows = payload["best_by_timeframe"]
    instrument_rows = payload["what_traded_by_instrument"]
    charge_rows = payload["brokerage_by_segment"]
    direction_exit_rows = payload["direction_exit_summary"]
    best_worst_rows = payload["best_worst_trades"]
    skip_rows = payload["skipped_signals"]
    failed_runs = [result for result in payload["runs"] if not result.get("success")]
    best_net = (
        max(comparison_rows, key=lambda row: float(row["net_pnl_after_brokerage"]))
        if comparison_rows
        else {}
    )
    best_gross = (
        max(comparison_rows, key=lambda row: float(row["gross_pnl_before_brokerage"]))
        if comparison_rows
        else {}
    )

    lines = [
        "# Smart Money Concepts [LuxAlgo] Multi-Timeframe Backtest",
        "",
        "## Executive Summary",
        "",
        f"- **generated_at**: {payload['generated_at']}",
        f"- **markets_tested**: {', '.join(payload['markets'])}",
        f"- **timeframes_tested**: {', '.join(payload['timeframes'])}",
        f"- **variants_tested**: {', '.join(payload['variants'])}",
        f"- **starting_capital**: {config.capital}",
        f"- **best_after_brokerage**: {best_net.get('timeframe', '')} / "
        f"{best_net.get('variant', '')} = {best_net.get('net_pnl_after_brokerage', '')}",
        f"- **best_before_brokerage**: {best_gross.get('timeframe', '')} / "
        f"{best_gross.get('variant', '')} = {best_gross.get('gross_pnl_before_brokerage', '')}",
        "- **pnl_note**: Before Brokerage includes configured slippage; After Brokerage subtracts segment-wise brokerage, taxes, and charges.",
        "",
        "## Timeframe And Variant Results",
        "",
    ]
    append_markdown_table(
        lines,
        comparison_rows,
        [
            ("Timeframe", "timeframe"),
            ("Variant", "variant"),
            ("Files", "files_tested"),
            ("Events", "events_tested"),
            ("Trades", "total_trades"),
            ("Before Brokerage", "gross_pnl_before_brokerage"),
            ("Brokerage/Charges", "brokerage_and_charges"),
            ("After Brokerage", "net_pnl_after_brokerage"),
            ("Win %", "win_rate_pct"),
            ("Max DD %", "max_drawdown_pct"),
            ("PF", "profit_factor"),
            ("Sharpe", "sharpe_ratio"),
        ],
    )

    lines.extend(["", "## Best Variant Per Timeframe", ""])
    append_markdown_table(
        lines,
        best_by_timeframe_rows,
        [
            ("Timeframe", "timeframe"),
            ("Best Variant", "best_variant"),
            ("Trades", "trades"),
            ("Before Brokerage", "gross_pnl_before_brokerage"),
            ("Brokerage/Charges", "brokerage_and_charges"),
            ("After Brokerage", "net_pnl_after_brokerage"),
            ("Win %", "win_rate_pct"),
            ("PF", "profit_factor"),
        ],
    )

    lines.extend(["", "## What Was Traded", ""])
    append_markdown_table(
        lines,
        instrument_rows,
        [
            ("Timeframe", "timeframe"),
            ("Variant", "variant"),
            ("Market", "market"),
            ("Instrument", "instrument"),
            ("Trades", "trades"),
            ("Long", "long_trades"),
            ("Short", "short_trades"),
            ("Before Brokerage", "gross_pnl_before_brokerage"),
            ("Charges", "brokerage_and_charges"),
            ("After Brokerage", "net_pnl_after_brokerage"),
            ("Win %", "win_rate_pct"),
        ],
    )

    lines.extend(["", "## Brokerage And Charges", ""])
    append_markdown_table(
        lines,
        charge_rows,
        [
            ("Timeframe", "timeframe"),
            ("Variant", "variant"),
            ("Segment", "segment_label"),
            ("Trades", "trades"),
            ("Turnover", "turnover"),
            ("Brokerage", "brokerage"),
            ("STT", "stt"),
            ("CTT", "ctt"),
            ("Exchange", "exchange_charge"),
            ("GST", "gst"),
            ("SEBI", "sebi_charges"),
            ("Stamp", "stamp_duty"),
            ("Total", "total_charges"),
        ],
    )

    lines.extend(["", "## Direction And Exit Summary", ""])
    append_markdown_table(
        lines,
        direction_exit_rows,
        [
            ("Timeframe", "timeframe"),
            ("Variant", "variant"),
            ("Direction", "direction"),
            ("Exit", "exit_reason"),
            ("Trades", "trades"),
            ("Before Brokerage", "gross_pnl_before_brokerage"),
            ("Charges", "brokerage_and_charges"),
            ("After Brokerage", "net_pnl_after_brokerage"),
        ],
    )

    lines.extend(["", "## Best And Worst Trades", ""])
    append_markdown_table(
        lines,
        best_worst_rows,
        [
            ("Rank Type", "rank_type"),
            ("Rank", "rank"),
            ("Timeframe", "timeframe"),
            ("Variant", "variant"),
            ("Market", "market"),
            ("Instrument", "instrument"),
            ("Date", "session_date"),
            ("Direction", "direction"),
            ("Exit", "exit_reason"),
            ("Before Brokerage", "gross_pnl_before_brokerage"),
            ("Charges", "brokerage_and_charges"),
            ("After Brokerage", "net_pnl_after_brokerage"),
        ],
    )

    lines.extend(["", "## Cost Model", ""])
    for key, value in base.cost_model_summary(config).items():
        lines.append(f"- **{key}**: {value}")

    lines.extend(["", "## Timeframe Session Policy", ""])
    append_markdown_table(
        lines,
        payload.get("timeframe_session_policy", []),
        [
            ("Timeframe", "timeframe"),
            ("Session Start", "session_start"),
            ("Exit Time", "exit_time"),
            ("Require Session Open", "require_session_open"),
            ("Note", "note"),
        ],
    )

    lines.extend(
        [
            "",
            "## Backtest Rules",
            "",
            "- Structure events are based on the LuxAlgo SMC BOS/CHoCH alert logic.",
            "- Internal structure uses the configured internal leg length; swing structure uses the configured swing leg length.",
            "- Entry happens at the next candle open after a signal candle closes.",
            "- Stop-loss uses the event order block when valid, otherwise ATR fallback.",
            "- Target uses fixed risk/reward from the entry to stop distance.",
            "- Trades exit on target, stop, opposite structure event, session end, or final bar.",
            "- Same-candle target/stop ambiguity uses the configured ambiguous policy.",
            "",
            "## Variant Meaning",
            "",
            "- `internal_all`: internal BOS and internal CHoCH events.",
            "- `internal_choch`: internal CHoCH events only.",
            "- `swing_all`: swing BOS and swing CHoCH events.",
            "- `swing_choch`: swing CHoCH events only.",
            "- `combined_all`: internal and swing BOS/CHoCH events.",
            "",
            "## Skipped Signals",
            "",
        ]
    )
    append_markdown_table(
        lines,
        skip_rows,
        [
            ("Timeframe", "timeframe"),
            ("Variant", "variant"),
            ("Reason", "reason"),
            ("Count", "count"),
        ],
    )

    if failed_runs:
        lines.extend(["", "## Failed Runs", ""])
        append_markdown_table(
            lines,
            failed_runs,
            [
                ("Timeframe", "timeframe"),
                ("Variant", "variant"),
                ("Error", "error"),
            ],
        )

    lines.extend(["", "## Parameters", ""])
    for key, value in config.__dict__.items():
        if isinstance(value, time):
            value = value.strftime("%H:%M")
        lines.append(f"- **{key}**: {value}")

    lines.extend(["", "## Output Files", ""])
    for output_file in output_files:
        lines.append(f"- `{output_file.name}`")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_variants(values: list[str]) -> tuple[str, ...]:
    valid = {"internal_all", "internal_choch", "swing_all", "swing_choch", "combined_all"}
    invalid = [value for value in values if value not in valid]
    if invalid:
        raise argparse.ArgumentTypeError(f"Invalid variants: {', '.join(invalid)}")
    return tuple(values)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backtest Smart Money Concepts [LuxAlgo]-inspired strategy across timeframes.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--timeframes",
        nargs="+",
        default=list(DEFAULT_TIMEFRAMES),
        help="Timeframes to test. Accepts 5m/15m/30m/1h or 5/15/30/60.",
    )
    parser.add_argument(
        "--markets",
        nargs="+",
        choices=base.MARKETS,
        default=list(base.MARKETS),
    )
    parser.add_argument("--internal-length", type=int, default=5)
    parser.add_argument("--swing-length", type=int, default=50)
    parser.add_argument("--atr-period", type=int, default=14)
    parser.add_argument("--order-block-atr-period", type=int, default=200)
    parser.add_argument("--atr-multiplier", type=float, default=1.5)
    parser.add_argument("--stop-buffer-pct", type=float, default=0.02)
    parser.add_argument("--risk-reward", type=float, default=2.0)
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
    parser.add_argument(
        "--variants",
        nargs="+",
        default=["internal_all", "swing_all", "combined_all"],
        help="Variants: internal_all internal_choch swing_all swing_choch combined_all",
    )
    parser.add_argument("--top-trade-count", type=int, default=10)
    parser.add_argument("--run-name", default="")
    parser.add_argument(
        "--write-trade-audit",
        action="store_true",
        help="Also write one all_trades.csv audit file. Default keeps output to summaries only.",
    )
    return parser.parse_args()


def config_from_args(args: argparse.Namespace) -> SMCConfig:
    return SMCConfig(
        internal_length=args.internal_length,
        swing_length=args.swing_length,
        atr_period=args.atr_period,
        order_block_atr_period=args.order_block_atr_period,
        atr_multiplier=args.atr_multiplier,
        stop_buffer_pct=args.stop_buffer_pct,
        risk_reward=args.risk_reward,
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
        variants=parse_variants(args.variants),
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
    timeframes = parse_timeframes(args.timeframes)
    config = config_from_args(args)

    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[2]
    common_root = script_path.parents[1]
    results_root = common_root / "results"
    run_name = args.run_name.strip() or (
        f"smart_money_concepts_multi_timeframe_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    output_dir = results_root / run_name
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Running Smart Money Concepts multi-timeframe backtest")
    print(f"Timeframes: {', '.join(timeframes)}")
    print(f"Markets: {', '.join(args.markets)}")
    print(f"Variants: {', '.join(config.variants)}")

    run_results: list[dict[str, Any]] = []
    comparison_rows: list[dict[str, Any]] = []
    all_trades: list[dict[str, Any]] = []
    data_files_by_timeframe: dict[str, list[str]] = {}

    for timeframe in timeframes:
        timeframe_config = config_for_timeframe(config, timeframe)
        data_files = discover_data_files_for_timeframe(repo_root, args.markets, timeframe)
        data_files_by_timeframe[timeframe] = [str(path) for path in data_files]
        if not data_files:
            error = f"No *_{timeframe}.csv files found in selected market data folders."
            print(f"\n{timeframe}: {error}")
            for variant in config.variants:
                run_results.append(
                    {
                        "timeframe": timeframe,
                        "variant": variant,
                        "success": False,
                        "error": error,
                        "data_files_count": 0,
                    }
                )
            continue

        print(f"\n{timeframe}: found {len(data_files)} files")
        if timeframe_config.require_session_open != config.require_session_open:
            print(f"{timeframe}: accepting first available session candle for this timeframe")
        for variant in config.variants:
            print(f"Testing {timeframe} / {variant}")
            variant_trades: list[dict[str, Any]] = []
            file_stats: list[dict[str, Any]] = []
            skip_counts: dict[str, int] = defaultdict(int)

            for path in data_files:
                trades, stats = backtest_instrument_variant(
                    path,
                    timeframe,
                    variant,
                    timeframe_config,
                    skip_counts,
                )
                variant_trades.extend(trades)
                file_stats.append(stats)
                print(
                    f"  {stats['market']}/{stats['instrument']}: "
                    f"{stats['events']} events, {stats['trades']} trades"
                )

            summary = build_summary(
                timeframe,
                variant,
                variant_trades,
                file_stats,
                skip_counts,
                timeframe_config,
            )
            comparison_rows.append(comparison_row(summary))
            all_trades.extend(variant_trades)
            run_results.append(
                {
                    "timeframe": timeframe,
                    "variant": variant,
                    "success": True,
                    "data_files_count": len(data_files),
                    "summary": summary,
                    "file_stats": file_stats,
                }
            )

            print(
                f"  {timeframe}/{variant}: "
                f"trades={summary['total_trades']}, "
                f"before_brokerage={summary['gross_pnl_before_brokerage']}, "
                f"charges={summary['brokerage_and_charges']}, "
                f"after_brokerage={summary['net_pnl_after_brokerage']}, "
                f"pf={summary['profit_factor']}"
            )

    if not comparison_rows:
        raise SystemExit("No backtests ran because no data files were found.")

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "strategy": "Smart Money Concepts [LuxAlgo] inspired multi-timeframe backtest",
        "markets": args.markets,
        "timeframes": list(timeframes),
        "variants": list(config.variants),
        "configuration": json_ready(config.__dict__),
        "timeframe_session_policy": build_timeframe_session_policy(timeframes, config),
        "cost_model": base.cost_model_summary(config),
        "source_pine": str(repo_root / "pine-scripts" / "Smart Money Concepts [LuxAlgo].pine"),
        "data_files": data_files_by_timeframe,
        "timeframe_variant_summary": comparison_rows,
        "best_by_timeframe": build_best_by_timeframe_rows(comparison_rows),
        "what_traded_by_instrument": build_instrument_rows(all_trades),
        "brokerage_by_segment": build_charge_rows(all_trades),
        "direction_exit_summary": build_direction_exit_rows(all_trades),
        "best_worst_trades": build_best_worst_trade_rows(all_trades, config.top_trade_count),
        "skipped_signals": build_skip_rows(run_results),
        "runs": run_results,
    }

    comparison_path = output_dir / "timeframe_variant_summary.csv"
    summary_path = output_dir / "summary.json"
    markdown_path = output_dir / "summary.md"
    output_files = [markdown_path, summary_path, comparison_path]

    base.write_csv(comparison_path, comparison_rows)
    if args.write_trade_audit:
        trade_audit_path = output_dir / "all_trades.csv"
        base.write_csv(trade_audit_path, all_trades)
        output_files.append(trade_audit_path)

    payload["output_files"] = [str(path) for path in output_files]
    summary_path.write_text(json.dumps(json_ready(payload), indent=2), encoding="utf-8")
    write_summary_markdown(markdown_path, payload, config, output_files)

    print("")
    print(f"Results written to: {output_dir}")
    print("Timeframe/variant comparison:")
    for row in comparison_rows:
        print(
            f"  {row['timeframe']}/{row['variant']}: "
            f"events={row['events_tested']}, "
            f"trades={row['total_trades']}, "
            f"before_brokerage={row['gross_pnl_before_brokerage']}, "
            f"charges={row['brokerage_and_charges']}, "
            f"after_brokerage={row['net_pnl_after_brokerage']}, "
            f"max_dd={row['max_drawdown_pct']}%, "
            f"pf={row['profit_factor']}"
        )


if __name__ == "__main__":
    main()
