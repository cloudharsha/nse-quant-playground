"""
Backtest Open = Low / Open = High with stricter position sizing controls.

This script keeps the same 5-minute signal, entry, stop, target, slippage, and
brokerage rules from open_low_high_5m_strategy.py, but separates signal
generation from sizing. It creates raw trade candidates first, then replays
them chronologically through multiple position sizing methods:

1. fixed_fractional: risk a fixed percentage of live equity per trade.
2. volatility_adjusted: fixed-fractional risk capped by ATR exposure.
3. fractional_kelly: fixed-fractional warmup, then capped fractional Kelly.

The simulation also applies portfolio-level controls: max open positions,
max gross exposure, and max open stop-risk.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, time
from pathlib import Path
from typing import Any

import open_low_high_5m_strategy as base


SIZING_METHODS = (
    "fixed_fractional",
    "volatility_adjusted",
    "fractional_kelly",
)


@dataclass(frozen=True)
class PositionSizingConfig:
    tolerance_pct: float
    stop_buffer_pct: float
    target_type: str
    risk_reward: float
    target_pct: float
    trailing_stop_pct: float
    capital: float
    risk_per_trade_pct: float
    max_allocation_pct: float
    min_first_candle_volume: float
    min_average_volume: float
    max_gap_pct: float
    brokerage_bps: float
    slippage_bps: float
    session_start: time | None
    exit_time: time | None
    require_session_open: bool
    ambiguous_policy: str
    top_trade_count: int
    atr_period: int
    volatility_risk_pct: float
    kelly_warmup_trades: int
    fractional_kelly_factor: float
    kelly_max_risk_pct: float
    max_portfolio_risk_pct: float
    max_gross_exposure_pct: float
    max_open_positions: int
    position_sizing_methods: tuple[str, ...]


def annotate_prior_atr(candles: list[dict[str, Any]], period: int) -> None:
    true_ranges: list[float] = []
    previous_close: float | None = None

    for index, candle in enumerate(candles):
        if previous_close is None:
            true_range = candle["High"] - candle["Low"]
        else:
            true_range = max(
                candle["High"] - candle["Low"],
                abs(candle["High"] - previous_close),
                abs(candle["Low"] - previous_close),
            )

        if index >= period:
            prior_values = true_ranges[index - period : index]
            candle["ATR_PRIOR"] = sum(prior_values) / period
        else:
            candle["ATR_PRIOR"] = 0.0

        true_ranges.append(true_range)
        previous_close = candle["Close"]


def config_strategy_view(config: PositionSizingConfig) -> base.StrategyConfig:
    return base.StrategyConfig(
        tolerance_pct=config.tolerance_pct,
        stop_buffer_pct=config.stop_buffer_pct,
        target_type=config.target_type,
        risk_reward=config.risk_reward,
        target_pct=config.target_pct,
        trailing_stop_pct=config.trailing_stop_pct,
        capital=config.capital,
        risk_per_trade_pct=config.risk_per_trade_pct,
        max_allocation_pct=config.max_allocation_pct,
        min_first_candle_volume=config.min_first_candle_volume,
        min_average_volume=config.min_average_volume,
        max_gap_pct=config.max_gap_pct,
        brokerage_bps=config.brokerage_bps,
        slippage_bps=config.slippage_bps,
        session_start=config.session_start,
        exit_time=config.exit_time,
        require_session_open=config.require_session_open,
        ambiguous_policy=config.ambiguous_policy,
        top_trade_count=config.top_trade_count,
    )


def build_candidate(
    market: str,
    instrument: str,
    source_file: Path,
    session_date: str,
    session: list[dict[str, Any]],
    setup_name: str,
    direction: str,
    signal_index: int,
    entry_index: int,
    stop_price: float,
    strategy_config: base.StrategyConfig,
    gap_pct: float | None,
) -> dict[str, Any] | None:
    first = session[0]
    signal = session[signal_index]
    entry_candle = session[entry_index]
    entry_price = base.apply_entry_slippage(
        entry_candle["Open"],
        direction,
        strategy_config.slippage_bps,
    )

    if direction == "LONG" and entry_price <= stop_price:
        return None
    if direction == "SHORT" and entry_price >= stop_price:
        return None

    target_price = base.fixed_target_price(
        direction,
        entry_price,
        stop_price,
        strategy_config,
    )
    exit_reason, exit_candle, exit_price = base.exit_trade(
        direction=direction,
        session=session,
        entry_index=entry_index,
        entry_price=entry_price,
        initial_stop=stop_price,
        target_price=target_price,
        config=strategy_config,
    )

    stop_fill = base.apply_exit_slippage(
        stop_price,
        direction,
        strategy_config.slippage_bps,
    )
    if direction == "LONG":
        gross_pnl_per_unit = exit_price - entry_price
        stop_distance = entry_price - stop_fill
    else:
        gross_pnl_per_unit = entry_price - exit_price
        stop_distance = stop_fill - entry_price

    if stop_distance <= 0:
        return None

    holding_candles = max(0, session.index(exit_candle) - entry_index + 1)
    atr_at_entry = float(entry_candle.get("ATR_PRIOR", 0.0) or 0.0)

    return {
        "market": market,
        "instrument": instrument,
        "source_file": str(source_file),
        "session_date": session_date,
        "setup": setup_name,
        "direction": direction,
        "first_candle_time": first["dt"].isoformat(),
        "first_open": round(first["Open"], 6),
        "first_high": round(first["High"], 6),
        "first_low": round(first["Low"], 6),
        "first_close": round(first["Close"], 6),
        "first_volume": round(first["Volume"], 2),
        "gap_pct": base.format_pct(gap_pct),
        "signal_time": signal["dt"].isoformat(),
        "signal_close": round(signal["Close"], 6),
        "entry_time": entry_candle["dt"].isoformat(),
        "entry_price": round(entry_price, 6),
        "stop_price": round(stop_price, 6),
        "target_price": round(target_price, 6) if target_price is not None else "",
        "exit_time": exit_candle["dt"].isoformat(),
        "exit_price": round(exit_price, 6),
        "exit_reason": exit_reason,
        "atr_at_entry": round(atr_at_entry, 6),
        "gross_pnl_per_unit": gross_pnl_per_unit,
        "stop_distance_per_unit": stop_distance,
        "holding_candles": holding_candles,
        "_entry_dt": entry_candle["dt"],
        "_exit_dt": exit_candle["dt"],
    }


def find_candidate_for_session(
    market: str,
    instrument: str,
    source_file: Path,
    session_date: str,
    session: list[dict[str, Any]],
    strategy_config: base.StrategyConfig,
    previous_close: float | None,
    skip_counts: dict[str, int],
) -> dict[str, Any] | None:
    if len(session) < 3:
        skip_counts["too_few_candles"] += 1
        return None

    first = session[0]
    if strategy_config.session_start is not None and strategy_config.require_session_open:
        if first["dt"].time() != strategy_config.session_start:
            skip_counts["missing_session_open"] += 1
            return None

    if first["Volume"] < strategy_config.min_first_candle_volume:
        skip_counts["first_volume_filter"] += 1
        return None

    if strategy_config.min_average_volume > 0:
        avg_volume = sum(candle["Volume"] for candle in session) / len(session)
        if avg_volume < strategy_config.min_average_volume:
            skip_counts["average_volume_filter"] += 1
            return None

    gap_pct: float | None = None
    if previous_close and previous_close > 0:
        gap_pct = ((first["Open"] - previous_close) / previous_close) * 100.0
        if strategy_config.max_gap_pct > 0 and abs(gap_pct) > strategy_config.max_gap_pct:
            skip_counts["gap_filter"] += 1
            return None

    bullish = base.is_open_low(first, strategy_config.tolerance_pct)
    bearish = base.is_open_high(first, strategy_config.tolerance_pct)

    if bullish and bearish:
        skip_counts["ambiguous_first_candle"] += 1
        return None

    if not bullish and not bearish:
        skip_counts["no_open_low_high_setup"] += 1
        return None

    if bullish:
        stop_price = first["Open"] * (1.0 - base.pct_to_decimal(strategy_config.stop_buffer_pct))
        for signal_index in range(1, len(session) - 1):
            if session[signal_index]["Close"] > first["High"]:
                return build_candidate(
                    market=market,
                    instrument=instrument,
                    source_file=source_file,
                    session_date=session_date,
                    session=session,
                    setup_name="OPEN_EQUALS_LOW",
                    direction="LONG",
                    signal_index=signal_index,
                    entry_index=signal_index + 1,
                    stop_price=stop_price,
                    strategy_config=strategy_config,
                    gap_pct=gap_pct,
                )
        skip_counts["no_breakout_entry"] += 1
        return None

    stop_price = first["Open"] * (1.0 + base.pct_to_decimal(strategy_config.stop_buffer_pct))
    for signal_index in range(1, len(session) - 1):
        if session[signal_index]["Close"] < first["Low"]:
            return build_candidate(
                market=market,
                instrument=instrument,
                source_file=source_file,
                session_date=session_date,
                session=session,
                setup_name="OPEN_EQUALS_HIGH",
                direction="SHORT",
                signal_index=signal_index,
                entry_index=signal_index + 1,
                stop_price=stop_price,
                strategy_config=strategy_config,
                gap_pct=gap_pct,
            )

    skip_counts["no_breakdown_entry"] += 1
    return None


def generate_candidates(
    path: Path,
    config: PositionSizingConfig,
    signal_skip_counts: dict[str, int],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    market = base.market_name(path)
    instrument = base.instrument_name(path)
    strategy_config = config_strategy_view(config)
    candles = base.load_candles(path)
    annotate_prior_atr(candles, config.atr_period)
    sessions = base.group_sessions(
        candles,
        strategy_config.session_start,
        strategy_config.exit_time,
    )

    candidates: list[dict[str, Any]] = []
    previous_close: float | None = None
    session_count = 0

    for session_date in sorted(sessions):
        session = sessions[session_date]
        session_count += 1
        candidate = find_candidate_for_session(
            market=market,
            instrument=instrument,
            source_file=path,
            session_date=session_date,
            session=session,
            strategy_config=strategy_config,
            previous_close=previous_close,
            skip_counts=signal_skip_counts,
        )
        if candidate is not None:
            candidates.append(candidate)
        previous_close = session[-1]["Close"]

    return candidates, {
        "market": market,
        "instrument": instrument,
        "file": str(path),
        "candles": len(candles),
        "sessions": session_count,
        "candidates": len(candidates),
    }


def calculate_kelly_fraction(history: list[float], warmup: int) -> float | None:
    if len(history) < warmup:
        return None

    wins = [value for value in history if value > 0]
    losses = [abs(value) for value in history if value <= 0]

    if not wins:
        return 0.0
    if not losses:
        return 1.0

    win_probability = len(wins) / len(history)
    win_loss_ratio = statistics.mean(wins) / statistics.mean(losses)
    if win_loss_ratio <= 0:
        return 0.0

    return win_probability - ((1.0 - win_probability) / win_loss_ratio)


def method_risk_pct(
    method: str,
    history: list[float],
    config: PositionSizingConfig,
) -> tuple[float, str]:
    if method != "fractional_kelly":
        return config.risk_per_trade_pct, "fixed_percent_risk"

    kelly_fraction = calculate_kelly_fraction(history, config.kelly_warmup_trades)
    if kelly_fraction is None:
        return config.risk_per_trade_pct, "kelly_warmup_fixed_percent_risk"

    risk_pct = max(0.0, kelly_fraction) * config.fractional_kelly_factor * 100.0
    risk_pct = min(config.kelly_max_risk_pct, risk_pct)
    return risk_pct, f"kelly_fraction={kelly_fraction:.4f}"


def sizing_decision(
    candidate: dict[str, Any],
    method: str,
    equity: float,
    open_positions: list[dict[str, Any]],
    history: list[float],
    config: PositionSizingConfig,
) -> dict[str, Any]:
    if config.max_open_positions > 0 and len(open_positions) >= config.max_open_positions:
        return {"quantity": 0, "reason": "max_open_positions"}

    if equity <= 0:
        return {"quantity": 0, "reason": "equity_depleted"}

    entry_price = float(candidate["entry_price"])
    stop_distance = float(candidate["stop_distance_per_unit"])
    if entry_price <= 0 or stop_distance <= 0:
        return {"quantity": 0, "reason": "invalid_entry_or_stop"}

    risk_pct, sizing_note = method_risk_pct(method, history, config)
    if risk_pct <= 0:
        return {"quantity": 0, "reason": "no_positive_kelly_edge", "sizing_note": sizing_note}

    open_risk = sum(float(position["position_risk_amount"]) for position in open_positions)
    open_notional = sum(float(position["notional"]) for position in open_positions)

    per_trade_risk_budget = equity * base.pct_to_decimal(risk_pct)
    portfolio_risk_limit = equity * base.pct_to_decimal(config.max_portfolio_risk_pct)
    available_portfolio_risk = max(0.0, portfolio_risk_limit - open_risk)

    per_trade_notional_limit = equity * base.pct_to_decimal(config.max_allocation_pct)
    gross_exposure_limit = equity * base.pct_to_decimal(config.max_gross_exposure_pct)
    available_gross_exposure = max(0.0, gross_exposure_limit - open_notional)

    caps = {
        "risk_budget": math.floor(per_trade_risk_budget / stop_distance),
        "portfolio_risk": math.floor(available_portfolio_risk / stop_distance),
        "per_trade_allocation": math.floor(per_trade_notional_limit / entry_price),
        "gross_exposure": math.floor(available_gross_exposure / entry_price),
    }

    if method == "volatility_adjusted":
        atr_at_entry = float(candidate.get("atr_at_entry") or 0.0)
        if atr_at_entry <= 0:
            return {"quantity": 0, "reason": "missing_atr_for_volatility_sizing"}
        volatility_budget = equity * base.pct_to_decimal(config.volatility_risk_pct)
        caps["volatility_budget"] = math.floor(volatility_budget / atr_at_entry)

    positive_caps = {key: value for key, value in caps.items() if value >= 0}
    quantity = min(positive_caps.values()) if positive_caps else 0
    limiting_factor = min(positive_caps, key=positive_caps.get) if positive_caps else "none"

    if quantity <= 0:
        return {
            "quantity": 0,
            "reason": f"{limiting_factor}_too_small",
            "sizing_note": sizing_note,
            "open_risk_before": open_risk,
            "open_notional_before": open_notional,
        }

    return {
        "quantity": quantity,
        "reason": "sized",
        "sizing_note": sizing_note,
        "risk_pct_budget": risk_pct,
        "per_trade_risk_budget": per_trade_risk_budget,
        "portfolio_risk_limit": portfolio_risk_limit,
        "open_risk_before": open_risk,
        "per_trade_notional_limit": per_trade_notional_limit,
        "gross_exposure_limit": gross_exposure_limit,
        "open_notional_before": open_notional,
        "limiting_factor": limiting_factor,
    }


def instantiate_trade(
    candidate: dict[str, Any],
    method: str,
    decision: dict[str, Any],
    equity_at_entry: float,
    config: PositionSizingConfig,
) -> dict[str, Any]:
    quantity = int(decision["quantity"])
    entry_price = float(candidate["entry_price"])
    exit_price = float(candidate["exit_price"])
    gross_pnl = float(candidate["gross_pnl_per_unit"]) * quantity
    costs = base.brokerage_cost(entry_price, exit_price, quantity, config.brokerage_bps)
    net_pnl = gross_pnl - costs
    notional = entry_price * quantity
    risk_amount = float(candidate["stop_distance_per_unit"]) * quantity
    r_multiple = net_pnl / risk_amount if risk_amount > 0 else 0.0

    trade = {
        "sizing_method": method,
        "market": candidate["market"],
        "instrument": candidate["instrument"],
        "session_date": candidate["session_date"],
        "setup": candidate["setup"],
        "direction": candidate["direction"],
        "first_candle_time": candidate["first_candle_time"],
        "first_open": candidate["first_open"],
        "first_high": candidate["first_high"],
        "first_low": candidate["first_low"],
        "first_close": candidate["first_close"],
        "first_volume": candidate["first_volume"],
        "gap_pct": candidate["gap_pct"],
        "signal_time": candidate["signal_time"],
        "signal_close": candidate["signal_close"],
        "entry_time": candidate["entry_time"],
        "entry_price": round(entry_price, 6),
        "stop_price": candidate["stop_price"],
        "target_price": candidate["target_price"],
        "exit_time": candidate["exit_time"],
        "exit_price": round(exit_price, 6),
        "exit_reason": candidate["exit_reason"],
        "atr_at_entry": candidate["atr_at_entry"],
        "quantity": quantity,
        "equity_at_entry": round(equity_at_entry, 2),
        "risk_pct_budget": round(float(decision["risk_pct_budget"]), 4),
        "position_risk_amount": round(risk_amount, 2),
        "open_risk_before": round(float(decision["open_risk_before"]), 2),
        "portfolio_risk_limit": round(float(decision["portfolio_risk_limit"]), 2),
        "notional": round(notional, 2),
        "open_notional_before": round(float(decision["open_notional_before"]), 2),
        "gross_exposure_limit": round(float(decision["gross_exposure_limit"]), 2),
        "limiting_factor": decision["limiting_factor"],
        "sizing_note": decision["sizing_note"],
        "gross_pnl": round(gross_pnl, 2),
        "costs": round(costs, 2),
        "net_pnl": round(net_pnl, 2),
        "return_pct_on_notional": round((net_pnl / notional) * 100.0, 4)
        if notional > 0
        else 0.0,
        "r_multiple": round(r_multiple, 4),
        "holding_candles": candidate["holding_candles"],
        "_entry_dt": candidate["_entry_dt"],
        "_exit_dt": candidate["_exit_dt"],
    }
    return trade


def public_trade(trade: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in trade.items() if not key.startswith("_")}


def simulate_position_sizing_method(
    method: str,
    candidates: list[dict[str, Any]],
    config: PositionSizingConfig,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    ordered_candidates = sorted(
        candidates,
        key=lambda item: (
            item["_entry_dt"],
            item["market"],
            item["instrument"],
        ),
    )

    equity = config.capital
    open_positions: list[dict[str, Any]] = []
    closed_trades: list[dict[str, Any]] = []
    equity_curve: list[dict[str, Any]] = []
    history: list[float] = []
    sizing_skip_counts: dict[str, int] = defaultdict(int)
    trade_number = 0
    peak_equity = config.capital

    def close_positions_until(cutoff: datetime | None) -> None:
        nonlocal equity, trade_number, peak_equity, open_positions

        due = [
            position
            for position in open_positions
            if cutoff is None or position["_exit_dt"] <= cutoff
        ]
        due = sorted(
            due,
            key=lambda item: (
                item["_exit_dt"],
                item["market"],
                item["instrument"],
            ),
        )

        for trade in due:
            equity += float(trade["net_pnl"])
            peak_equity = max(peak_equity, equity)
            drawdown = equity - peak_equity
            trade_number += 1
            trade["equity_after_exit"] = round(equity, 2)
            closed_trades.append(public_trade(trade))
            history.append(float(trade["r_multiple"]))
            equity_curve.append(
                {
                    "sizing_method": method,
                    "trade_number": trade_number,
                    "exit_time": trade["exit_time"],
                    "session_date": trade["session_date"],
                    "market": trade["market"],
                    "instrument": trade["instrument"],
                    "net_pnl": trade["net_pnl"],
                    "equity": round(equity, 2),
                    "drawdown": round(drawdown, 2),
                    "drawdown_pct": round((drawdown / peak_equity) * 100.0, 4)
                    if peak_equity
                    else 0.0,
                }
            )

        if due:
            due_ids = {id(item) for item in due}
            open_positions = [item for item in open_positions if id(item) not in due_ids]

    for candidate in ordered_candidates:
        close_positions_until(candidate["_entry_dt"])
        decision = sizing_decision(
            candidate=candidate,
            method=method,
            equity=equity,
            open_positions=open_positions,
            history=history,
            config=config,
        )
        if int(decision.get("quantity", 0)) <= 0:
            sizing_skip_counts[str(decision.get("reason", "unknown_sizing_skip"))] += 1
            continue

        trade = instantiate_trade(
            candidate=candidate,
            method=method,
            decision=decision,
            equity_at_entry=equity,
            config=config,
        )
        open_positions.append(trade)

    close_positions_until(None)
    return closed_trades, equity_curve, dict(sorted(sizing_skip_counts.items()))


def build_method_summary(
    method: str,
    trades: list[dict[str, Any]],
    equity_rows: list[dict[str, Any]],
    file_stats: list[dict[str, Any]],
    signal_skip_counts: dict[str, int],
    sizing_skip_counts: dict[str, int],
    total_candidates: int,
    config: PositionSizingConfig,
) -> dict[str, Any]:
    datewise_rows = base.build_datewise_pnl(trades, config.capital)
    summary = base.build_summary(
        trades=trades,
        datewise_rows=datewise_rows,
        equity_rows=equity_rows,
        file_stats=[
            {
                "market": item["market"],
                "instrument": item["instrument"],
                "file": item["file"],
                "candles": item["candles"],
                "sessions": item["sessions"],
                "trades": item["candidates"],
            }
            for item in file_stats
        ],
        skip_counts=defaultdict(int, signal_skip_counts),
        config=config_strategy_view(config),
    )
    summary["position_sizing_method"] = method
    summary["total_candidates"] = total_candidates
    summary["sizing_skip_counts"] = sizing_skip_counts
    summary["signal_skip_counts"] = dict(sorted(signal_skip_counts.items()))
    return summary


def comparison_row(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "position_sizing_method": summary["position_sizing_method"],
        "total_candidates": summary["total_candidates"],
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


def write_summary_markdown(
    path: Path,
    comparison_rows: list[dict[str, Any]],
    summaries: dict[str, dict[str, Any]],
    config: PositionSizingConfig,
    output_files: list[Path],
) -> None:
    lines = [
        "# Open = Low / Open = High Position Sizing Backtest",
        "",
        "## Method Comparison",
        "",
        "| Method | Trades | Win Rate % | Net P&L | Ending Equity | Max DD % | Profit Factor | Sharpe |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for row in comparison_rows:
        lines.append(
            "| {position_sizing_method} | {total_trades} | {win_rate_pct} | "
            "{net_pnl} | {ending_equity} | {max_drawdown_pct} | "
            "{profit_factor} | {sharpe_ratio} |".format(**row)
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
            f"- **total_candidates**: {first_summary.get('total_candidates', '')}",
            "",
            "## Cost Model",
            "",
            f"- **brokerage_calculated**: {config.brokerage_bps > 0}",
            f"- **slippage_calculated**: {config.slippage_bps > 0}",
            f"- **brokerage_bps**: {config.brokerage_bps}",
            f"- **slippage_bps**: {config.slippage_bps}",
            "- **pnl_basis**: Gross P&L; brokerage and slippage disabled"
            if config.brokerage_bps == 0 and config.slippage_bps == 0
            else "- **pnl_basis**: Net P&L after brokerage and slippage",
        ]
    )

    lines.extend(
        [
            "",
            "## Position Sizing Logic",
            "",
            "- `fixed_fractional`: quantity is capped by live-equity risk per trade, per-trade notional, portfolio stop-risk, and gross exposure.",
            "- `volatility_adjusted`: same as fixed fractional, with an extra ATR exposure cap.",
            "- `fractional_kelly`: starts fixed fractional, then uses capped fractional Kelly after the warmup sample closes.",
            "",
            "## Sizing Skips",
            "",
        ]
    )

    for method, summary in summaries.items():
        lines.append(f"### {method}")
        skips = summary.get("sizing_skip_counts", {})
        if skips:
            for key, value in skips.items():
                lines.append(f"- **{key}**: {value}")
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

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare position sizing methods for Open=Low/Open=High 5m strategy.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--markets",
        nargs="+",
        choices=base.MARKETS,
        default=list(base.MARKETS),
    )
    parser.add_argument(
        "--position-sizing-methods",
        nargs="+",
        choices=SIZING_METHODS,
        default=list(SIZING_METHODS),
    )
    parser.add_argument("--tolerance-pct", type=float, default=0.1)
    parser.add_argument("--stop-buffer-pct", type=float, default=0.02)
    parser.add_argument(
        "--target-type",
        choices=("rr", "percent", "trailing", "none"),
        default="rr",
    )
    parser.add_argument("--risk-reward", type=float, default=2.0)
    parser.add_argument("--target-pct", type=float, default=0.75)
    parser.add_argument("--trailing-stop-pct", type=float, default=0.0)
    parser.add_argument("--capital", type=float, default=100000.0)
    parser.add_argument("--risk-per-trade-pct", type=float, default=1.0)
    parser.add_argument("--max-allocation-pct", type=float, default=100.0)
    parser.add_argument("--min-first-candle-volume", type=float, default=0.0)
    parser.add_argument("--min-average-volume", type=float, default=0.0)
    parser.add_argument("--max-gap-pct", type=float, default=0.0)
    parser.add_argument("--brokerage-bps", type=float, default=3.0)
    parser.add_argument("--slippage-bps", type=float, default=2.0)
    parser.add_argument("--session-start", type=base.parse_clock, default=base.parse_clock("09:15"))
    parser.add_argument("--exit-time", type=base.parse_clock, default=base.parse_clock("15:20"))
    parser.add_argument("--allow-missing-session-open", action="store_true")
    parser.add_argument(
        "--ambiguous-policy",
        choices=("stop_first", "target_first"),
        default="stop_first",
    )
    parser.add_argument("--atr-period", type=int, default=14)
    parser.add_argument("--volatility-risk-pct", type=float, default=0.5)
    parser.add_argument("--kelly-warmup-trades", type=int, default=30)
    parser.add_argument("--fractional-kelly-factor", type=float, default=0.25)
    parser.add_argument("--kelly-max-risk-pct", type=float, default=2.0)
    parser.add_argument("--max-portfolio-risk-pct", type=float, default=6.0)
    parser.add_argument("--max-gross-exposure-pct", type=float, default=300.0)
    parser.add_argument("--max-open-positions", type=int, default=6)
    parser.add_argument("--run-name", default="")
    parser.add_argument("--top-trade-count", type=int, default=10)
    return parser.parse_args()


def config_from_args(args: argparse.Namespace) -> PositionSizingConfig:
    return PositionSizingConfig(
        tolerance_pct=args.tolerance_pct,
        stop_buffer_pct=args.stop_buffer_pct,
        target_type=args.target_type,
        risk_reward=args.risk_reward,
        target_pct=args.target_pct,
        trailing_stop_pct=args.trailing_stop_pct,
        capital=args.capital,
        risk_per_trade_pct=args.risk_per_trade_pct,
        max_allocation_pct=args.max_allocation_pct,
        min_first_candle_volume=args.min_first_candle_volume,
        min_average_volume=args.min_average_volume,
        max_gap_pct=args.max_gap_pct,
        brokerage_bps=args.brokerage_bps,
        slippage_bps=args.slippage_bps,
        session_start=args.session_start,
        exit_time=args.exit_time,
        require_session_open=not args.allow_missing_session_open,
        ambiguous_policy=args.ambiguous_policy,
        top_trade_count=args.top_trade_count,
        atr_period=args.atr_period,
        volatility_risk_pct=args.volatility_risk_pct,
        kelly_warmup_trades=args.kelly_warmup_trades,
        fractional_kelly_factor=args.fractional_kelly_factor,
        kelly_max_risk_pct=args.kelly_max_risk_pct,
        max_portfolio_risk_pct=args.max_portfolio_risk_pct,
        max_gross_exposure_pct=args.max_gross_exposure_pct,
        max_open_positions=args.max_open_positions,
        position_sizing_methods=tuple(args.position_sizing_methods),
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
    run_name = args.run_name.strip() or (
        f"open_low_high_5m_position_sizing_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    output_dir = results_root / run_name
    output_dir.mkdir(parents=True, exist_ok=True)

    data_files = base.discover_data_files(repo_root, args.markets)
    if not data_files:
        raise SystemExit("No *_5m.csv files found in selected market data folders.")

    signal_skip_counts: dict[str, int] = defaultdict(int)
    all_candidates: list[dict[str, Any]] = []
    file_stats: list[dict[str, Any]] = []

    print(f"Generating Open=Low/Open=High candidates from {len(data_files)} files...")
    for path in data_files:
        candidates, stats = generate_candidates(path, config, signal_skip_counts)
        all_candidates.extend(candidates)
        file_stats.append(stats)
        print(
            f"{stats['market']}/{stats['instrument']}: "
            f"{stats['sessions']} sessions, {stats['candidates']} candidates"
        )

    print(f"\nTotal candidates before sizing: {len(all_candidates)}")

    summaries: dict[str, dict[str, Any]] = {}
    comparison_rows: list[dict[str, Any]] = []
    output_files: list[Path] = []

    for method in config.position_sizing_methods:
        print(f"Simulating position sizing: {method}")
        trades, equity_curve, sizing_skips = simulate_position_sizing_method(
            method,
            all_candidates,
            config,
        )
        datewise_rows = base.build_datewise_pnl(trades, config.capital)
        instrument_rows = base.build_instrument_metrics(trades)
        best_worst_rows = base.build_best_worst_trades(trades, config.top_trade_count)
        summary = build_method_summary(
            method=method,
            trades=trades,
            equity_rows=equity_curve,
            file_stats=file_stats,
            signal_skip_counts=signal_skip_counts,
            sizing_skip_counts=sizing_skips,
            total_candidates=len(all_candidates),
            config=config,
        )
        summaries[method] = summary
        comparison_rows.append(comparison_row(summary))

        method_outputs = {
            "trades": output_dir / f"trades_{method}.csv",
            "datewise_pnl": output_dir / f"datewise_pnl_{method}.csv",
            "equity_curve": output_dir / f"equity_curve_{method}.csv",
            "instrument_metrics": output_dir / f"instrument_metrics_{method}.csv",
            "best_worst_trades": output_dir / f"best_worst_trades_{method}.csv",
        }
        base.write_csv(method_outputs["trades"], trades)
        base.write_csv(method_outputs["datewise_pnl"], datewise_rows)
        base.write_csv(method_outputs["equity_curve"], equity_curve)
        base.write_csv(method_outputs["instrument_metrics"], instrument_rows)
        base.write_csv(method_outputs["best_worst_trades"], best_worst_rows)
        output_files.extend(method_outputs.values())

        print(
            f"  trades={summary['total_trades']}, "
            f"net_pnl={summary['net_pnl']}, "
            f"max_dd={summary['max_drawdown_pct']}%, "
            f"pf={summary['profit_factor']}"
        )

    comparison_path = output_dir / "method_comparison.csv"
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
                "signal_skip_counts": dict(sorted(signal_skip_counts.items())),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    output_files.extend([comparison_path, summary_path, config_path, markdown_path])
    write_summary_markdown(
        markdown_path,
        comparison_rows,
        summaries,
        config,
        output_files,
    )

    print("")
    print(f"Results written to: {output_dir}")
    print("Method comparison:")
    for row in comparison_rows:
        print(
            f"  {row['position_sizing_method']}: "
            f"trades={row['total_trades']}, "
            f"net_pnl={row['net_pnl']}, "
            f"win_rate={row['win_rate_pct']}%, "
            f"max_dd={row['max_drawdown_pct']}%, "
            f"pf={row['profit_factor']}"
        )


if __name__ == "__main__":
    main()
