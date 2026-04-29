"""
Backtest the Open = Low / Open = High intraday strategy on 5-minute candles.

The script discovers *_5m.csv files from equity, derivatives, and commodities
data folders, runs a one-trade-per-instrument-per-day backtest, and writes the
reports into common-strategies/results.

Entry is intentionally delayed until the next candle open after a confirming
candle close. That keeps the backtest free from lookahead bias.
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


REQUIRED_COLUMNS = ("Date", "Open", "High", "Low", "Close", "Volume")
MARKETS = ("equity", "derivatives", "commodities")


@dataclass(frozen=True)
class StrategyConfig:
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
    brokerage_entry_fee: float
    brokerage_exit_fee: float
    other_charges: float
    equity_slippage: float
    derivatives_slippage: float
    commodities_slippage: float
    session_start: time | None
    exit_time: time | None
    require_session_open: bool
    ambiguous_policy: str
    top_trade_count: int


def parse_clock(value: str | None) -> time | None:
    if value is None:
        return None

    cleaned = value.strip()
    if not cleaned or cleaned.lower() in {"none", "off", "all"}:
        return None

    try:
        return datetime.strptime(cleaned, "%H:%M").time()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Expected HH:MM time or 'none', got {value!r}"
        ) from exc


def parse_iso_datetime(value: str) -> datetime:
    cleaned = value.strip().replace("Z", "+00:00")
    return datetime.fromisoformat(cleaned)


def safe_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        if value == "":
            return default
        result = float(value)
        if math.isnan(result) or math.isinf(result):
            return default
        return result
    except (TypeError, ValueError):
        return default


def pct_to_decimal(value: float) -> float:
    return value / 100.0


def format_pct(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.4f}"


def discover_data_files(repo_root: Path, markets: list[str]) -> list[Path]:
    files: list[Path] = []
    for market in markets:
        data_dir = repo_root / market / "data"
        if data_dir.exists():
            files.extend(sorted(data_dir.glob("*_5m.csv")))
    return sorted(files)


def instrument_name(path: Path) -> str:
    stem = path.stem
    for suffix in ("_equity_data_5m", "_data_5m", "_5m"):
        if stem.endswith(suffix):
            return stem[: -len(suffix)]
    return stem


def market_name(path: Path) -> str:
    try:
        return path.parents[1].name
    except IndexError:
        return "unknown"


def load_candles(path: Path) -> list[dict[str, Any]]:
    candles: list[dict[str, Any]] = []

    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = [name for name in REQUIRED_COLUMNS if name not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{path} is missing columns: {', '.join(missing)}")

        for row in reader:
            try:
                candle_time = parse_iso_datetime(row["Date"])
            except ValueError:
                continue

            candle = {
                "Date": row["Date"],
                "dt": candle_time,
                "Open": safe_float(row.get("Open")),
                "High": safe_float(row.get("High")),
                "Low": safe_float(row.get("Low")),
                "Close": safe_float(row.get("Close")),
                "Volume": safe_float(row.get("Volume")),
            }

            if candle["Open"] <= 0 or candle["High"] <= 0 or candle["Low"] <= 0:
                continue
            if candle["High"] < candle["Low"]:
                continue
            candles.append(candle)

    return sorted(candles, key=lambda item: item["dt"])


def group_sessions(
    candles: list[dict[str, Any]],
    session_start: time | None,
    exit_time: time | None,
) -> dict[str, list[dict[str, Any]]]:
    sessions: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for candle in candles:
        candle_time = candle["dt"].time()
        if session_start is not None and candle_time < session_start:
            continue
        if exit_time is not None and candle_time > exit_time:
            continue
        sessions[candle["dt"].date().isoformat()].append(candle)

    return {
        session_date: sorted(day_candles, key=lambda item: item["dt"])
        for session_date, day_candles in sessions.items()
        if day_candles
    }


def is_open_low(first: dict[str, Any], tolerance_pct: float) -> bool:
    tolerance = pct_to_decimal(tolerance_pct)
    return abs(first["Open"] - first["Low"]) / first["Open"] <= tolerance


def is_open_high(first: dict[str, Any], tolerance_pct: float) -> bool:
    tolerance = pct_to_decimal(tolerance_pct)
    return abs(first["High"] - first["Open"]) / first["Open"] <= tolerance


def apply_entry_slippage(price: float, direction: str, slippage_points: float) -> float:
    if direction == "LONG":
        return price + slippage_points
    return max(0.0, price - slippage_points)


def apply_exit_slippage(price: float, direction: str, slippage_points: float) -> float:
    if direction == "LONG":
        return max(0.0, price - slippage_points)
    return price + slippage_points


def slippage_points_for_market(market: str, instrument: str, config: Any) -> float:
    market_name = market.lower()
    instrument_name = instrument.upper()

    if market_name == "derivatives":
        return float(config.derivatives_slippage)
    if market_name == "commodities":
        return float(config.commodities_slippage)
    if any(marker in instrument_name for marker in ("NIFTY", "NSEI", "NSEBANK", "CNX")):
        return float(config.derivatives_slippage)
    return float(config.equity_slippage)


def brokerage_cost(
    entry_price: float,
    exit_price: float,
    quantity: int,
    brokerage_entry_fee: float,
    brokerage_exit_fee: float,
    other_charges: float,
) -> float:
    if quantity <= 0:
        return 0.0
    return brokerage_entry_fee + brokerage_exit_fee + other_charges


def fixed_trade_cost(config: Any) -> float:
    return (
        float(config.brokerage_entry_fee)
        + float(config.brokerage_exit_fee)
        + float(config.other_charges)
    )


def any_slippage_enabled(config: Any) -> bool:
    return any(
        value > 0
        for value in (
            float(config.equity_slippage),
            float(config.derivatives_slippage),
            float(config.commodities_slippage),
        )
    )


def costs_enabled(config: Any) -> bool:
    return fixed_trade_cost(config) > 0 or any_slippage_enabled(config)


def fixed_target_price(
    direction: str,
    entry_price: float,
    stop_price: float,
    config: StrategyConfig,
) -> float | None:
    if config.target_type == "none" or config.target_type == "trailing":
        return None

    if config.target_type == "percent":
        move = pct_to_decimal(config.target_pct)
        if direction == "LONG":
            return entry_price * (1.0 + move)
        return entry_price * (1.0 - move)

    risk_per_unit = abs(entry_price - stop_price)
    if risk_per_unit <= 0:
        return None
    if direction == "LONG":
        return entry_price + (config.risk_reward * risk_per_unit)
    return entry_price - (config.risk_reward * risk_per_unit)


def position_size(
    direction: str,
    entry_price: float,
    stop_price: float,
    config: StrategyConfig,
    slippage_points: float,
) -> int:
    stop_fill = apply_exit_slippage(stop_price, direction, slippage_points)
    risk_per_unit = abs(entry_price - stop_fill)
    if risk_per_unit <= 0:
        return 0

    risk_amount = config.capital * pct_to_decimal(config.risk_per_trade_pct)
    max_notional = config.capital * pct_to_decimal(config.max_allocation_pct)
    risk_qty = math.floor(risk_amount / risk_per_unit)
    allocation_qty = math.floor(max_notional / entry_price)

    return max(0, min(risk_qty, allocation_qty))


def update_trailing_stop(
    direction: str,
    current_stop: float,
    candle: dict[str, Any],
    trailing_stop_pct: float,
) -> float:
    if trailing_stop_pct <= 0:
        return current_stop

    trail = pct_to_decimal(trailing_stop_pct)
    if direction == "LONG":
        return max(current_stop, candle["Close"] * (1.0 - trail))
    return min(current_stop, candle["Close"] * (1.0 + trail))


def exit_trade(
    direction: str,
    session: list[dict[str, Any]],
    entry_index: int,
    entry_price: float,
    initial_stop: float,
    target_price: float | None,
    config: StrategyConfig,
    slippage_points: float,
) -> tuple[str, dict[str, Any], float]:
    active_stop = initial_stop
    exit_reason = "END_OF_DAY"
    exit_candle = session[-1]
    raw_exit_price = session[-1]["Close"]

    for candle in session[entry_index:]:
        if direction == "LONG":
            stop_hit = candle["Low"] <= active_stop
            target_hit = target_price is not None and candle["High"] >= target_price
        else:
            stop_hit = candle["High"] >= active_stop
            target_hit = target_price is not None and candle["Low"] <= target_price

        if stop_hit and target_hit:
            exit_candle = candle
            if config.ambiguous_policy == "target_first":
                raw_exit_price = target_price if target_price is not None else active_stop
                exit_reason = "TARGET_AND_STOP_SAME_CANDLE_TARGET_FIRST"
            else:
                raw_exit_price = active_stop
                exit_reason = "TARGET_AND_STOP_SAME_CANDLE_STOP_FIRST"
            break

        if stop_hit:
            exit_candle = candle
            raw_exit_price = active_stop
            exit_reason = "STOP_LOSS"
            break

        if target_hit:
            exit_candle = candle
            raw_exit_price = target_price if target_price is not None else candle["Close"]
            exit_reason = "TARGET"
            break

        active_stop = update_trailing_stop(
            direction=direction,
            current_stop=active_stop,
            candle=candle,
            trailing_stop_pct=config.trailing_stop_pct,
        )

    return exit_reason, exit_candle, apply_exit_slippage(
        raw_exit_price,
        direction,
        slippage_points,
    )


def build_trade(
    market: str,
    instrument: str,
    session_date: str,
    session: list[dict[str, Any]],
    setup_name: str,
    direction: str,
    signal_index: int,
    entry_index: int,
    stop_price: float,
    config: StrategyConfig,
    gap_pct: float | None,
) -> dict[str, Any] | None:
    first = session[0]
    signal = session[signal_index]
    entry_candle = session[entry_index]
    slippage_points = slippage_points_for_market(market, instrument, config)
    entry_price = apply_entry_slippage(entry_candle["Open"], direction, slippage_points)

    if direction == "LONG" and entry_price <= stop_price:
        return None
    if direction == "SHORT" and entry_price >= stop_price:
        return None

    quantity = position_size(direction, entry_price, stop_price, config, slippage_points)
    if quantity <= 0:
        return None

    target_price = fixed_target_price(direction, entry_price, stop_price, config)
    exit_reason, exit_candle, exit_price = exit_trade(
        direction=direction,
        session=session,
        entry_index=entry_index,
        entry_price=entry_price,
        initial_stop=stop_price,
        target_price=target_price,
        config=config,
        slippage_points=slippage_points,
    )

    if direction == "LONG":
        gross_pnl = (exit_price - entry_price) * quantity
        stop_distance = entry_price - apply_exit_slippage(
            stop_price,
            direction,
            slippage_points,
        )
    else:
        gross_pnl = (entry_price - exit_price) * quantity
        stop_distance = apply_exit_slippage(
            stop_price,
            direction,
            slippage_points,
        ) - entry_price

    costs = brokerage_cost(
        entry_price,
        exit_price,
        quantity,
        config.brokerage_entry_fee,
        config.brokerage_exit_fee,
        config.other_charges,
    )
    net_pnl = gross_pnl - costs
    risk_amount = max(stop_distance * quantity, 0.0)
    r_multiple = net_pnl / risk_amount if risk_amount > 0 else 0.0
    notional = entry_price * quantity

    return {
        "market": market,
        "instrument": instrument,
        "session_date": session_date,
        "setup": setup_name,
        "direction": direction,
        "first_candle_time": first["dt"].isoformat(),
        "first_open": round(first["Open"], 6),
        "first_high": round(first["High"], 6),
        "first_low": round(first["Low"], 6),
        "first_close": round(first["Close"], 6),
        "first_volume": round(first["Volume"], 2),
        "gap_pct": format_pct(gap_pct),
        "signal_time": signal["dt"].isoformat(),
        "signal_close": round(signal["Close"], 6),
        "entry_time": entry_candle["dt"].isoformat(),
        "entry_price": round(entry_price, 6),
        "stop_price": round(stop_price, 6),
        "target_price": round(target_price, 6) if target_price is not None else "",
        "exit_time": exit_candle["dt"].isoformat(),
        "exit_price": round(exit_price, 6),
        "exit_reason": exit_reason,
        "quantity": quantity,
        "notional": round(notional, 2),
        "slippage_points": round(slippage_points, 6),
        "gross_pnl": round(gross_pnl, 2),
        "costs": round(costs, 2),
        "net_pnl": round(net_pnl, 2),
        "return_pct_on_notional": round((net_pnl / notional) * 100.0, 4)
        if notional > 0
        else 0.0,
        "r_multiple": round(r_multiple, 4),
        "holding_candles": max(0, session.index(exit_candle) - entry_index + 1),
    }


def find_trade_for_session(
    market: str,
    instrument: str,
    session_date: str,
    session: list[dict[str, Any]],
    config: StrategyConfig,
    previous_close: float | None,
    skip_counts: dict[str, int],
) -> dict[str, Any] | None:
    if len(session) < 3:
        skip_counts["too_few_candles"] += 1
        return None

    first = session[0]
    if config.session_start is not None and config.require_session_open:
        if first["dt"].time() != config.session_start:
            skip_counts["missing_session_open"] += 1
            return None

    if first["Volume"] < config.min_first_candle_volume:
        skip_counts["first_volume_filter"] += 1
        return None

    if config.min_average_volume > 0:
        avg_volume = sum(candle["Volume"] for candle in session) / len(session)
        if avg_volume < config.min_average_volume:
            skip_counts["average_volume_filter"] += 1
            return None

    gap_pct: float | None = None
    if previous_close and previous_close > 0:
        gap_pct = ((first["Open"] - previous_close) / previous_close) * 100.0
        if config.max_gap_pct > 0 and abs(gap_pct) > config.max_gap_pct:
            skip_counts["gap_filter"] += 1
            return None

    bullish = is_open_low(first, config.tolerance_pct)
    bearish = is_open_high(first, config.tolerance_pct)

    if bullish and bearish:
        skip_counts["ambiguous_first_candle"] += 1
        return None

    if not bullish and not bearish:
        skip_counts["no_open_low_high_setup"] += 1
        return None

    if bullish:
        setup_name = "OPEN_EQUALS_LOW"
        direction = "LONG"
        stop_price = first["Open"] * (1.0 - pct_to_decimal(config.stop_buffer_pct))
        for signal_index in range(1, len(session) - 1):
            if session[signal_index]["Close"] > first["High"]:
                return build_trade(
                    market=market,
                    instrument=instrument,
                    session_date=session_date,
                    session=session,
                    setup_name=setup_name,
                    direction=direction,
                    signal_index=signal_index,
                    entry_index=signal_index + 1,
                    stop_price=stop_price,
                    config=config,
                    gap_pct=gap_pct,
                )
        skip_counts["no_breakout_entry"] += 1
        return None

    setup_name = "OPEN_EQUALS_HIGH"
    direction = "SHORT"
    stop_price = first["Open"] * (1.0 + pct_to_decimal(config.stop_buffer_pct))
    for signal_index in range(1, len(session) - 1):
        if session[signal_index]["Close"] < first["Low"]:
            return build_trade(
                market=market,
                instrument=instrument,
                session_date=session_date,
                session=session,
                setup_name=setup_name,
                direction=direction,
                signal_index=signal_index,
                entry_index=signal_index + 1,
                stop_price=stop_price,
                config=config,
                gap_pct=gap_pct,
            )

    skip_counts["no_breakdown_entry"] += 1
    return None


def backtest_file(
    path: Path,
    config: StrategyConfig,
    skip_counts: dict[str, int],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    market = market_name(path)
    instrument = instrument_name(path)
    candles = load_candles(path)
    sessions = group_sessions(candles, config.session_start, config.exit_time)

    trades: list[dict[str, Any]] = []
    previous_close: float | None = None
    session_count = 0

    for session_date in sorted(sessions):
        session = sessions[session_date]
        session_count += 1
        trade = find_trade_for_session(
            market=market,
            instrument=instrument,
            session_date=session_date,
            session=session,
            config=config,
            previous_close=previous_close,
            skip_counts=skip_counts,
        )
        if trade is not None:
            trades.append(trade)
        previous_close = session[-1]["Close"]

    file_stats = {
        "market": market,
        "instrument": instrument,
        "file": str(path),
        "candles": len(candles),
        "sessions": session_count,
        "trades": len(trades),
    }
    return trades, file_stats


def profit_factor(trades: list[dict[str, Any]]) -> float | str:
    gross_profit = sum(max(float(trade["net_pnl"]), 0.0) for trade in trades)
    gross_loss = abs(sum(min(float(trade["net_pnl"]), 0.0) for trade in trades))
    if gross_loss == 0:
        return "inf" if gross_profit > 0 else ""
    return gross_profit / gross_loss


def max_drawdown_from_equity(equity_values: list[float]) -> tuple[float, float]:
    if not equity_values:
        return 0.0, 0.0

    peak = equity_values[0]
    max_dd = 0.0
    max_dd_pct = 0.0

    for value in equity_values:
        peak = max(peak, value)
        drawdown = value - peak
        drawdown_pct = (drawdown / peak) * 100.0 if peak else 0.0
        if drawdown < max_dd:
            max_dd = drawdown
            max_dd_pct = drawdown_pct

    return max_dd, max_dd_pct


def build_equity_curve(
    trades: list[dict[str, Any]],
    starting_capital: float,
) -> list[dict[str, Any]]:
    equity = starting_capital
    peak = starting_capital
    rows: list[dict[str, Any]] = []

    ordered = sorted(
        trades,
        key=lambda trade: (
            trade["exit_time"],
            trade["market"],
            trade["instrument"],
        ),
    )
    for index, trade in enumerate(ordered, start=1):
        equity += float(trade["net_pnl"])
        peak = max(peak, equity)
        drawdown = equity - peak
        rows.append(
            {
                "trade_number": index,
                "exit_time": trade["exit_time"],
                "session_date": trade["session_date"],
                "market": trade["market"],
                "instrument": trade["instrument"],
                "net_pnl": trade["net_pnl"],
                "equity": round(equity, 2),
                "drawdown": round(drawdown, 2),
                "drawdown_pct": round((drawdown / peak) * 100.0 if peak else 0.0, 4),
            }
        )

    return rows


def build_datewise_pnl(
    trades: list[dict[str, Any]],
    starting_capital: float,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for trade in trades:
        grouped[trade["session_date"]].append(trade)

    equity = starting_capital
    peak = starting_capital
    rows: list[dict[str, Any]] = []

    for session_date in sorted(grouped):
        day_trades = grouped[session_date]
        gross_pnl = sum(float(trade["gross_pnl"]) for trade in day_trades)
        costs = sum(float(trade["costs"]) for trade in day_trades)
        net_pnl = sum(float(trade["net_pnl"]) for trade in day_trades)
        previous_equity = equity
        equity += net_pnl
        peak = max(peak, equity)
        drawdown = equity - peak

        rows.append(
            {
                "date": session_date,
                "trades": len(day_trades),
                "wins": sum(1 for trade in day_trades if float(trade["net_pnl"]) > 0),
                "losses": sum(1 for trade in day_trades if float(trade["net_pnl"]) <= 0),
                "gross_pnl": round(gross_pnl, 2),
                "costs": round(costs, 2),
                "net_pnl": round(net_pnl, 2),
                "day_return_pct": round((net_pnl / previous_equity) * 100.0, 4)
                if previous_equity
                else 0.0,
                "ending_equity": round(equity, 2),
                "drawdown": round(drawdown, 2),
                "drawdown_pct": round((drawdown / peak) * 100.0 if peak else 0.0, 4),
            }
        )

    return rows


def build_instrument_metrics(trades: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for trade in trades:
        grouped[(trade["market"], trade["instrument"])].append(trade)

    rows: list[dict[str, Any]] = []
    for (market, instrument), instrument_trades in sorted(grouped.items()):
        net_values = [float(trade["net_pnl"]) for trade in instrument_trades]
        wins = [value for value in net_values if value > 0]
        losses = [value for value in net_values if value <= 0]
        pf = profit_factor(instrument_trades)
        rows.append(
            {
                "market": market,
                "instrument": instrument,
                "trades": len(instrument_trades),
                "wins": len(wins),
                "losses": len(losses),
                "win_rate_pct": round((len(wins) / len(instrument_trades)) * 100.0, 2)
                if instrument_trades
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
    if len(datewise_rows) < 2:
        return None

    returns = [float(row["day_return_pct"]) / 100.0 for row in datewise_rows]
    stdev = statistics.stdev(returns)
    if stdev == 0:
        return None

    return (statistics.mean(returns) / stdev) * math.sqrt(252)


def build_summary(
    trades: list[dict[str, Any]],
    datewise_rows: list[dict[str, Any]],
    equity_rows: list[dict[str, Any]],
    file_stats: list[dict[str, Any]],
    skip_counts: dict[str, int],
    config: StrategyConfig,
) -> dict[str, Any]:
    net_values = [float(trade["net_pnl"]) for trade in trades]
    wins = [value for value in net_values if value > 0]
    losses = [value for value in net_values if value <= 0]
    total_costs = sum(float(trade.get("costs", 0.0)) for trade in trades)

    equity_values = [config.capital] + [float(row["equity"]) for row in equity_rows]
    max_dd, max_dd_pct = max_drawdown_from_equity(equity_values)
    pf = profit_factor(trades)
    sharpe = sharpe_ratio(datewise_rows)

    return {
        "strategy": "Open = Low / Open = High Strategy (5-min timeframe)",
        "starting_capital": round(config.capital, 2),
        "ending_equity": round(equity_values[-1], 2) if equity_values else round(config.capital, 2),
        "net_pnl": round(sum(net_values), 2),
        "total_trades": len(trades),
        "total_costs": round(total_costs, 2),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate_pct": round((len(wins) / len(trades)) * 100.0, 2) if trades else 0.0,
        "average_profit_loss": round(statistics.mean(net_values), 2) if net_values else 0.0,
        "average_win": round(statistics.mean(wins), 2) if wins else 0.0,
        "average_loss": round(statistics.mean(losses), 2) if losses else 0.0,
        "max_drawdown": round(max_dd, 2),
        "max_drawdown_pct": round(max_dd_pct, 4),
        "profit_factor": round(pf, 4) if isinstance(pf, float) else pf,
        "sharpe_ratio": round(sharpe, 4) if sharpe is not None else "",
        "markets_tested": ",".join(sorted({item["market"] for item in file_stats})),
        "files_tested": len(file_stats),
        "sessions_tested": sum(int(item["sessions"]) for item in file_stats),
        "candles_tested": sum(int(item["candles"]) for item in file_stats),
        "brokerage_calculated": fixed_trade_cost(config) > 0,
        "slippage_calculated": any_slippage_enabled(config),
        "brokerage_entry_fee": config.brokerage_entry_fee,
        "brokerage_exit_fee": config.brokerage_exit_fee,
        "other_charges": config.other_charges,
        "fixed_cost_per_trade": fixed_trade_cost(config),
        "equity_slippage": config.equity_slippage,
        "derivatives_slippage": config.derivatives_slippage,
        "commodities_slippage": config.commodities_slippage,
        "pnl_basis": "Gross P&L; brokerage and slippage disabled"
        if not costs_enabled(config)
        else "Net P&L after fixed brokerage/charges and fixed slippage",
        "skip_counts": dict(sorted(skip_counts.items())),
    }


def csv_fieldnames(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return []
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    return fieldnames


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = csv_fieldnames(rows)

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown_summary(
    path: Path,
    summary: dict[str, Any],
    config: StrategyConfig,
    output_files: list[Path],
) -> None:
    lines = [
        "# Open = Low / Open = High Strategy Backtest",
        "",
        "## Summary",
        "",
    ]
    for key, value in summary.items():
        if key == "skip_counts":
            continue
        lines.append(f"- **{key}**: {value}")

    lines.extend(
        [
            "",
            "## Testing Scope",
            "",
            f"- **markets_tested**: {summary.get('markets_tested', '')}",
            "- **timeframe**: 5-minute candles",
            f"- **files_tested**: {summary.get('files_tested', '')}",
            f"- **sessions_tested**: {summary.get('sessions_tested', '')}",
            f"- **candles_tested**: {summary.get('candles_tested', '')}",
            f"- **total_trades**: {summary.get('total_trades', '')}",
            "",
            "## Cost Model",
            "",
            f"- **brokerage_calculated**: {fixed_trade_cost(config) > 0}",
            f"- **slippage_calculated**: {any_slippage_enabled(config)}",
            f"- **brokerage_entry_fee**: {config.brokerage_entry_fee}",
            f"- **brokerage_exit_fee**: {config.brokerage_exit_fee}",
            f"- **other_charges**: {config.other_charges}",
            f"- **fixed_cost_per_trade**: {fixed_trade_cost(config)}",
            f"- **equity_slippage**: {config.equity_slippage}",
            f"- **derivatives_slippage**: {config.derivatives_slippage}",
            f"- **commodities_slippage**: {config.commodities_slippage}",
            "- **pnl_basis**: Gross P&L; brokerage and slippage disabled"
            if not costs_enabled(config)
            else "- **pnl_basis**: Net P&L after fixed brokerage/charges and fixed slippage",
        ]
    )

    lines.extend(["", "## Skip Counts", ""])
    for key, value in summary["skip_counts"].items():
        lines.append(f"- **{key}**: {value}")

    lines.extend(["", "## Parameters", ""])
    for key, value in config.__dict__.items():
        if isinstance(value, time):
            value = value.strftime("%H:%M")
        lines.append(f"- **{key}**: {value}")

    lines.extend(["", "## Output Files", ""])
    for output_file in output_files:
        lines.append(f"- `{output_file.name}`")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_best_worst_trades(
    trades: list[dict[str, Any]],
    count: int,
) -> list[dict[str, Any]]:
    if not trades:
        return []

    ordered_best = sorted(trades, key=lambda trade: float(trade["net_pnl"]), reverse=True)
    ordered_worst = sorted(trades, key=lambda trade: float(trade["net_pnl"]))
    rows: list[dict[str, Any]] = []

    for rank, trade in enumerate(ordered_best[:count], start=1):
        row = {"rank_type": "BEST", "rank": rank}
        row.update(trade)
        rows.append(row)

    for rank, trade in enumerate(ordered_worst[:count], start=1):
        row = {"rank_type": "WORST", "rank": rank}
        row.update(trade)
        rows.append(row)

    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backtest Open=Low/Open=High 5-minute intraday strategy.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--markets",
        nargs="+",
        choices=MARKETS,
        default=list(MARKETS),
        help="Market folders to scan for *_5m.csv files.",
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
    parser.add_argument(
        "--trailing-stop-pct",
        type=float,
        default=0.0,
        help="Set above 0 to trail stop after each completed candle close.",
    )
    parser.add_argument("--capital", type=float, default=100000.0)
    parser.add_argument("--risk-per-trade-pct", type=float, default=1.0)
    parser.add_argument("--max-allocation-pct", type=float, default=100.0)
    parser.add_argument("--min-first-candle-volume", type=float, default=0.0)
    parser.add_argument("--min-average-volume", type=float, default=0.0)
    parser.add_argument(
        "--max-gap-pct",
        type=float,
        default=0.0,
        help="0 disables the gap filter.",
    )
    parser.add_argument("--brokerage-entry-fee", type=float, default=20.0)
    parser.add_argument("--brokerage-exit-fee", type=float, default=20.0)
    parser.add_argument("--other-charges", type=float, default=10.0)
    parser.add_argument("--equity-slippage", type=float, default=0.2)
    parser.add_argument("--derivatives-slippage", type=float, default=5.0)
    parser.add_argument("--commodities-slippage", type=float, default=0.2)
    parser.add_argument("--session-start", type=parse_clock, default=parse_clock("09:15"))
    parser.add_argument("--exit-time", type=parse_clock, default=parse_clock("15:20"))
    parser.add_argument(
        "--allow-missing-session-open",
        action="store_true",
        help="Use the first available candle when the exact session start is missing.",
    )
    parser.add_argument(
        "--ambiguous-policy",
        choices=("stop_first", "target_first"),
        default="stop_first",
        help="How to handle candles where both stop and target are touched.",
    )
    parser.add_argument("--run-name", default="")
    parser.add_argument("--top-trade-count", type=int, default=10)
    return parser.parse_args()


def config_from_args(args: argparse.Namespace) -> StrategyConfig:
    return StrategyConfig(
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
        brokerage_entry_fee=args.brokerage_entry_fee,
        brokerage_exit_fee=args.brokerage_exit_fee,
        other_charges=args.other_charges,
        equity_slippage=args.equity_slippage,
        derivatives_slippage=args.derivatives_slippage,
        commodities_slippage=args.commodities_slippage,
        session_start=args.session_start,
        exit_time=args.exit_time,
        require_session_open=not args.allow_missing_session_open,
        ambiguous_policy=args.ambiguous_policy,
        top_trade_count=args.top_trade_count,
    )


def json_ready(value: Any) -> Any:
    if isinstance(value, time):
        return value.strftime("%H:%M")
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {key: json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_ready(item) for item in value]
    return value


def main() -> None:
    args = parse_args()
    config = config_from_args(args)

    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[2]
    common_root = script_path.parents[1]
    results_root = common_root / "results"
    run_name = args.run_name.strip() or f"open_low_high_5m_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_dir = results_root / run_name
    output_dir.mkdir(parents=True, exist_ok=True)

    data_files = discover_data_files(repo_root, args.markets)
    if not data_files:
        raise SystemExit("No *_5m.csv files found in selected market data folders.")

    all_trades: list[dict[str, Any]] = []
    file_stats: list[dict[str, Any]] = []
    skip_counts: dict[str, int] = defaultdict(int)

    print(f"Running Open=Low/Open=High 5m backtest on {len(data_files)} files...")
    for path in data_files:
        trades, stats = backtest_file(path, config, skip_counts)
        all_trades.extend(trades)
        file_stats.append(stats)
        print(
            f"{stats['market']}/{stats['instrument']}: "
            f"{stats['sessions']} sessions, {stats['trades']} trades"
        )

    equity_rows = build_equity_curve(all_trades, config.capital)
    datewise_rows = build_datewise_pnl(all_trades, config.capital)
    instrument_rows = build_instrument_metrics(all_trades)
    best_worst_rows = build_best_worst_trades(all_trades, config.top_trade_count)
    summary = build_summary(
        trades=all_trades,
        datewise_rows=datewise_rows,
        equity_rows=equity_rows,
        file_stats=file_stats,
        skip_counts=skip_counts,
        config=config,
    )

    output_paths = {
        "trades": output_dir / "trades.csv",
        "datewise_pnl": output_dir / "datewise_pnl.csv",
        "equity_curve": output_dir / "equity_curve.csv",
        "instrument_metrics": output_dir / "instrument_metrics.csv",
        "best_worst_trades": output_dir / "best_worst_trades.csv",
        "summary": output_dir / "summary.json",
        "run_config": output_dir / "run_config.json",
        "summary_markdown": output_dir / "summary.md",
    }
    output_files = list(output_paths.values())

    write_csv(output_paths["trades"], all_trades)
    write_csv(output_paths["datewise_pnl"], datewise_rows)
    write_csv(output_paths["equity_curve"], equity_rows)
    write_csv(output_paths["instrument_metrics"], instrument_rows)
    write_csv(output_paths["best_worst_trades"], best_worst_rows)
    output_paths["summary"].write_text(
        json.dumps(json_ready(summary), indent=2),
        encoding="utf-8",
    )
    output_paths["run_config"].write_text(
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
    write_markdown_summary(
        output_paths["summary_markdown"],
        summary,
        config,
        output_files,
    )

    print("")
    print(f"Results written to: {output_dir}")
    print(f"Total trades: {summary['total_trades']}")
    print(f"Win rate: {summary['win_rate_pct']}%")
    print(f"Net P&L: {summary['net_pnl']}")
    print(f"Max drawdown: {summary['max_drawdown']} ({summary['max_drawdown_pct']}%)")
    print(f"Profit factor: {summary['profit_factor']}")
    print(f"Sharpe ratio: {summary['sharpe_ratio']}")


if __name__ == "__main__":
    main()
