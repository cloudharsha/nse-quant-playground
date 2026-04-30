"""
Backtest the Squeeze Momentum Indicator [LazyBear] across multiple timeframes.

The local Pine file is currently empty, so this runner implements the canonical
LazyBear squeeze formula:

- Bollinger Bands and Keltner Channels define squeeze on/off state.
- Momentum is a linear regression of close minus the LazyBear mean reference.
- Squeeze-release entries trade the first bar after a squeeze fires.
- Momentum-zero-cross entries trade histogram crosses through zero.
- Entry happens on the next candle open after the signal candle closes.
- Exit/reverse on opposite signal, session end, or final bar.

Output is compact: one markdown summary, one JSON summary, one comparison CSV,
and an optional full trade audit CSV.
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
DEFAULT_MARKETS = ("derivatives", "equity", "commodities", "usdinr")
DEFAULT_VARIANTS = ("squeeze_release", "momentum_zero_cross")
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


@dataclass(frozen=True)
class SqueezeConfig:
    bb_length: int
    bb_mult: float
    kc_length: int
    kc_mult: float
    use_true_range: bool
    capital: float
    max_allocation_pct: float
    cost_multiplier: float
    equity_slippage: float
    derivatives_slippage: float
    commodities_slippage: float
    session_start: time | None
    exit_time: time | None
    require_session_open: bool
    exit_at_session_end: bool
    variants: tuple[str, ...]
    top_trade_count: int


def normalize_timeframe(value: str) -> str:
    cleaned = value.strip().lower().replace("-", "").replace("_", "").replace(" ", "")
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


def parse_variants(values: list[str]) -> tuple[str, ...]:
    valid = set(DEFAULT_VARIANTS)
    invalid = [value for value in values if value not in valid]
    if invalid:
        raise argparse.ArgumentTypeError(f"Invalid variants: {', '.join(invalid)}")
    seen: list[str] = []
    for value in values:
        if value not in seen:
            seen.append(value)
    return tuple(seen)


def timeframe_sort_key(timeframe: str) -> tuple[int, str]:
    try:
        return DEFAULT_TIMEFRAMES.index(timeframe), timeframe
    except ValueError:
        return len(DEFAULT_TIMEFRAMES), timeframe


def variant_sort_key(variant: str) -> tuple[int, str]:
    try:
        return DEFAULT_VARIANTS.index(variant), variant
    except ValueError:
        return len(DEFAULT_VARIANTS), variant


def config_for_timeframe(config: SqueezeConfig, timeframe: str) -> SqueezeConfig:
    if timeframe in AUTO_ALLOW_MISSING_SESSION_OPEN_TIMEFRAMES and config.require_session_open:
        return replace(config, require_session_open=False)
    return config


def build_timeframe_session_policy(
    timeframes: tuple[str, ...],
    base_config: SqueezeConfig,
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


def session_key(candle: dict[str, Any]) -> str:
    return candle["dt"].date().isoformat()


def sma_at(values: list[float], index: int, period: int) -> float | None:
    if index < period - 1:
        return None
    window = values[index - period + 1 : index + 1]
    return sum(window) / period


def stdev_at(values: list[float], index: int, period: int) -> float | None:
    mean = sma_at(values, index, period)
    if mean is None:
        return None
    window = values[index - period + 1 : index + 1]
    variance = sum((value - mean) ** 2 for value in window) / period
    return math.sqrt(variance)


def highest_at(values: list[float], index: int, period: int) -> float | None:
    if index < period - 1:
        return None
    return max(values[index - period + 1 : index + 1])


def lowest_at(values: list[float], index: int, period: int) -> float | None:
    if index < period - 1:
        return None
    return min(values[index - period + 1 : index + 1])


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


def linreg_at(values: list[float], index: int, period: int) -> float | None:
    if index < period - 1:
        return None
    window = values[index - period + 1 : index + 1]
    n = float(period)
    sum_x = (period - 1) * period / 2.0
    sum_x2 = (period - 1) * period * ((2 * period) - 1) / 6.0
    sum_y = sum(window)
    sum_xy = sum(x * y for x, y in enumerate(window))
    denominator = (n * sum_x2) - (sum_x * sum_x)
    if denominator == 0:
        return window[-1]
    slope = ((n * sum_xy) - (sum_x * sum_y)) / denominator
    intercept = (sum_y - (slope * sum_x)) / n
    return intercept + slope * (period - 1)


def annotate_squeeze(candles: list[dict[str, Any]], config: SqueezeConfig) -> None:
    closes = [float(candle["Close"]) for candle in candles]
    highs = [float(candle["High"]) for candle in candles]
    lows = [float(candle["Low"]) for candle in candles]
    ranges = true_range_values(candles) if config.use_true_range else [
        high - low for high, low in zip(highs, lows)
    ]
    momentum_source: list[float | None] = []

    for index, candle in enumerate(candles):
        basis = sma_at(closes, index, config.bb_length)
        deviation = stdev_at(closes, index, config.bb_length)
        ma = sma_at(closes, index, config.kc_length)
        range_ma = sma_at(ranges, index, config.kc_length)
        highest = highest_at(highs, index, config.kc_length)
        lowest = lowest_at(lows, index, config.kc_length)
        close_sma = sma_at(closes, index, config.kc_length)

        sqz_on = False
        sqz_off = False
        no_sqz = False
        upper_bb = lower_bb = upper_kc = lower_kc = None

        if basis is not None and deviation is not None:
            upper_bb = basis + (config.bb_mult * deviation)
            lower_bb = basis - (config.bb_mult * deviation)
        if ma is not None and range_ma is not None:
            upper_kc = ma + (range_ma * config.kc_mult)
            lower_kc = ma - (range_ma * config.kc_mult)

        if None not in (upper_bb, lower_bb, upper_kc, lower_kc):
            sqz_on = bool(lower_bb > lower_kc and upper_bb < upper_kc)
            sqz_off = bool(lower_bb < lower_kc and upper_bb > upper_kc)
            no_sqz = not sqz_on and not sqz_off

        if highest is None or lowest is None or close_sma is None:
            momentum_source.append(None)
        else:
            mean_reference = (((highest + lowest) / 2.0) + close_sma) / 2.0
            momentum_source.append(float(candle["Close"]) - mean_reference)

        valid_momentum = [
            0.0 if value is None else float(value) for value in momentum_source
        ]
        momentum = (
            linreg_at(valid_momentum, index, config.kc_length)
            if momentum_source[index] is not None
            else None
        )

        previous_momentum = candles[index - 1].get("SQZ_MOMENTUM") if index else None
        momentum_delta = (
            float(momentum) - float(previous_momentum)
            if momentum is not None and previous_momentum not in (None, "")
            else None
        )

        candle["SQZ_ON"] = sqz_on
        candle["SQZ_OFF"] = sqz_off
        candle["SQZ_NONE"] = no_sqz
        candle["SQZ_MOMENTUM"] = round(momentum, 8) if momentum is not None else ""
        candle["SQZ_MOMENTUM_DELTA"] = round(momentum_delta, 8) if momentum_delta is not None else ""
        candle["SQZ_BB_UPPER"] = round(upper_bb, 8) if upper_bb is not None else ""
        candle["SQZ_BB_LOWER"] = round(lower_bb, 8) if lower_bb is not None else ""
        candle["SQZ_KC_UPPER"] = round(upper_kc, 8) if upper_kc is not None else ""
        candle["SQZ_KC_LOWER"] = round(lower_kc, 8) if lower_kc is not None else ""


def build_signal_events(
    candles: list[dict[str, Any]],
    variant: str,
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for index, candle in enumerate(candles):
        momentum = candle.get("SQZ_MOMENTUM")
        if momentum in (None, ""):
            continue
        momentum_value = float(momentum)
        previous = candles[index - 1] if index else None
        previous_momentum = previous.get("SQZ_MOMENTUM") if previous else None

        signal = ""
        direction = ""
        if variant == "squeeze_release":
            if previous and previous.get("SQZ_ON") and candle.get("SQZ_OFF"):
                if momentum_value > 0:
                    signal = "SQUEEZE_RELEASE_UP"
                    direction = "LONG"
                elif momentum_value < 0:
                    signal = "SQUEEZE_RELEASE_DOWN"
                    direction = "SHORT"
        elif variant == "momentum_zero_cross":
            if previous_momentum not in (None, ""):
                previous_value = float(previous_momentum)
                if previous_value <= 0 < momentum_value:
                    signal = "MOMENTUM_CROSS_UP"
                    direction = "LONG"
                elif previous_value >= 0 > momentum_value:
                    signal = "MOMENTUM_CROSS_DOWN"
                    direction = "SHORT"
        else:
            raise ValueError(f"Unsupported squeeze variant: {variant}")

        if not signal:
            continue

        events.append(
            {
                "index": index,
                "time": candle["dt"].isoformat(),
                "session_date": session_key(candle),
                "signal": signal,
                "direction": direction,
                "momentum": round(momentum_value, 8),
                "momentum_delta": candle.get("SQZ_MOMENTUM_DELTA", ""),
                "sqz_on": candle.get("SQZ_ON", False),
                "sqz_off": candle.get("SQZ_OFF", False),
                "sqz_none": candle.get("SQZ_NONE", False),
                "close": float(candle["Close"]),
            }
        )
    return events


def allocation_quantity(entry_price: float, config: SqueezeConfig) -> int:
    allocation = float(config.capital) * (float(config.max_allocation_pct) / 100.0)
    if entry_price <= 0 or allocation <= 0:
        return 0
    return int(allocation // entry_price)


def charge_breakdown_for_trade(
    entry_price: float,
    exit_price: float,
    quantity: int,
    market: str,
    instrument: str,
    config: SqueezeConfig,
) -> dict[str, Any]:
    segment = base.charge_segment_for_market(market, instrument)
    return base.charge_breakdown_for_segment(
        abs(entry_price) * quantity,
        abs(exit_price) * quantity,
        segment,
        float(config.cost_multiplier),
    )


def build_trade(
    market: str,
    instrument: str,
    timeframe: str,
    variant: str,
    event: dict[str, Any],
    entry_candle: dict[str, Any],
    config: SqueezeConfig,
) -> dict[str, Any] | None:
    direction = str(event["direction"])
    slippage_points = base.slippage_points_for_market(market, instrument, config)
    entry_price = base.apply_entry_slippage(
        float(entry_candle["Open"]),
        direction,
        slippage_points,
    )
    quantity = allocation_quantity(entry_price, config)
    if quantity <= 0:
        return None

    return {
        "strategy": "Squeeze Momentum Indicator [LazyBear] multi-timeframe backtest",
        "market": market,
        "instrument": instrument,
        "timeframe": timeframe,
        "variant": variant,
        "session_date": entry_candle["dt"].date().isoformat(),
        "direction": direction,
        "signal": event["signal"],
        "signal_time": event["time"],
        "entry_time": entry_candle["dt"].isoformat(),
        "entry_price": round(entry_price, 6),
        "quantity": quantity,
        "notional": round(abs(entry_price) * quantity, 2),
        "slippage_points": round(slippage_points, 6),
        "momentum_at_signal": event["momentum"],
        "momentum_delta_at_signal": event["momentum_delta"],
        "squeeze_state_at_signal": "on" if event["sqz_on"] else "off" if event["sqz_off"] else "none",
        "_entry_index": int(entry_candle["_index"]),
    }


def public_trade(trade: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in trade.items() if not key.startswith("_")}


def close_trade(
    trade: dict[str, Any],
    candle: dict[str, Any],
    raw_exit_price: float,
    exit_reason: str,
    config: SqueezeConfig,
) -> dict[str, Any]:
    direction = str(trade["direction"])
    entry_price = float(trade["entry_price"])
    quantity = int(trade["quantity"])
    slippage_points = float(trade.get("slippage_points", 0.0))
    exit_price = base.apply_exit_slippage(raw_exit_price, direction, slippage_points)

    if direction == "LONG":
        gross_pnl = (exit_price - entry_price) * quantity
    else:
        gross_pnl = (entry_price - exit_price) * quantity

    charges = charge_breakdown_for_trade(
        entry_price,
        exit_price,
        quantity,
        str(trade["market"]),
        str(trade["instrument"]),
        config,
    )
    costs = float(charges["total"])
    net_pnl = gross_pnl - costs

    trade.update(
        {
            "exit_time": candle["dt"].isoformat(),
            "exit_price": round(exit_price, 6),
            "exit_reason": exit_reason,
            "holding_candles": int(candle["_index"]) - int(trade["_entry_index"]) + 1,
            "gross_pnl_before_brokerage": round(gross_pnl, 2),
            "gross_pnl": round(gross_pnl, 2),
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
            "brokerage_and_charges": round(costs, 2),
            "costs": round(costs, 2),
            "net_pnl_after_brokerage": round(net_pnl, 2),
            "net_pnl": round(net_pnl, 2),
            "return_on_notional_pct": round((net_pnl / float(trade["notional"])) * 100.0, 4)
            if float(trade["notional"])
            else 0.0,
        }
    )
    return trade


def is_last_candle_of_session(candles: list[dict[str, Any]], index: int) -> bool:
    if index >= len(candles) - 1:
        return True
    return session_key(candles[index + 1]) != session_key(candles[index])


def backtest_instrument_variant(
    path: Path,
    timeframe: str,
    variant: str,
    config: SqueezeConfig,
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

    annotate_squeeze(candles, config)
    events = build_signal_events(candles, variant)
    event_lookup = {int(event["index"]): event for event in events}

    trades: list[dict[str, Any]] = []
    active_trade: dict[str, Any] | None = None
    pending_event: dict[str, Any] | None = None

    for index, candle in enumerate(candles):
        if pending_event is not None and int(pending_event["index"]) == index - 1:
            if session_key(candle) != pending_event["session_date"]:
                skip_counts["signal_without_next_session_bar"] += 1
            else:
                if active_trade is not None:
                    trades.append(
                        public_trade(
                            close_trade(
                                active_trade,
                                candle,
                                float(candle["Open"]),
                                "OPPOSITE_SIGNAL",
                                config,
                            )
                        )
                    )
                    active_trade = None

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

        event = event_lookup.get(index)
        if event is not None and (
            active_trade is None or event["direction"] != active_trade["direction"]
        ):
            pending_event = event

        if active_trade is not None and config.exit_at_session_end and is_last_candle_of_session(candles, index):
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
        "variant": variant,
        "market": market,
        "instrument": instrument,
        "file": str(path),
        "candles": len(candles),
        "sessions": len({session_key(candle) for candle in candles}),
        "signals": len(events),
        "trades": len(trades),
        "skipped_partial_sessions": skipped_partial_sessions,
    }
    return trades, stats


def sum_trade_value(trades: list[dict[str, Any]], key: str) -> float:
    return sum(float(trade.get(key, 0.0) or 0.0) for trade in trades)


def profit_factor_from_values(values: list[float]) -> float | str:
    gross_profit = sum(max(value, 0.0) for value in values)
    gross_loss = abs(sum(min(value, 0.0) for value in values))
    if gross_loss == 0:
        return "inf" if gross_profit > 0 else ""
    return gross_profit / gross_loss


def max_drawdown(equity_rows: list[dict[str, Any]], starting_capital: float) -> tuple[float, float]:
    equity_values = [starting_capital] + [float(row["equity"]) for row in equity_rows]
    return base.max_drawdown_from_equity(equity_values)


def summary_for_timeframe_variant(
    timeframe: str,
    variant: str,
    trades: list[dict[str, Any]],
    file_stats: list[dict[str, Any]],
    skip_counts: dict[str, int],
    config: SqueezeConfig,
) -> dict[str, Any]:
    datewise_rows = base.build_datewise_pnl(trades, config.capital)
    equity_rows = base.build_equity_curve(trades, config.capital)
    gross_values = [float(trade["gross_pnl"]) for trade in trades]
    net_values = [float(trade["net_pnl"]) for trade in trades]
    wins = [value for value in net_values if value > 0]
    losses = [value for value in net_values if value <= 0]
    gross_wins = [value for value in gross_values if value > 0]
    pf = base.profit_factor(trades)
    gross_pf = profit_factor_from_values(gross_values)
    max_dd, max_dd_pct = max_drawdown(equity_rows, config.capital)
    sharpe = base.sharpe_ratio(datewise_rows)
    trade_dates = sorted({trade["session_date"] for trade in trades})
    traded_instruments = sorted(
        {f"{trade['market']}:{trade['instrument']}:{timeframe}" for trade in trades}
    )
    tested_instruments = sorted(
        {f"{item['market']}:{item['instrument']}:{timeframe}" for item in file_stats}
    )
    total_costs = sum_trade_value(trades, "costs")

    summary = {
        "strategy": "Squeeze Momentum Indicator [LazyBear] multi-timeframe backtest",
        "timeframe": timeframe,
        "variant": variant,
        "starting_capital": round(config.capital, 2),
        "ending_equity_without_brokerage": round(config.capital + sum(gross_values), 2),
        "ending_equity_with_brokerage": round(config.capital + sum(net_values), 2),
        "ending_equity": round(config.capital + sum(net_values), 2),
        "gross_pnl_before_brokerage": round(sum(gross_values), 2),
        "brokerage_and_charges": round(total_costs, 2),
        "total_costs": round(total_costs, 2),
        "net_pnl_after_brokerage": round(sum(net_values), 2),
        "net_pnl": round(sum(net_values), 2),
        "total_trades": len(trades),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate_pct": round((len(wins) / len(trades)) * 100.0, 2) if trades else 0.0,
        "gross_wins": len(gross_wins),
        "gross_losses": len(gross_values) - len(gross_wins),
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
        "total_turnover": round(sum_trade_value(trades, "turnover"), 2),
        "total_entry_notional": round(sum_trade_value(trades, "notional"), 2),
        "markets_tested": ",".join(sorted({item["market"] for item in file_stats})),
        "files_tested": len(file_stats),
        "sessions_tested": sum(int(item["sessions"]) for item in file_stats),
        "candles_tested": sum(int(item["candles"]) for item in file_stats),
        "signals_tested": sum(int(item["signals"]) for item in file_stats),
        "trade_start_date": trade_dates[0] if trade_dates else "",
        "trade_end_date": trade_dates[-1] if trade_dates else "",
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
        "signals_tested": summary["signals_tested"],
        "total_trades": summary["total_trades"],
        "gross_pnl_before_brokerage": summary["gross_pnl_before_brokerage"],
        "brokerage_and_charges": summary["brokerage_and_charges"],
        "net_pnl_after_brokerage": summary["net_pnl_after_brokerage"],
        "win_rate_pct": summary["win_rate_pct"],
        "ending_equity": summary["ending_equity"],
        "max_drawdown": summary["max_drawdown"],
        "max_drawdown_pct": summary["max_drawdown_pct"],
        "profit_factor": summary["profit_factor"],
        "sharpe_ratio": summary["sharpe_ratio"],
    }


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
        key=lambda item: (
            timeframe_sort_key(item[0][0]),
            variant_sort_key(item[0][1]),
            item[0][2],
            item[0][3],
        ),
    ):
        net_values = [float(trade["net_pnl"]) for trade in group_trades]
        gross_values = [float(trade["gross_pnl"]) for trade in group_trades]
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
                "gross_pnl_before_brokerage": round(sum(gross_values), 2),
                "brokerage_and_charges": round(sum_trade_value(group_trades, "costs"), 2),
                "net_pnl_after_brokerage": round(sum(net_values), 2),
                "win_rate_pct": round((len(wins) / len(group_trades)) * 100.0, 2)
                if group_trades
                else 0.0,
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
                str(trade["charge_segment"]),
                str(trade["charge_segment_label"]),
            )
        ].append(trade)

    rows: list[dict[str, Any]] = []
    for (timeframe, variant, segment, label), group_trades in sorted(
        grouped.items(),
        key=lambda item: (
            timeframe_sort_key(item[0][0]),
            variant_sort_key(item[0][1]),
            item[0][2],
            item[0][3],
        ),
    ):
        rows.append(
            {
                "timeframe": timeframe,
                "variant": variant,
                "segment": segment,
                "segment_label": label,
                "trades": len(group_trades),
                "turnover": round(sum_trade_value(group_trades, "turnover"), 2),
                "brokerage": round(sum_trade_value(group_trades, "brokerage"), 2),
                "stt": round(sum_trade_value(group_trades, "stt"), 2),
                "ctt": round(sum_trade_value(group_trades, "ctt"), 2),
                "exchange_charge": round(sum_trade_value(group_trades, "exchange_charge"), 2),
                "gst": round(sum_trade_value(group_trades, "gst"), 2),
                "sebi_charges": round(sum_trade_value(group_trades, "sebi_charges"), 2),
                "stamp_duty": round(sum_trade_value(group_trades, "stamp_duty"), 2),
                "total_charges": round(sum_trade_value(group_trades, "costs"), 2),
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
        key=lambda item: (
            timeframe_sort_key(item[0][0]),
            variant_sort_key(item[0][1]),
            item[0][2],
            item[0][3],
        ),
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


def build_best_by_timeframe_rows(comparison_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in comparison_rows:
        grouped[str(row["timeframe"])].append(row)

    rows: list[dict[str, Any]] = []
    for timeframe, timeframe_rows in sorted(
        grouped.items(),
        key=lambda item: timeframe_sort_key(item[0]),
    ):
        traded_rows = [row for row in timeframe_rows if int(row["total_trades"]) > 0]
        if not traded_rows:
            rows.append(
                {
                    "timeframe": timeframe,
                    "best_variant": "",
                    "trades": 0,
                    "gross_pnl_before_brokerage": 0,
                    "brokerage_and_charges": 0,
                    "net_pnl_after_brokerage": 0,
                    "win_rate_pct": 0,
                    "profit_factor": "",
                }
            )
            continue

        best = max(traded_rows, key=lambda row: float(row["net_pnl_after_brokerage"]))
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


def build_skip_rows(run_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], int] = defaultdict(int)
    for result in run_results:
        if not result.get("success"):
            grouped[
                (
                    str(result.get("timeframe", "")),
                    str(result.get("variant", "")),
                    "run_failed",
                )
            ] += 1
            continue

        summary = result.get("summary", {})
        for reason, count in summary.get("skip_counts", {}).items():
            grouped[(str(result["timeframe"]), str(result["variant"]), str(reason))] += int(count)
        for stats in result.get("file_stats", []):
            skipped = int(stats.get("skipped_partial_sessions", 0))
            if skipped:
                grouped[
                    (
                        str(result["timeframe"]),
                        str(result["variant"]),
                        "partial_session_missing_configured_open",
                    )
                ] += skipped

    return [
        {
            "timeframe": timeframe,
            "variant": variant,
            "reason": reason,
            "count": count,
        }
        for (timeframe, variant, reason), count in sorted(
            grouped.items(),
            key=lambda item: (
                timeframe_sort_key(item[0][0]),
                variant_sort_key(item[0][1]),
                item[0][2],
            ),
        )
    ]


def build_best_worst_trade_rows(
    trades: list[dict[str, Any]],
    limit: int,
) -> list[dict[str, Any]]:
    if not trades or limit <= 0:
        return []

    rows: list[dict[str, Any]] = []
    best = sorted(trades, key=lambda trade: float(trade["net_pnl"]), reverse=True)[:limit]
    worst = sorted(trades, key=lambda trade: float(trade["net_pnl"]))[:limit]

    for rank_type, group in (("best", best), ("worst", worst)):
        for rank, trade in enumerate(group, start=1):
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
                    "exit_reason": trade["exit_reason"],
                    "gross_pnl_before_brokerage": trade["gross_pnl"],
                    "brokerage_and_charges": trade["costs"],
                    "net_pnl_after_brokerage": trade["net_pnl"],
                }
            )
    return rows


def markdown_cell(value: Any) -> str:
    return str(value).replace("|", "\\|")


def append_markdown_table(
    lines: list[str],
    rows: list[dict[str, Any]],
    columns: list[tuple[str, str]],
) -> None:
    if not rows:
        lines.append("_No rows._")
        return

    lines.append("| " + " | ".join(title for title, _ in columns) + " |")
    lines.append("| " + " | ".join("---" for _ in columns) + " |")
    for row in rows:
        lines.append(
            "| "
            + " | ".join(markdown_cell(row.get(key, "")) for _, key in columns)
            + " |"
        )


def build_summary_markdown(payload: dict[str, Any], config: SqueezeConfig) -> str:
    comparison_rows = payload["timeframe_variant_summary"]
    traded_comparison_rows = [
        row for row in comparison_rows if int(row["total_trades"]) > 0
    ]
    best_source_rows = traded_comparison_rows or comparison_rows
    best_net = (
        max(best_source_rows, key=lambda row: float(row["net_pnl_after_brokerage"]))
        if best_source_rows
        else {}
    )
    best_gross = (
        max(best_source_rows, key=lambda row: float(row["gross_pnl_before_brokerage"]))
        if best_source_rows
        else {}
    )

    lines = [
        "# Squeeze Momentum Indicator [LazyBear] Multi-Timeframe Backtest",
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
        "- **source_note**: The local Pine file is empty, so this uses the canonical LazyBear formula.",
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
            ("Signals", "signals_tested"),
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
        payload["best_by_timeframe"],
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
        payload["what_traded_by_instrument"],
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
        payload["brokerage_by_segment"],
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
        payload["direction_exit_summary"],
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
        payload["best_worst_trades"],
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
            "- Bollinger Bands use configured `bb_length` and `bb_mult`.",
            "- Keltner Channels use configured `kc_length`, `kc_mult`, and true range by default.",
            "- Momentum is `linreg(close - avg(avg(highest, lowest), sma(close)), kc_length, 0)`.",
            "- `squeeze_release`: long when squeeze turns off with positive momentum; short when it turns off with negative momentum.",
            "- `momentum_zero_cross`: long when momentum crosses above zero; short when it crosses below zero.",
            "- Entry is the next candle open after signal close.",
            "- Existing positions exit/reverse on the next opposite signal.",
            "- Positions also exit at session end unless overnight holding is enabled.",
            "",
            "## Skipped Signals",
            "",
        ]
    )
    append_markdown_table(
        lines,
        payload["skipped_signals"],
        [
            ("Timeframe", "timeframe"),
            ("Variant", "variant"),
            ("Reason", "reason"),
            ("Count", "count"),
        ],
    )

    failed_runs = [result for result in payload["runs"] if not result.get("success")]
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
    for output_file in payload["output_files"]:
        lines.append(f"- `{Path(output_file).name}`")

    return "\n".join(lines) + "\n"


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backtest Squeeze Momentum Indicator [LazyBear] across timeframes.",
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
        default=list(DEFAULT_MARKETS),
        help="Market folders to test.",
    )
    parser.add_argument(
        "--variants",
        nargs="+",
        default=list(DEFAULT_VARIANTS),
        help="Variants: squeeze_release momentum_zero_cross",
    )
    parser.add_argument("--bb-length", type=int, default=20)
    parser.add_argument("--bb-mult", type=float, default=2.0)
    parser.add_argument("--kc-length", type=int, default=20)
    parser.add_argument("--kc-mult", type=float, default=1.5)
    parser.add_argument(
        "--use-high-low-range",
        action="store_true",
        help="Use high-low range for Keltner Channel instead of true range.",
    )
    parser.add_argument("--capital", type=float, default=1000000.0)
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
    parser.add_argument(
        "--session-start",
        type=base.parse_clock,
        default=base.parse_clock("09:15"),
    )
    parser.add_argument(
        "--exit-time",
        type=base.parse_clock,
        default=base.parse_clock("15:20"),
    )
    parser.add_argument("--allow-missing-session-open", action="store_true")
    parser.add_argument("--allow-overnight", action="store_true")
    parser.add_argument("--top-trade-count", type=int, default=10)
    parser.add_argument("--run-name", default="")
    parser.add_argument(
        "--write-trade-audit",
        action="store_true",
        help="Also write one all_trades.csv audit file. Default keeps output to summaries only.",
    )
    return parser.parse_args()


def config_from_args(args: argparse.Namespace) -> SqueezeConfig:
    return SqueezeConfig(
        bb_length=args.bb_length,
        bb_mult=args.bb_mult,
        kc_length=args.kc_length,
        kc_mult=args.kc_mult,
        use_true_range=not args.use_high_low_range,
        capital=args.capital,
        max_allocation_pct=args.max_allocation_pct,
        cost_multiplier=args.cost_multiplier,
        equity_slippage=args.equity_slippage,
        derivatives_slippage=args.derivatives_slippage,
        commodities_slippage=args.commodities_slippage,
        session_start=args.session_start,
        exit_time=args.exit_time,
        require_session_open=not args.allow_missing_session_open,
        exit_at_session_end=not args.allow_overnight,
        variants=parse_variants(args.variants),
        top_trade_count=args.top_trade_count,
    )


def main() -> None:
    args = parse_args()
    timeframes = parse_timeframes(args.timeframes)
    config = config_from_args(args)

    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[2]
    common_root = script_path.parents[1]
    results_root = common_root / "results"
    run_name = args.run_name.strip() or (
        f"squeeze_momentum_lazybear_multi_timeframe_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    output_dir = results_root / run_name
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Running Squeeze Momentum Indicator [LazyBear] multi-timeframe backtest")
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
                    f"{stats['signals']} signals, {stats['trades']} trades"
                )

            summary = summary_for_timeframe_variant(
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

    comparison_path = output_dir / "timeframe_variant_summary.csv"
    summary_path = output_dir / "summary.json"
    markdown_path = output_dir / "summary.md"
    output_files: list[Path] = [markdown_path, summary_path, comparison_path]

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "strategy": "Squeeze Momentum Indicator [LazyBear] multi-timeframe backtest",
        "source_note": "Local Pine file is empty; canonical LazyBear formula implemented.",
        "markets": args.markets,
        "timeframes": list(timeframes),
        "variants": list(config.variants),
        "configuration": json_ready(config.__dict__),
        "timeframe_session_policy": build_timeframe_session_policy(timeframes, config),
        "cost_model": base.cost_model_summary(config),
        "source_pine": str(repo_root / "pine-scripts" / "Squeeze Momentum Indicator [LazyBear].pine"),
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

    base.write_csv(comparison_path, comparison_rows)
    if args.write_trade_audit:
        trade_audit_path = output_dir / "all_trades.csv"
        base.write_csv(trade_audit_path, all_trades)
        output_files.append(trade_audit_path)

    payload["output_files"] = [str(path) for path in output_files]
    summary_path.write_text(json.dumps(json_ready(payload), indent=2), encoding="utf-8")
    markdown_path.write_text(build_summary_markdown(payload, config), encoding="utf-8")

    print("\nSqueeze Momentum Indicator [LazyBear] backtest completed")
    print(f"Results written to: {output_dir}")
    print("Timeframe/variant comparison:")
    for row in comparison_rows:
        print(
            f"  {row['timeframe']}/{row['variant']}: "
            f"signals={row['signals_tested']}, "
            f"trades={row['total_trades']}, "
            f"before_brokerage={row['gross_pnl_before_brokerage']}, "
            f"charges={row['brokerage_and_charges']}, "
            f"after_brokerage={row['net_pnl_after_brokerage']}, "
            f"max_dd={row['max_drawdown_pct']}%, "
            f"pf={row['profit_factor']}"
        )


if __name__ == "__main__":
    main()
