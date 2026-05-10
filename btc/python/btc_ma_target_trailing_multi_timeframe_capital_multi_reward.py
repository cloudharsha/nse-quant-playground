#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import btc_ma_continuous_trailing_multi_timeframe as base


LOG_FILENAME = base.LOG_FILENAME
TIMEFRAME_ORDER = base.TIMEFRAME_ORDER
TIMEFRAME_SPECS = base.TIMEFRAME_SPECS
CAPITAL_MODE = "fixed_notional_per_trade"
COST_MODEL = "none"
SHORT_MODE = "enabled_symmetric_1x"
DEFAULT_TARGET_LEVELS = (3.0, 4.0, 5.0)
MAX_ENTRY_GAP_PCT = 0.5
AMBIGUOUS_POLICY = "stop_first"
ENTRY_RULE = (
    "close_above_ma_long_close_below_ma_short_and_entry_requires_close_within_0.5pct_of_ma"
)
POST_TARGET_REENTRY_RULE = (
    "block_same_direction_same_candle_reentry_after_target_allow_same_candle_reversal_if_signal_flips"
)
TARGET_EXIT_REASON = "target_hit_rr"


@dataclass
class ActiveTrade:
    trade_id: str
    entry_date: str
    signal_timestamp: str
    entry_timestamp: str
    direction: str
    entry_price: float
    entry_ma: float
    stop_ma: float
    initial_stop_ma: float
    initial_risk_points: float
    target_price: float
    quantity_btc: float
    entry_notional_usd: float
    entry_gap_pct: float
    entry_dt: dt.datetime


@dataclass
class TradeResult:
    trade_id: str
    report_date: str
    entry_date: str
    exit_date: str
    signal_timestamp: str
    entry_timestamp: str
    direction: str
    entry_price_points: str
    entry_ma: str
    initial_stop_points: str
    initial_risk_points: str
    target_price_points: str
    entry_gap_pct: str
    exit_candle_timestamp: str
    exit_timestamp: str
    exit_price_points: str
    exit_reason: str
    exit_ma: str
    points_pnl: str
    quantity_btc: str
    entry_notional_usd: str
    exit_notional_usd: str
    gross_pnl_usd: str
    trade_return_pct: str
    cumulative_pnl_usd: str
    equity_after_trade: str
    holding_days: str
    remarks: str


@dataclass
class DayResult:
    date: str
    status: str
    trades: str
    gap_events: str
    long_trades: str
    short_trades: str
    stop_exits: str
    target_exits: str
    gap_exits: str
    end_of_data_exits: str
    winning_trades: str
    losing_trades: str
    break_even_trades: str
    total_points: str
    average_points: str
    max_profit_points: str
    max_loss_points: str
    total_pnl_usd: str
    average_pnl_usd: str
    max_profit_usd: str
    max_loss_usd: str
    ending_equity: str
    max_consecutive_wins: str
    max_consecutive_losses: str
    max_drawdown_points: str
    max_drawdown_usd: str
    max_drawdown_pct: str
    remarks: str


@dataclass
class AggregateResult:
    period: str
    days: str
    held_days: str
    flat_days: str
    skipped_days: str
    trades: str
    gap_events: str
    long_trades: str
    short_trades: str
    stop_exits: str
    target_exits: str
    gap_exits: str
    end_of_data_exits: str
    winning_days: str
    losing_days: str
    break_even_days: str
    total_points: str
    average_points: str
    total_pnl_usd: str
    average_pnl_usd: str
    ending_equity: str
    max_profit_date: str
    max_profit_points: str
    max_profit_usd: str
    max_loss_date: str
    max_loss_points: str
    max_loss_usd: str
    max_consecutive_wins: str
    max_consecutive_losses: str
    max_drawdown_points: str
    max_drawdown_usd: str
    max_drawdown_pct: str


@dataclass
class EquityCurveRow:
    trade_id: str
    report_date: str
    exit_timestamp: str
    direction: str
    gross_pnl_usd: str
    cumulative_pnl_usd: str
    equity: str
    peak_equity: str
    drawdown_usd: str
    drawdown_pct: str


@dataclass
class TimeframeRun:
    spec: base.TimeframeSpec
    input_file: Path
    output_dir: Path
    trade_results: list[TradeResult]
    gap_events: list[base.GapEvent]
    candidate_days: list[str]
    held_days: set[str]
    first_csv_timestamp: str
    first_ma_timestamp: str
    activation_timestamp: str
    total_source_rows: int
    filtered_rows: int
    processed_rows: int
    capital: float
    target_risk_reward: float


def format_reward_value(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else f"{value:g}"


def reward_label(value: float) -> str:
    return f"{format_reward_value(value)}R"


def reward_slug(value: float) -> str:
    return format_reward_value(value).replace(".", "p")


def build_target_rule(target_risk_reward: float) -> str:
    return (
        f"fixed_{format_reward_value(target_risk_reward).lower()}r_"
        "from_entry_to_initial_ma_stop_with_trailing_ma_stop"
    )


def build_strategy_name(target_risk_reward: float) -> str:
    return (
        "BTC local multi-timeframe "
        f"{reward_label(target_risk_reward)} target with trailing MA stop "
        "fixed-notional capital backtest"
    )


def build_multi_reward_strategy_name(target_levels: tuple[float, ...]) -> str:
    levels = ", ".join(reward_label(level) for level in target_levels)
    return (
        "BTC local multi-timeframe multi-reward target with trailing MA stop "
        f"fixed-notional capital backtest ({levels})"
    )


def parse_target_levels(values: list[float]) -> tuple[float, ...]:
    levels: list[float] = []
    seen: set[str] = set()
    for value in values:
        if value <= 0:
            raise ValueError("all target levels must be > 0")
        normalized = float(value)
        key = reward_slug(normalized)
        if key in seen:
            continue
        seen.add(key)
        levels.append(normalized)
    if not levels:
        raise ValueError("at least one target level is required")
    return tuple(levels)


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(
        description="BTC local multi-timeframe multi-reward MA target backtest with fixed-notional capital."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=repo_root / "btc" / "data",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=repo_root / "btc" / "results",
    )
    parser.add_argument("--run-name", default="")
    parser.add_argument("--initial-start-time", default="00:00")
    parser.add_argument("--start-date", default="")
    parser.add_argument("--end-date", default="")
    parser.add_argument(
        "--timeframes",
        nargs="+",
        choices=TIMEFRAME_ORDER,
        default=list(TIMEFRAME_ORDER),
    )
    parser.add_argument(
        "--target-levels",
        nargs="+",
        type=float,
        default=list(DEFAULT_TARGET_LEVELS),
    )
    parser.add_argument("--capital", type=float, default=1000000.0)
    args = parser.parse_args()

    base.validate_optional_date(parser, args.start_date, "--start-date")
    base.validate_optional_date(parser, args.end_date, "--end-date")
    base.validate_time(parser, args.initial_start_time, "--initial-start-time")
    if args.start_date and args.end_date and args.start_date > args.end_date:
        parser.error("--start-date must be <= --end-date")
    minute = int(args.initial_start_time.split(":")[1])
    if minute not in (0, 15, 30, 45):
        parser.error("--initial-start-time minutes must be one of 00, 15, 30, 45")
    if args.capital <= 0:
        parser.error("--capital must be > 0")
    try:
        args.target_levels = parse_target_levels(args.target_levels)
    except ValueError as exc:
        parser.error(f"--target-levels {exc}")
    return args


def format_amount(value: float) -> str:
    return f"{value:.2f}"


def format_quantity(value: float) -> str:
    return f"{value:.8f}"


def format_pct(value: float) -> str:
    return f"{value:.4f}"


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def display_path(path: Path, repo_root: Path) -> str:
    return base.display_path(path, repo_root)


def json_ready(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, set):
        return sorted(value)
    if isinstance(value, dt.datetime):
        return base.format_timestamp(value)
    if hasattr(value, "__dataclass_fields__"):
        return {key: json_ready(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {key: json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_ready(item) for item in value]
    return value


def compute_max_consecutive_streaks(values: list[float]) -> tuple[int, int]:
    max_wins = 0
    max_losses = 0
    current_wins = 0
    current_losses = 0

    for value in values:
        if value > 0:
            current_wins += 1
            current_losses = 0
            max_wins = max(max_wins, current_wins)
        elif value < 0:
            current_losses += 1
            current_wins = 0
            max_losses = max(max_losses, current_losses)
        else:
            current_wins = 0
            current_losses = 0

    return max_wins, max_losses


def compute_max_drawdown(point_values: list[float]) -> float:
    cumulative = 0.0
    peak = 0.0
    max_drawdown = 0.0
    for value in point_values:
        cumulative += value
        peak = max(peak, cumulative)
        max_drawdown = max(max_drawdown, peak - cumulative)
    return max_drawdown


def compute_max_drawdown_from_equity(equity_values: list[float]) -> tuple[float, float]:
    if not equity_values:
        return 0.0, 0.0

    peak = equity_values[0]
    max_drawdown = 0.0
    max_drawdown_pct = 0.0
    for equity in equity_values:
        peak = max(peak, equity)
        drawdown = peak - equity
        drawdown_pct = (drawdown / peak * 100.0) if peak else 0.0
        max_drawdown = max(max_drawdown, drawdown)
        max_drawdown_pct = max(max_drawdown_pct, drawdown_pct)
    return max_drawdown, max_drawdown_pct


def extend_held_days(held_days: set[str], active_trade: ActiveTrade, exit_timestamp: str) -> None:
    exit_date = exit_timestamp[:10]
    held_days.update(base.date_strings_between(active_trade.entry_date, exit_date))


def evaluate_entry(
    row: base.PriceRow,
    boundary_dt: dt.datetime,
    trade_id: str,
    capital: float,
    target_risk_reward: float,
    blocked_direction_after_target: str | None = None,
) -> ActiveTrade | None:
    if row.ma_value is None:
        return None

    entry_gap_pct = abs(row.close_value - row.ma_value) / row.ma_value * 100.0
    if entry_gap_pct > MAX_ENTRY_GAP_PCT:
        return None

    if row.close_value > row.ma_value:
        direction = "LONG"
    elif row.close_value < row.ma_value:
        direction = "SHORT"
    else:
        return None

    if blocked_direction_after_target == direction:
        return None

    initial_stop_ma = row.ma_value
    initial_risk_points = abs(row.close_value - initial_stop_ma)
    if initial_risk_points <= 0:
        return None

    if direction == "LONG":
        target_price = row.close_value + (initial_risk_points * target_risk_reward)
    else:
        target_price = row.close_value - (initial_risk_points * target_risk_reward)

    quantity_btc = capital / row.close_value
    entry_notional_usd = row.close_value * quantity_btc

    return ActiveTrade(
        trade_id=trade_id,
        entry_date=boundary_dt.date().isoformat(),
        signal_timestamp=row.timestamp,
        entry_timestamp=base.format_timestamp(boundary_dt),
        direction=direction,
        entry_price=row.close_value,
        entry_ma=row.ma_value,
        stop_ma=row.ma_value,
        initial_stop_ma=initial_stop_ma,
        initial_risk_points=initial_risk_points,
        target_price=target_price,
        quantity_btc=quantity_btc,
        entry_notional_usd=entry_notional_usd,
        entry_gap_pct=entry_gap_pct,
        entry_dt=boundary_dt,
    )


def candle_stop_hit(active_trade: ActiveTrade, row: base.PriceRow) -> bool:
    if active_trade.direction == "LONG":
        return row.low_value <= active_trade.stop_ma
    return row.high_value >= active_trade.stop_ma


def candle_target_hit(active_trade: ActiveTrade, row: base.PriceRow) -> bool:
    if active_trade.direction == "LONG":
        return row.high_value >= active_trade.target_price
    return row.low_value <= active_trade.target_price


def build_trade_result(
    active_trade: ActiveTrade,
    exit_candle_timestamp: str,
    exit_timestamp: str,
    exit_price: float,
    exit_reason: str,
    exit_ma: float,
    capital: float,
    cumulative_pnl_usd_before: float,
    remarks: str = "",
) -> tuple[TradeResult, float]:
    exit_date = exit_timestamp[:10]
    if active_trade.direction == "LONG":
        points_pnl = exit_price - active_trade.entry_price
    else:
        points_pnl = active_trade.entry_price - exit_price

    exit_notional_usd = exit_price * active_trade.quantity_btc
    gross_pnl_usd = points_pnl * active_trade.quantity_btc
    cumulative_pnl_usd_after = cumulative_pnl_usd_before + gross_pnl_usd
    equity_after_trade = capital + cumulative_pnl_usd_after
    trade_return_pct = (gross_pnl_usd / capital * 100.0) if capital else 0.0

    return (
        TradeResult(
            trade_id=active_trade.trade_id,
            report_date=exit_date,
            entry_date=active_trade.entry_date,
            exit_date=exit_date,
            signal_timestamp=active_trade.signal_timestamp,
            entry_timestamp=active_trade.entry_timestamp,
            direction=active_trade.direction,
            entry_price_points=format_amount(active_trade.entry_price),
            entry_ma=format_amount(active_trade.entry_ma),
            initial_stop_points=format_amount(active_trade.initial_stop_ma),
            initial_risk_points=format_amount(active_trade.initial_risk_points),
            target_price_points=format_amount(active_trade.target_price),
            entry_gap_pct=format_pct(active_trade.entry_gap_pct),
            exit_candle_timestamp=exit_candle_timestamp,
            exit_timestamp=exit_timestamp,
            exit_price_points=format_amount(exit_price),
            exit_reason=exit_reason,
            exit_ma=format_amount(exit_ma),
            points_pnl=format_amount(points_pnl),
            quantity_btc=format_quantity(active_trade.quantity_btc),
            entry_notional_usd=format_amount(active_trade.entry_notional_usd),
            exit_notional_usd=format_amount(exit_notional_usd),
            gross_pnl_usd=format_amount(gross_pnl_usd),
            trade_return_pct=format_pct(trade_return_pct),
            cumulative_pnl_usd=format_amount(cumulative_pnl_usd_after),
            equity_after_trade=format_amount(equity_after_trade),
            holding_days=base.holding_days(active_trade.entry_date, exit_date),
            remarks=remarks,
        ),
        cumulative_pnl_usd_after,
    )


def run_backtest(
    spec: base.TimeframeSpec,
    input_file: Path,
    output_dir: Path,
    initial_start_time: str,
    start_date: str,
    end_date: str,
    capital: float,
    target_risk_reward: float,
) -> TimeframeRun:
    logger = base.configure_logger(
        output_dir / LOG_FILENAME,
        "btc_ma_target_trailing_multi_timeframe_capital_multi_reward_"
        f"{spec.timeframe}_rr{reward_slug(target_risk_reward)}",
    )
    rows = base.load_price_rows(input_file, spec.ma_period)
    candidate_rows = base.filter_price_rows(rows, start_date, end_date)
    if not candidate_rows:
        raise SystemExit(f"{spec.timeframe}: no rows remain after applying the date filters.")

    first_ma_row = next((row for row in rows if row.ma_value is not None), None)
    if first_ma_row is None:
        raise SystemExit(
            f"{spec.timeframe}: the BTC dataset does not contain enough rows to compute MA {spec.ma_period}."
        )

    activation_row = base.compute_activation_row(candidate_rows, initial_start_time)
    activation_timestamp = activation_row.timestamp
    active_rows = [row for row in candidate_rows if row.dt >= activation_row.dt]
    if not active_rows:
        raise SystemExit(f"{spec.timeframe}: no rows remain after the activation threshold.")

    candidate_days = base.date_strings_between(candidate_rows[0].date, candidate_rows[-1].date)
    trade_results: list[TradeResult] = []
    gap_events: list[base.GapEvent] = []
    held_days: set[str] = set()
    active_trade: ActiveTrade | None = None
    prev_row: base.PriceRow | None = None
    last_processed_row: base.PriceRow | None = None
    trade_counter = 1
    gap_counter = 1
    cumulative_pnl_usd = 0.0

    logger.info(
        "ACTIVATION timeframe=%s start=%s source_rows=%s filtered_rows=%s processed_rows=%s first_ma=%s",
        spec.timeframe,
        activation_timestamp,
        len(rows),
        len(candidate_rows),
        len(active_rows),
        first_ma_row.timestamp,
    )

    for row in active_rows:
        blocked_direction_after_target: str | None = None

        if prev_row is not None:
            missing_candles = base.missing_candle_count(prev_row, row, spec.step_minutes)
            if missing_candles > 0:
                forced_exit_trade_id = ""
                had_active_trade = active_trade is not None
                gap_boundary_dt = prev_row.dt + spec.step_delta
                report_date = gap_boundary_dt.date().isoformat()
                remarks = (
                    f"Missing {missing_candles} candle(s) between {prev_row.timestamp} "
                    f"and {row.timestamp}; resumed on next available row."
                )
                if active_trade is not None:
                    gap_exit, cumulative_pnl_usd = build_trade_result(
                        active_trade=active_trade,
                        exit_candle_timestamp=prev_row.timestamp,
                        exit_timestamp=base.format_timestamp(gap_boundary_dt),
                        exit_price=prev_row.close_value,
                        exit_reason="gap_exit_missing_candles",
                        exit_ma=active_trade.stop_ma,
                        capital=capital,
                        cumulative_pnl_usd_before=cumulative_pnl_usd,
                        remarks=remarks,
                    )
                    trade_results.append(gap_exit)
                    extend_held_days(held_days, active_trade, gap_exit.exit_timestamp)
                    forced_exit_trade_id = active_trade.trade_id
                    logger.info(
                        "GAP_EXIT timeframe=%s trade_id=%s direction=%s exit=%s exit_price=%s missing_candles=%s",
                        spec.timeframe,
                        active_trade.trade_id,
                        active_trade.direction,
                        gap_exit.exit_timestamp,
                        gap_exit.exit_price_points,
                        missing_candles,
                    )
                    active_trade = None

                gap_event = base.GapEvent(
                    event_id=base.make_gap_id(gap_counter),
                    report_date=report_date,
                    gap_start_timestamp=prev_row.timestamp,
                    gap_resume_timestamp=row.timestamp,
                    missing_candles=str(missing_candles),
                    had_active_trade="YES" if had_active_trade else "NO",
                    forced_exit_trade_id=forced_exit_trade_id,
                    pre_gap_close_points=format_amount(prev_row.close_value),
                    pre_gap_ma=format_amount(prev_row.ma_value) if prev_row.ma_value is not None else "",
                    remarks=remarks,
                )
                gap_events.append(gap_event)
                gap_counter += 1
                logger.info(
                    "GAP timeframe=%s event_id=%s start=%s resume=%s missing_candles=%s active_trade=%s",
                    spec.timeframe,
                    gap_event.event_id,
                    gap_event.gap_start_timestamp,
                    gap_event.gap_resume_timestamp,
                    gap_event.missing_candles,
                    gap_event.had_active_trade,
                )

        boundary_dt = row.dt + spec.step_delta
        if active_trade is not None and boundary_dt > active_trade.entry_dt:
            stop_hit = candle_stop_hit(active_trade, row)
            target_hit = candle_target_hit(active_trade, row)

            if stop_hit:
                stop_exit, cumulative_pnl_usd = build_trade_result(
                    active_trade=active_trade,
                    exit_candle_timestamp=row.timestamp,
                    exit_timestamp=base.format_timestamp(boundary_dt),
                    exit_price=active_trade.stop_ma,
                    exit_reason="stop_loss_ma_touch",
                    exit_ma=active_trade.stop_ma,
                    capital=capital,
                    cumulative_pnl_usd_before=cumulative_pnl_usd,
                )
                trade_results.append(stop_exit)
                extend_held_days(held_days, active_trade, stop_exit.exit_timestamp)
                logger.info(
                    "STOP_EXIT timeframe=%s trade_id=%s direction=%s exit=%s exit_price=%s target=%s",
                    spec.timeframe,
                    active_trade.trade_id,
                    active_trade.direction,
                    stop_exit.exit_timestamp,
                    stop_exit.exit_price_points,
                    stop_exit.target_price_points,
                )
                active_trade = None
            elif target_hit:
                blocked_direction_after_target = active_trade.direction
                target_exit, cumulative_pnl_usd = build_trade_result(
                    active_trade=active_trade,
                    exit_candle_timestamp=row.timestamp,
                    exit_timestamp=base.format_timestamp(boundary_dt),
                    exit_price=active_trade.target_price,
                    exit_reason=TARGET_EXIT_REASON,
                    exit_ma=active_trade.stop_ma,
                    capital=capital,
                    cumulative_pnl_usd_before=cumulative_pnl_usd,
                    remarks=f"Fixed {reward_label(target_risk_reward)} target hit.",
                )
                trade_results.append(target_exit)
                extend_held_days(held_days, active_trade, target_exit.exit_timestamp)
                logger.info(
                    "TARGET_EXIT timeframe=%s trade_id=%s direction=%s exit=%s exit_price=%s stop_ma=%s",
                    spec.timeframe,
                    active_trade.trade_id,
                    active_trade.direction,
                    target_exit.exit_timestamp,
                    target_exit.exit_price_points,
                    target_exit.exit_ma,
                )
                active_trade = None
            elif row.ma_value is not None:
                active_trade.stop_ma = row.ma_value

        if active_trade is None and row.ma_value is not None:
            new_trade = evaluate_entry(
                row=row,
                boundary_dt=boundary_dt,
                trade_id=base.make_trade_id(trade_counter),
                capital=capital,
                target_risk_reward=target_risk_reward,
                blocked_direction_after_target=blocked_direction_after_target,
            )
            if new_trade is not None:
                active_trade = new_trade
                trade_counter += 1
                logger.info(
                    "ENTRY timeframe=%s trade_id=%s direction=%s signal=%s entry=%s entry_price=%s stop_ma=%s target=%s gap_pct=%s",
                    spec.timeframe,
                    active_trade.trade_id,
                    active_trade.direction,
                    active_trade.signal_timestamp,
                    active_trade.entry_timestamp,
                    format_amount(active_trade.entry_price),
                    format_amount(active_trade.stop_ma),
                    format_amount(active_trade.target_price),
                    format_pct(active_trade.entry_gap_pct),
                )

        prev_row = row
        last_processed_row = row

    if active_trade is not None and last_processed_row is not None:
        final_exit, cumulative_pnl_usd = build_trade_result(
            active_trade=active_trade,
            exit_candle_timestamp=last_processed_row.timestamp,
            exit_timestamp=base.format_timestamp(last_processed_row.dt + spec.step_delta),
            exit_price=last_processed_row.close_value,
            exit_reason="end_of_data",
            exit_ma=active_trade.stop_ma,
            capital=capital,
            cumulative_pnl_usd_before=cumulative_pnl_usd,
        )
        trade_results.append(final_exit)
        extend_held_days(held_days, active_trade, final_exit.exit_timestamp)
        logger.info(
            "EOD_EXIT timeframe=%s trade_id=%s direction=%s exit=%s exit_price=%s",
            spec.timeframe,
            active_trade.trade_id,
            active_trade.direction,
            final_exit.exit_timestamp,
            final_exit.exit_price_points,
        )

    logger.info(
        "COMPLETED timeframe=%s trades=%s targets=%s gaps=%s candidate_days=%s",
        spec.timeframe,
        len(trade_results),
        sum(1 for result in trade_results if result.exit_reason == TARGET_EXIT_REASON),
        len(gap_events),
        len(candidate_days),
    )

    return TimeframeRun(
        spec=spec,
        input_file=input_file,
        output_dir=output_dir,
        trade_results=trade_results,
        gap_events=gap_events,
        candidate_days=candidate_days,
        held_days=held_days,
        first_csv_timestamp=rows[0].timestamp,
        first_ma_timestamp=first_ma_row.timestamp,
        activation_timestamp=activation_timestamp,
        total_source_rows=len(rows),
        filtered_rows=len(candidate_rows),
        processed_rows=len(active_rows),
        capital=capital,
        target_risk_reward=target_risk_reward,
    )


def build_equity_curve_rows(
    trade_results: list[TradeResult],
    capital: float,
) -> list[EquityCurveRow]:
    rows: list[EquityCurveRow] = []
    peak_equity = capital

    for trade in trade_results:
        equity = float(trade.equity_after_trade)
        peak_equity = max(peak_equity, equity)
        drawdown_usd = peak_equity - equity
        drawdown_pct = (drawdown_usd / peak_equity * 100.0) if peak_equity else 0.0
        rows.append(
            EquityCurveRow(
                trade_id=trade.trade_id,
                report_date=trade.report_date,
                exit_timestamp=trade.exit_timestamp,
                direction=trade.direction,
                gross_pnl_usd=trade.gross_pnl_usd,
                cumulative_pnl_usd=trade.cumulative_pnl_usd,
                equity=trade.equity_after_trade,
                peak_equity=format_amount(peak_equity),
                drawdown_usd=format_amount(drawdown_usd),
                drawdown_pct=format_pct(drawdown_pct),
            )
        )

    return rows


def summarize_trades(results: list[TradeResult], capital: float) -> dict[str, Any]:
    point_values = [float(result.points_pnl) for result in results]
    usd_values = [float(result.gross_pnl_usd) for result in results]
    total_points = sum(point_values)
    gross_pnl_usd = sum(usd_values)
    max_wins, max_losses = compute_max_consecutive_streaks(usd_values)
    max_drawdown_points = compute_max_drawdown(point_values)
    ending_equity = capital + gross_pnl_usd
    total_return_pct = (gross_pnl_usd / capital * 100.0) if capital else 0.0
    max_drawdown_usd, max_drawdown_pct = compute_max_drawdown_from_equity(
        [capital] + [float(result.equity_after_trade) for result in results]
    )

    return {
        "trades": len(results),
        "long_trades": sum(1 for result in results if result.direction == "LONG"),
        "short_trades": sum(1 for result in results if result.direction == "SHORT"),
        "stop_exits": sum(1 for result in results if result.exit_reason == "stop_loss_ma_touch"),
        "target_exits": sum(1 for result in results if result.exit_reason == TARGET_EXIT_REASON),
        "gap_exits": sum(1 for result in results if result.exit_reason == "gap_exit_missing_candles"),
        "end_of_data_exits": sum(1 for result in results if result.exit_reason == "end_of_data"),
        "winning_trades": sum(1 for value in usd_values if value > 0),
        "losing_trades": sum(1 for value in usd_values if value < 0),
        "break_even_trades": sum(1 for value in usd_values if value == 0),
        "total_points": total_points,
        "average_points": total_points / len(results) if results else 0.0,
        "gross_pnl_usd": gross_pnl_usd,
        "average_pnl_usd": gross_pnl_usd / len(results) if results else 0.0,
        "ending_equity": ending_equity,
        "total_return_pct": total_return_pct,
        "max_profit": max(results, key=lambda result: float(result.gross_pnl_usd), default=None),
        "max_loss": min(results, key=lambda result: float(result.gross_pnl_usd), default=None),
        "max_consecutive_wins": max_wins,
        "max_consecutive_losses": max_losses,
        "max_drawdown_points": max_drawdown_points,
        "max_drawdown_usd": max_drawdown_usd,
        "max_drawdown_pct": max_drawdown_pct,
        "win_rate_pct": (sum(1 for value in usd_values if value > 0) / len(results) * 100.0)
        if results
        else 0.0,
    }


def build_daywise_results(run: TimeframeRun) -> list[DayResult]:
    trades_by_day: dict[str, list[TradeResult]] = {}
    gaps_by_day: dict[str, list[base.GapEvent]] = {}
    for trade in run.trade_results:
        trades_by_day.setdefault(trade.report_date, []).append(trade)
    for gap_event in run.gap_events:
        gaps_by_day.setdefault(gap_event.report_date, []).append(gap_event)

    report_days = sorted(set(run.candidate_days) | set(trades_by_day) | set(gaps_by_day))
    current_equity = run.capital
    rows: list[DayResult] = []

    for day in report_days:
        day_trades = trades_by_day.get(day, [])
        day_gaps = gaps_by_day.get(day, [])
        point_values = [float(result.points_pnl) for result in day_trades]
        usd_values = [float(result.gross_pnl_usd) for result in day_trades]
        total_points = sum(point_values)
        total_pnl_usd = sum(usd_values)
        max_wins, max_losses = compute_max_consecutive_streaks(usd_values)
        max_drawdown_points = compute_max_drawdown(point_values)

        if day_trades and day_gaps:
            status = "MIXED"
        elif day_trades:
            status = "TRADED"
        elif day_gaps:
            status = "SKIPPED"
        elif day in run.held_days:
            status = "HELD"
        else:
            status = "FLAT"

        remarks_parts = [gap_event.remarks for gap_event in day_gaps if gap_event.remarks]
        if status == "HELD" and not remarks_parts:
            remarks_parts.append("Open position carried through this UTC date with no realized exit.")

        equity_values = [current_equity]
        if day_trades:
            equity_values.extend(float(result.equity_after_trade) for result in day_trades)
            current_equity = float(day_trades[-1].equity_after_trade)
        max_drawdown_usd, max_drawdown_pct = compute_max_drawdown_from_equity(equity_values)

        rows.append(
            DayResult(
                date=day,
                status=status,
                trades=str(len(day_trades)),
                gap_events=str(len(day_gaps)),
                long_trades=str(sum(1 for result in day_trades if result.direction == "LONG")),
                short_trades=str(sum(1 for result in day_trades if result.direction == "SHORT")),
                stop_exits=str(
                    sum(1 for result in day_trades if result.exit_reason == "stop_loss_ma_touch")
                ),
                target_exits=str(
                    sum(1 for result in day_trades if result.exit_reason == TARGET_EXIT_REASON)
                ),
                gap_exits=str(
                    sum(1 for result in day_trades if result.exit_reason == "gap_exit_missing_candles")
                ),
                end_of_data_exits=str(
                    sum(1 for result in day_trades if result.exit_reason == "end_of_data")
                ),
                winning_trades=str(sum(1 for value in usd_values if value > 0)),
                losing_trades=str(sum(1 for value in usd_values if value < 0)),
                break_even_trades=str(sum(1 for value in usd_values if value == 0)),
                total_points=format_amount(total_points),
                average_points=format_amount(total_points / len(day_trades) if day_trades else 0.0),
                max_profit_points=format_amount(max(point_values)) if point_values else "",
                max_loss_points=format_amount(min(point_values)) if point_values else "",
                total_pnl_usd=format_amount(total_pnl_usd),
                average_pnl_usd=format_amount(total_pnl_usd / len(day_trades) if day_trades else 0.0),
                max_profit_usd=format_amount(max(usd_values)) if usd_values else "",
                max_loss_usd=format_amount(min(usd_values)) if usd_values else "",
                ending_equity=format_amount(current_equity),
                max_consecutive_wins=str(max_wins),
                max_consecutive_losses=str(max_losses),
                max_drawdown_points=format_amount(max_drawdown_points),
                max_drawdown_usd=format_amount(max_drawdown_usd),
                max_drawdown_pct=format_pct(max_drawdown_pct),
                remarks="; ".join(remarks_parts),
            )
        )

    return rows


def aggregate_day_results(period: str, rows: list[DayResult]) -> AggregateResult:
    traded_rows = [row for row in rows if int(row.trades) > 0]
    point_values = [float(row.total_points) for row in traded_rows]
    usd_values = [float(row.total_pnl_usd) for row in traded_rows]
    total_points = sum(point_values)
    total_pnl_usd = sum(usd_values)
    max_wins, max_losses = compute_max_consecutive_streaks(usd_values)
    max_drawdown_points = compute_max_drawdown(point_values)
    max_profit = max(traded_rows, key=lambda row: float(row.total_pnl_usd), default=None)
    max_loss = min(traded_rows, key=lambda row: float(row.total_pnl_usd), default=None)

    if rows:
        period_start_equity = float(rows[0].ending_equity) - float(rows[0].total_pnl_usd)
        equity_values = [period_start_equity] + [float(row.ending_equity) for row in rows]
        ending_equity = rows[-1].ending_equity
    else:
        period_start_equity = 0.0
        equity_values = [period_start_equity]
        ending_equity = format_amount(period_start_equity)

    max_drawdown_usd, max_drawdown_pct = compute_max_drawdown_from_equity(equity_values)

    return AggregateResult(
        period=period,
        days=str(len(rows)),
        held_days=str(sum(1 for row in rows if row.status == "HELD")),
        flat_days=str(sum(1 for row in rows if row.status == "FLAT")),
        skipped_days=str(sum(1 for row in rows if row.status == "SKIPPED")),
        trades=str(sum(int(row.trades) for row in rows)),
        gap_events=str(sum(int(row.gap_events) for row in rows)),
        long_trades=str(sum(int(row.long_trades) for row in rows)),
        short_trades=str(sum(int(row.short_trades) for row in rows)),
        stop_exits=str(sum(int(row.stop_exits) for row in rows)),
        target_exits=str(sum(int(row.target_exits) for row in rows)),
        gap_exits=str(sum(int(row.gap_exits) for row in rows)),
        end_of_data_exits=str(sum(int(row.end_of_data_exits) for row in rows)),
        winning_days=str(sum(1 for value in usd_values if value > 0)),
        losing_days=str(sum(1 for value in usd_values if value < 0)),
        break_even_days=str(sum(1 for value in usd_values if value == 0)),
        total_points=format_amount(total_points),
        average_points=format_amount(total_points / len(traded_rows) if traded_rows else 0.0),
        total_pnl_usd=format_amount(total_pnl_usd),
        average_pnl_usd=format_amount(total_pnl_usd / len(traded_rows) if traded_rows else 0.0),
        ending_equity=ending_equity,
        max_profit_date=max_profit.date if max_profit else "",
        max_profit_points=max_profit.total_points if max_profit else "",
        max_profit_usd=max_profit.total_pnl_usd if max_profit else "",
        max_loss_date=max_loss.date if max_loss else "",
        max_loss_points=max_loss.total_points if max_loss else "",
        max_loss_usd=max_loss.total_pnl_usd if max_loss else "",
        max_consecutive_wins=str(max_wins),
        max_consecutive_losses=str(max_losses),
        max_drawdown_points=format_amount(max_drawdown_points),
        max_drawdown_usd=format_amount(max_drawdown_usd),
        max_drawdown_pct=format_pct(max_drawdown_pct),
    )


def aggregate_by_period(rows: list[DayResult], period_length: int) -> list[AggregateResult]:
    grouped: dict[str, list[DayResult]] = {}
    for row in rows:
        grouped.setdefault(row.date[:period_length], []).append(row)
    return [aggregate_day_results(period, grouped[period]) for period in sorted(grouped)]


def aggregate_table_lines(rows: list[AggregateResult]) -> list[str]:
    lines = [
        "| Period | Days | Held | Flat | Skipped | Trades | Gaps | Targets | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | PnL USD | End Equity | Max DD USD | Max DD % |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"{row.period} | "
            f"{row.days} | "
            f"{row.held_days} | "
            f"{row.flat_days} | "
            f"{row.skipped_days} | "
            f"{row.trades} | "
            f"{row.gap_events} | "
            f"{row.target_exits} | "
            f"{row.stop_exits} | "
            f"{row.gap_exits} | "
            f"{row.end_of_data_exits} | "
            f"{row.winning_days} | "
            f"{row.losing_days} | "
            f"{row.total_points} | "
            f"{row.total_pnl_usd} | "
            f"{row.ending_equity} | "
            f"{row.max_drawdown_usd} | "
            f"{row.max_drawdown_pct} |"
        )
    return lines


def build_timeframe_summary_markdown(
    output_path: Path,
    run: TimeframeRun,
    daywise_results: list[DayResult],
    monthly_results: list[AggregateResult],
    yearly_results: list[AggregateResult],
    overall: AggregateResult,
    overall_trade_summary: dict[str, Any],
    output_files: list[Path],
    repo_root: Path,
) -> None:
    lines: list[str] = [
        f"# BTC {run.spec.timeframe} MA{run.spec.ma_period} {reward_label(run.target_risk_reward)} Target + Trailing MA Stop Backtest",
        "",
        "## Strategy Details",
        "",
        f"- Dataset: `{display_path(run.input_file, repo_root)}`",
        f"- Tested UTC date range: `{daywise_results[0].date if daywise_results else 'N/A'}` through `{daywise_results[-1].date if daywise_results else 'N/A'}`",
        f"- Signal source: BTC-USD {run.spec.timeframe} close",
        f"- Initial activation: `{run.activation_timestamp}` (one-time UTC activation threshold)",
        f"- Entry rule: close above SMA -> long, close below SMA -> short, and entry requires close within `{MAX_ENTRY_GAP_PCT:g}%` of the SMA.",
        f"- Target rule: fixed `{reward_label(run.target_risk_reward)}` target from the entry-to-initial-MA-stop distance.",
        "- Stop rule: the active stop uses the carried-forward moving average and trails with each completed candle if no exit occurs.",
        f"- Ambiguous same-candle stop/target handling: `{AMBIGUOUS_POLICY}`.",
        "- Post-target rule: same-candle reversal is allowed if the signal flips across the MA and the entry gap filter passes; same-direction same-candle re-entry is blocked.",
        "- Gap rule: force flat at the last known boundary before a gap, then resume on the first post-gap candle and allow a new entry only after that candle completes.",
        f"- Accounting: fixed `${format_amount(run.capital)}` notional per trade, no costs, no compounding position sizing, and points/USD metrics reported together.",
        "",
        "## Data Notes",
        "",
        f"- First CSV row: `{run.first_csv_timestamp}`",
        f"- First MA-usable row: `{run.first_ma_timestamp}`",
        f"- Source rows loaded: `{run.total_source_rows}`",
        f"- Rows inside requested date filter: `{run.filtered_rows}`",
        f"- Rows processed after activation: `{run.processed_rows}`",
        f"- Gap events detected in this run: `{len(run.gap_events)}`",
        "",
        "## Overall Results",
        "",
        *aggregate_table_lines([overall]),
        "",
        f"- Total trades: `{overall_trade_summary['trades']}`",
        f"- Target exits: `{overall_trade_summary['target_exits']}`",
        f"- Stop exits: `{overall_trade_summary['stop_exits']}`",
        f"- Gap exits: `{overall_trade_summary['gap_exits']}`",
        f"- Win rate: `{format_pct(overall_trade_summary['win_rate_pct'])}%`",
        f"- Starting capital: `${format_amount(run.capital)}`",
        f"- Ending equity: `${format_amount(overall_trade_summary['ending_equity'])}`",
        f"- Gross PnL USD: `${format_amount(overall_trade_summary['gross_pnl_usd'])}`",
        f"- Total return: `{format_pct(overall_trade_summary['total_return_pct'])}%`",
        f"- Max drawdown: `${format_amount(overall_trade_summary['max_drawdown_usd'])}` (`{format_pct(overall_trade_summary['max_drawdown_pct'])}%`)",
        "",
        "## Yearly Results",
        "",
        *aggregate_table_lines(yearly_results),
        "",
        "## Monthly Results",
        "",
        *aggregate_table_lines(monthly_results),
        "",
        "## Gap Events / Exceptions",
        "",
    ]

    if run.gap_events:
        for gap_event in run.gap_events:
            lines.append(
                f"- `{gap_event.gap_start_timestamp}` -> `{gap_event.gap_resume_timestamp}`: "
                f"`{gap_event.missing_candles}` missing candles; active trade = `{gap_event.had_active_trade}`. "
                f"{gap_event.remarks}"
            )
    else:
        lines.append("- None")

    lines.extend(["", "## Output Files", ""])
    for path in output_files:
        lines.append(f"- `{display_path(path, repo_root)}`")

    lines.extend(
        [
            "",
            "## Remarks",
            "",
            "- The one-time activation threshold is applied only on the first candidate UTC date.",
            "- The entry candle itself cannot exit a newly opened position.",
            "- Daywise results are grouped by realized exit date in UTC; held-only dates are preserved separately.",
            "- Monthly and yearly drawdowns are period-local from day-ending equity; overall drawdown is full-run.",
        ]
    )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_timeframe_outputs(
    run: TimeframeRun,
    repo_root: Path,
) -> dict[str, Any]:
    daywise_results = build_daywise_results(run)
    monthly_results = aggregate_by_period(daywise_results, 7)
    yearly_results = aggregate_by_period(daywise_results, 4)
    overall = aggregate_day_results("Overall", daywise_results)
    overall_trade_summary = summarize_trades(run.trade_results, run.capital)
    equity_curve_rows = build_equity_curve_rows(run.trade_results, run.capital)

    trades_path = run.output_dir / "trades.csv"
    gaps_path = run.output_dir / "gap_events.csv"
    daywise_path = run.output_dir / "daywise_summary.csv"
    monthly_path = run.output_dir / "monthly_summary.csv"
    yearly_path = run.output_dir / "yearly_summary.csv"
    equity_curve_path = run.output_dir / "equity_curve.csv"
    summary_json_path = run.output_dir / "summary.json"
    summary_md_path = run.output_dir / "summary.md"
    log_path = run.output_dir / LOG_FILENAME

    write_csv(
        trades_path,
        [asdict(result) for result in run.trade_results],
        [
            "trade_id",
            "report_date",
            "entry_date",
            "exit_date",
            "signal_timestamp",
            "entry_timestamp",
            "direction",
            "entry_price_points",
            "entry_ma",
            "initial_stop_points",
            "initial_risk_points",
            "target_price_points",
            "entry_gap_pct",
            "exit_candle_timestamp",
            "exit_timestamp",
            "exit_price_points",
            "exit_reason",
            "exit_ma",
            "points_pnl",
            "quantity_btc",
            "entry_notional_usd",
            "exit_notional_usd",
            "gross_pnl_usd",
            "trade_return_pct",
            "cumulative_pnl_usd",
            "equity_after_trade",
            "holding_days",
            "remarks",
        ],
    )
    write_csv(
        gaps_path,
        [asdict(event) for event in run.gap_events],
        [
            "event_id",
            "report_date",
            "gap_start_timestamp",
            "gap_resume_timestamp",
            "missing_candles",
            "had_active_trade",
            "forced_exit_trade_id",
            "pre_gap_close_points",
            "pre_gap_ma",
            "remarks",
        ],
    )
    write_csv(
        daywise_path,
        [asdict(result) for result in daywise_results],
        [
            "date",
            "status",
            "trades",
            "gap_events",
            "long_trades",
            "short_trades",
            "stop_exits",
            "target_exits",
            "gap_exits",
            "end_of_data_exits",
            "winning_trades",
            "losing_trades",
            "break_even_trades",
            "total_points",
            "average_points",
            "max_profit_points",
            "max_loss_points",
            "total_pnl_usd",
            "average_pnl_usd",
            "max_profit_usd",
            "max_loss_usd",
            "ending_equity",
            "max_consecutive_wins",
            "max_consecutive_losses",
            "max_drawdown_points",
            "max_drawdown_usd",
            "max_drawdown_pct",
            "remarks",
        ],
    )
    write_csv(
        monthly_path,
        [asdict(result) for result in monthly_results],
        [
            "period",
            "days",
            "held_days",
            "flat_days",
            "skipped_days",
            "trades",
            "gap_events",
            "long_trades",
            "short_trades",
            "stop_exits",
            "target_exits",
            "gap_exits",
            "end_of_data_exits",
            "winning_days",
            "losing_days",
            "break_even_days",
            "total_points",
            "average_points",
            "total_pnl_usd",
            "average_pnl_usd",
            "ending_equity",
            "max_profit_date",
            "max_profit_points",
            "max_profit_usd",
            "max_loss_date",
            "max_loss_points",
            "max_loss_usd",
            "max_consecutive_wins",
            "max_consecutive_losses",
            "max_drawdown_points",
            "max_drawdown_usd",
            "max_drawdown_pct",
        ],
    )
    write_csv(
        yearly_path,
        [asdict(result) for result in yearly_results],
        [
            "period",
            "days",
            "held_days",
            "flat_days",
            "skipped_days",
            "trades",
            "gap_events",
            "long_trades",
            "short_trades",
            "stop_exits",
            "target_exits",
            "gap_exits",
            "end_of_data_exits",
            "winning_days",
            "losing_days",
            "break_even_days",
            "total_points",
            "average_points",
            "total_pnl_usd",
            "average_pnl_usd",
            "ending_equity",
            "max_profit_date",
            "max_profit_points",
            "max_profit_usd",
            "max_loss_date",
            "max_loss_points",
            "max_loss_usd",
            "max_consecutive_wins",
            "max_consecutive_losses",
            "max_drawdown_points",
            "max_drawdown_usd",
            "max_drawdown_pct",
        ],
    )
    write_csv(
        equity_curve_path,
        [asdict(result) for result in equity_curve_rows],
        [
            "trade_id",
            "report_date",
            "exit_timestamp",
            "direction",
            "gross_pnl_usd",
            "cumulative_pnl_usd",
            "equity",
            "peak_equity",
            "drawdown_usd",
            "drawdown_pct",
        ],
    )

    output_files = [
        trades_path,
        gaps_path,
        daywise_path,
        monthly_path,
        yearly_path,
        equity_curve_path,
        summary_json_path,
        summary_md_path,
        log_path,
    ]

    summary_payload = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "strategy": build_strategy_name(run.target_risk_reward),
        "timeframe": run.spec.timeframe,
        "ma_period": run.spec.ma_period,
        "expected_candle_interval": run.spec.timeframe,
        "source_dataset": display_path(run.input_file, repo_root),
        "tested_utc_date_range": {
            "start": daywise_results[0].date if daywise_results else "",
            "end": daywise_results[-1].date if daywise_results else "",
        },
        "starting_capital": run.capital,
        "capital_mode": CAPITAL_MODE,
        "fixed_trade_notional_usd": run.capital,
        "cost_model": COST_MODEL,
        "short_mode": SHORT_MODE,
        "target_risk_reward": run.target_risk_reward,
        "max_entry_gap_pct": MAX_ENTRY_GAP_PCT,
        "ambiguous_policy": AMBIGUOUS_POLICY,
        "entry_rule": ENTRY_RULE,
        "target_rule": build_target_rule(run.target_risk_reward),
        "post_target_reentry_rule": POST_TARGET_REENTRY_RULE,
        "first_csv_timestamp": run.first_csv_timestamp,
        "first_ma_usable_timestamp": run.first_ma_timestamp,
        "activation_timestamp": run.activation_timestamp,
        "data_notes": {
            "total_source_rows": run.total_source_rows,
            "filtered_rows": run.filtered_rows,
            "processed_rows": run.processed_rows,
            "candidate_days": len(run.candidate_days),
        },
        "overall_trade_summary": {
            **overall_trade_summary,
            "max_profit": asdict(overall_trade_summary["max_profit"])
            if overall_trade_summary["max_profit"]
            else None,
            "max_loss": asdict(overall_trade_summary["max_loss"])
            if overall_trade_summary["max_loss"]
            else None,
        },
        "overall_day_summary": asdict(overall),
        "gap_summary": {
            "total_gap_events": len(run.gap_events),
            "total_missing_candles": sum(int(event.missing_candles) for event in run.gap_events),
            "gaps": [asdict(event) for event in run.gap_events],
        },
        "yearly_results": [asdict(result) for result in yearly_results],
        "monthly_results": [asdict(result) for result in monthly_results],
        "daywise_results": [asdict(result) for result in daywise_results],
        "equity_curve_file": display_path(equity_curve_path, repo_root),
        "output_files": [display_path(path, repo_root) for path in output_files],
    }
    summary_json_path.write_text(json.dumps(json_ready(summary_payload), indent=2), encoding="utf-8")
    build_timeframe_summary_markdown(
        summary_md_path,
        run,
        daywise_results,
        monthly_results,
        yearly_results,
        overall,
        overall_trade_summary,
        output_files,
        repo_root,
    )

    summary_row = {
        "timeframe": run.spec.timeframe,
        "ma_period": str(run.spec.ma_period),
        "target_risk_reward": format_reward_value(run.target_risk_reward),
        "target_label": reward_label(run.target_risk_reward),
        "input_file": display_path(run.input_file, repo_root),
        "tested_start_date": daywise_results[0].date if daywise_results else "",
        "tested_end_date": daywise_results[-1].date if daywise_results else "",
        "first_csv_timestamp": run.first_csv_timestamp,
        "first_ma_usable_timestamp": run.first_ma_timestamp,
        "activation_timestamp": run.activation_timestamp,
        "gap_events": str(len(run.gap_events)),
        "missing_candles_total": str(sum(int(event.missing_candles) for event in run.gap_events)),
        "total_trades": str(overall_trade_summary["trades"]),
        "long_trades": str(overall_trade_summary["long_trades"]),
        "short_trades": str(overall_trade_summary["short_trades"]),
        "target_exits": str(overall_trade_summary["target_exits"]),
        "stop_exits": str(overall_trade_summary["stop_exits"]),
        "gap_exits": str(overall_trade_summary["gap_exits"]),
        "winning_trades": str(overall_trade_summary["winning_trades"]),
        "losing_trades": str(overall_trade_summary["losing_trades"]),
        "win_rate_pct": format_pct(overall_trade_summary["win_rate_pct"]),
        "total_points": format_amount(overall_trade_summary["total_points"]),
        "average_points": format_amount(overall_trade_summary["average_points"]),
        "max_drawdown_points": format_amount(overall_trade_summary["max_drawdown_points"]),
        "starting_capital": format_amount(run.capital),
        "fixed_trade_notional_usd": format_amount(run.capital),
        "gross_pnl_usd": format_amount(overall_trade_summary["gross_pnl_usd"]),
        "average_pnl_usd": format_amount(overall_trade_summary["average_pnl_usd"]),
        "ending_equity": format_amount(overall_trade_summary["ending_equity"]),
        "total_return_pct": format_pct(overall_trade_summary["total_return_pct"]),
        "max_drawdown_usd": format_amount(overall_trade_summary["max_drawdown_usd"]),
        "max_drawdown_pct": format_pct(overall_trade_summary["max_drawdown_pct"]),
    }

    return {
        "run": run,
        "target_risk_reward": run.target_risk_reward,
        "summary_row": summary_row,
        "summary_payload": summary_payload,
        "output_files": output_files,
    }


def build_timeframe_table_lines(rows: list[dict[str, str]]) -> list[str]:
    lines = [
        "| Timeframe | MA | Target | Date Range | Gaps | Trades | Targets | Stops | Gap Exits | Win Rate % | Total Points | Gross PnL USD | Ending Equity | Max DD USD | Max DD % |",
        "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"{row['timeframe']} | "
            f"{row['ma_period']} | "
            f"{row['target_label']} | "
            f"{row['tested_start_date']} -> {row['tested_end_date']} | "
            f"{row['gap_events']} | "
            f"{row['total_trades']} | "
            f"{row['target_exits']} | "
            f"{row['stop_exits']} | "
            f"{row['gap_exits']} | "
            f"{row['win_rate_pct']} | "
            f"{row['total_points']} | "
            f"{row['gross_pnl_usd']} | "
            f"{row['ending_equity']} | "
            f"{row['max_drawdown_usd']} | "
            f"{row['max_drawdown_pct']} |"
        )
    return lines


def write_top_level_summary_markdown(
    output_path: Path,
    timeframe_rows: list[dict[str, str]],
    timeframe_artifacts: list[dict[str, Any]],
    output_files: list[Path],
    repo_root: Path,
    capital: float,
    target_levels: tuple[float, ...],
) -> None:
    lines: list[str] = [
        "# BTC Local Multi-Timeframe Multi-Reward Target + Trailing MA Stop Capital Backtest",
        "",
        "## Strategy Details",
        "",
        "- Results are written under `btc/results`.",
        "- Tested mappings:",
        "  - `15m` with `MA 96`",
        "  - `30m` with `MA 48`",
        "  - `1h` with `MA 24`",
        f"- Target levels tested: `{', '.join(reward_label(level) for level in target_levels)}`.",
        f"- Fixed trade notional: `${format_amount(capital)}` per trade across all timeframes.",
        "- Each trade uses a fixed target based on the selected reward multiple and trails the MA stop until exit.",
        f"- Entry requires price to be within `{MAX_ENTRY_GAP_PCT:g}%` of the moving average.",
        f"- Same-candle stop/target ambiguity uses `{AMBIGUOUS_POLICY}`.",
        "- Same-candle reversal after target is allowed only if the signal flips and the gap filter passes.",
        "- No brokerage, slippage, borrow cost, or compounding position sizing is modeled.",
        "",
        "## Timeframe Comparison",
        "",
        *build_timeframe_table_lines(timeframe_rows),
        "",
        "## Per-Timeframe Output Folders",
        "",
    ]

    for artifact in timeframe_artifacts:
        run: TimeframeRun = artifact["run"]
        summary_row = artifact["summary_row"]
        lines.append(
            f"- `{run.spec.timeframe} {summary_row['target_label']}`: `{display_path(run.output_dir, repo_root)}` "
            f"(MA {run.spec.ma_period}, gaps {len(run.gap_events)})"
        )

    lines.extend(["", "## Output Files", ""])
    for path in output_files:
        lines.append(f"- `{display_path(path, repo_root)}`")

    lines.extend(
        [
            "",
            "## Remarks",
            "",
            "- All timestamps and grouping are UTC.",
            "- Gap handling is consistent across all selected timeframes: flat gaps log an event; live gaps force an exit at the last known boundary before the gap.",
        ]
    )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    results_root = args.results_dir
    run_name = args.run_name.strip() or (
        "btc_ma_target_trailing_multi_timeframe_capital_multi_reward_"
        f"{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    output_dir = results_root / run_name
    output_dir.mkdir(parents=True, exist_ok=True)

    selected_specs = [
        TIMEFRAME_SPECS[name]
        for name in TIMEFRAME_ORDER
        if name in dict.fromkeys(args.timeframes)
    ]

    timeframe_artifacts: list[dict[str, Any]] = []
    for spec in selected_specs:
        input_file = args.data_dir / spec.filename
        for target_risk_reward in args.target_levels:
            timeframe_output_dir = output_dir / (
                f"{spec.subdir_name}_rr{reward_slug(target_risk_reward)}"
            )
            timeframe_output_dir.mkdir(parents=True, exist_ok=True)
            run = run_backtest(
                spec=spec,
                input_file=input_file,
                output_dir=timeframe_output_dir,
                initial_start_time=args.initial_start_time,
                start_date=args.start_date,
                end_date=args.end_date,
                capital=args.capital,
                target_risk_reward=target_risk_reward,
            )
            timeframe_artifacts.append(write_timeframe_outputs(run, repo_root))

    timeframe_summary_path = output_dir / "timeframe_summary.csv"
    timeframe_target_summary_path = output_dir / "timeframe_target_summary.csv"
    summary_json_path = output_dir / "summary.json"
    summary_md_path = output_dir / "summary.md"
    run_config_path = output_dir / "run_config.json"

    timeframe_rows = [artifact["summary_row"] for artifact in timeframe_artifacts]
    write_csv(
        timeframe_summary_path,
        timeframe_rows,
        [
            "timeframe",
            "ma_period",
            "target_risk_reward",
            "target_label",
            "input_file",
            "tested_start_date",
            "tested_end_date",
            "first_csv_timestamp",
            "first_ma_usable_timestamp",
            "activation_timestamp",
            "gap_events",
            "missing_candles_total",
            "total_trades",
            "long_trades",
            "short_trades",
            "target_exits",
            "stop_exits",
            "gap_exits",
            "winning_trades",
            "losing_trades",
            "win_rate_pct",
            "total_points",
            "average_points",
            "max_drawdown_points",
            "starting_capital",
            "fixed_trade_notional_usd",
            "gross_pnl_usd",
            "average_pnl_usd",
            "ending_equity",
            "total_return_pct",
            "max_drawdown_usd",
            "max_drawdown_pct",
        ],
    )
    write_csv(
        timeframe_target_summary_path,
        timeframe_rows,
        [
            "timeframe",
            "ma_period",
            "target_risk_reward",
            "target_label",
            "input_file",
            "tested_start_date",
            "tested_end_date",
            "first_csv_timestamp",
            "first_ma_usable_timestamp",
            "activation_timestamp",
            "gap_events",
            "missing_candles_total",
            "total_trades",
            "long_trades",
            "short_trades",
            "target_exits",
            "stop_exits",
            "gap_exits",
            "winning_trades",
            "losing_trades",
            "win_rate_pct",
            "total_points",
            "average_points",
            "max_drawdown_points",
            "starting_capital",
            "fixed_trade_notional_usd",
            "gross_pnl_usd",
            "average_pnl_usd",
            "ending_equity",
            "total_return_pct",
            "max_drawdown_usd",
            "max_drawdown_pct",
        ],
    )

    top_level_output_files = [
        timeframe_summary_path,
        timeframe_target_summary_path,
        summary_json_path,
        summary_md_path,
        run_config_path,
    ]

    top_level_summary = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "strategy": build_multi_reward_strategy_name(args.target_levels),
        "results_root": display_path(output_dir, repo_root),
        "starting_capital": args.capital,
        "capital_mode": CAPITAL_MODE,
        "fixed_trade_notional_usd": args.capital,
        "cost_model": COST_MODEL,
        "short_mode": SHORT_MODE,
        "target_levels": list(args.target_levels),
        "max_entry_gap_pct": MAX_ENTRY_GAP_PCT,
        "ambiguous_policy": AMBIGUOUS_POLICY,
        "entry_rule": ENTRY_RULE,
        "target_rule_template": "fixed_rr_from_entry_to_initial_ma_stop_with_trailing_ma_stop",
        "post_target_reentry_rule": POST_TARGET_REENTRY_RULE,
        "selected_timeframes": [spec.timeframe for spec in selected_specs],
        "mappings": {
            spec.timeframe: {
                "input_file": display_path(args.data_dir / spec.filename, repo_root),
                "ma_period": spec.ma_period,
                "step_minutes": spec.step_minutes,
            }
            for spec in selected_specs
        },
        "legacy_common_strategies_outputs_used": False,
        "timeframe_summary": timeframe_rows,
        "timeframe_target_summary": timeframe_rows,
        "timeframe_target_runs": {
            f"{artifact['run'].spec.timeframe}_rr{reward_slug(artifact['target_risk_reward'])}": {
                "output_dir": display_path(artifact["run"].output_dir, repo_root),
                "summary": artifact["summary_payload"],
            }
            for artifact in timeframe_artifacts
        },
        "output_files": [display_path(path, repo_root) for path in top_level_output_files],
    }
    summary_json_path.write_text(json.dumps(json_ready(top_level_summary), indent=2), encoding="utf-8")

    run_config_payload = {
        "args": {
            "data_dir": str(args.data_dir),
            "results_dir": str(args.results_dir),
            "run_name": run_name,
            "initial_start_time": args.initial_start_time,
            "start_date": args.start_date,
            "end_date": args.end_date,
            "timeframes": list(args.timeframes),
            "target_levels": list(args.target_levels),
            "capital": args.capital,
        },
        "resolved_paths": {
            "repo_root": str(repo_root.resolve()),
            "data_dir": str(args.data_dir.resolve()),
            "results_root": str(results_root.resolve()),
            "output_dir": str(output_dir.resolve()),
        },
        "timezone": "UTC",
        "capital_mode": CAPITAL_MODE,
        "cost_model": COST_MODEL,
        "short_mode": SHORT_MODE,
        "target_levels": list(args.target_levels),
        "max_entry_gap_pct": MAX_ENTRY_GAP_PCT,
        "ambiguous_policy": AMBIGUOUS_POLICY,
        "entry_rule": ENTRY_RULE,
        "target_rule_template": "fixed_rr_from_entry_to_initial_ma_stop_with_trailing_ma_stop",
        "post_target_reentry_rule": POST_TARGET_REENTRY_RULE,
        "gap_policy": "force_exit_before_gap_and_resume_after_first_post_gap_candle",
        "selected_timeframes": [spec.timeframe for spec in selected_specs],
        "timeframe_configuration": {
            spec.timeframe: {
                "input_file": display_path(args.data_dir / spec.filename, repo_root),
                "ma_period": spec.ma_period,
                "step_minutes": spec.step_minutes,
            }
            for spec in selected_specs
        },
        "per_timeframe_target_metadata": {
            f"{artifact['run'].spec.timeframe}_rr{reward_slug(artifact['target_risk_reward'])}": {
                "target_risk_reward": artifact["target_risk_reward"],
                "first_csv_timestamp": artifact["run"].first_csv_timestamp,
                "first_ma_usable_timestamp": artifact["run"].first_ma_timestamp,
                "activation_timestamp": artifact["run"].activation_timestamp,
                "total_source_rows": artifact["run"].total_source_rows,
                "filtered_rows": artifact["run"].filtered_rows,
                "processed_rows": artifact["run"].processed_rows,
                "detected_gaps": [asdict(event) for event in artifact["run"].gap_events],
            }
            for artifact in timeframe_artifacts
        },
    }
    run_config_path.write_text(json.dumps(json_ready(run_config_payload), indent=2), encoding="utf-8")

    write_top_level_summary_markdown(
        summary_md_path,
        timeframe_rows,
        timeframe_artifacts,
        top_level_output_files,
        repo_root,
        args.capital,
        args.target_levels,
    )

    print(f"Results written to: {output_dir}")
    for row in timeframe_rows:
        print(
            f"{row['timeframe']} {row['target_label']}: MA{row['ma_period']}, trades={row['total_trades']}, "
            f"targets={row['target_exits']}, stops={row['stop_exits']}, "
            f"gross_pnl_usd={row['gross_pnl_usd']}, ending_equity={row['ending_equity']}"
        )


if __name__ == "__main__":
    main()
