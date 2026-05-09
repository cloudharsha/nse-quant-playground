#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


LOG_FILENAME = "backtest.log"
TIMEFRAME_ORDER = ("15m", "30m", "1h")


@dataclass(frozen=True)
class TimeframeSpec:
    timeframe: str
    filename: str
    ma_period: int
    step_minutes: int

    @property
    def step_delta(self) -> dt.timedelta:
        return dt.timedelta(minutes=self.step_minutes)

    @property
    def subdir_name(self) -> str:
        return f"{self.timeframe}_ma{self.ma_period}"


TIMEFRAME_SPECS = {
    "15m": TimeframeSpec("15m", "BTCUSD_data_15m.csv", 96, 15),
    "30m": TimeframeSpec("30m", "BTCUSD_data_30m.csv", 48, 30),
    "1h": TimeframeSpec("1h", "BTCUSD_data_1h.csv", 24, 60),
}


@dataclass
class PriceRow:
    timestamp: str
    dt: dt.datetime
    date: str
    open_value: float
    high_value: float
    low_value: float
    close_value: float
    volume_value: float
    ma_value: float | None


@dataclass
class ActiveTrade:
    trade_id: str
    entry_date: str
    signal_timestamp: str
    entry_timestamp: str
    direction: str
    entry_price: float
    entry_price_text: str
    entry_ma: float
    stop_ma: float
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
    exit_candle_timestamp: str
    exit_timestamp: str
    exit_price_points: str
    exit_reason: str
    exit_ma: str
    points_pnl: str
    holding_days: str
    remarks: str


@dataclass
class GapEvent:
    event_id: str
    report_date: str
    gap_start_timestamp: str
    gap_resume_timestamp: str
    missing_candles: str
    had_active_trade: str
    forced_exit_trade_id: str
    pre_gap_close_points: str
    pre_gap_ma: str
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
    gap_exits: str
    end_of_data_exits: str
    winning_trades: str
    losing_trades: str
    break_even_trades: str
    total_points: str
    average_points: str
    max_profit_points: str
    max_loss_points: str
    max_consecutive_wins: str
    max_consecutive_losses: str
    max_drawdown_points: str
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
    gap_exits: str
    end_of_data_exits: str
    winning_days: str
    losing_days: str
    break_even_days: str
    total_points: str
    average_points: str
    max_profit_date: str
    max_profit_points: str
    max_loss_date: str
    max_loss_points: str
    max_consecutive_wins: str
    max_consecutive_losses: str
    max_drawdown_points: str


@dataclass
class TimeframeRun:
    spec: TimeframeSpec
    input_file: Path
    output_dir: Path
    trade_results: list[TradeResult]
    gap_events: list[GapEvent]
    candidate_days: list[str]
    held_days: set[str]
    first_csv_timestamp: str
    first_ma_timestamp: str
    activation_timestamp: str
    total_source_rows: int
    filtered_rows: int
    processed_rows: int


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(
        description="BTC local multi-timeframe continuous trailing-MA backtest."
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
    args = parser.parse_args()

    validate_optional_date(parser, args.start_date, "--start-date")
    validate_optional_date(parser, args.end_date, "--end-date")
    validate_time(parser, args.initial_start_time, "--initial-start-time")
    if args.start_date and args.end_date and args.start_date > args.end_date:
        parser.error("--start-date must be <= --end-date")
    minute = int(args.initial_start_time.split(":")[1])
    if minute not in (0, 15, 30, 45):
        parser.error("--initial-start-time minutes must be one of 00, 15, 30, 45")
    return args


def validate_optional_date(parser: argparse.ArgumentParser, value: str, name: str) -> None:
    if not value:
        return
    try:
        dt.date.fromisoformat(value)
    except ValueError:
        parser.error(f"{name} must be YYYY-MM-DD")


def validate_time(parser: argparse.ArgumentParser, value: str, name: str) -> None:
    parts = value.split(":")
    if len(parts) != 2 or not all(part.isdigit() for part in parts):
        parser.error(f"{name} must be HH:MM")
    hour, minute = (int(part) for part in parts)
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        parser.error(f"{name} must be HH:MM")


def parse_timestamp(value: str) -> dt.datetime:
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"Invalid timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"Timestamp must be timezone-aware: {value!r}")
    return parsed.astimezone(dt.timezone.utc)


def format_timestamp(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).isoformat(sep=" ", timespec="seconds")


def format_number(value: float) -> str:
    return f"{value:.2f}"


def holding_days(entry_date: str, exit_date: str) -> str:
    start_date = dt.date.fromisoformat(entry_date)
    end_date = dt.date.fromisoformat(exit_date)
    return str((end_date - start_date).days)


def date_strings_between(start_date: str, end_date: str) -> list[str]:
    start = dt.date.fromisoformat(start_date)
    end = dt.date.fromisoformat(end_date)
    day_count = (end - start).days
    return [(start + dt.timedelta(days=offset)).isoformat() for offset in range(day_count + 1)]


def display_path(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def configure_logger(log_path: Path, logger_name: str) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def load_price_rows(input_file: Path, ma_period: int) -> list[PriceRow]:
    required_columns = {"Date", "Open", "High", "Low", "Close", "Volume"}
    raw_rows: list[dict[str, Any]] = []

    with input_file.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing_columns = sorted(required_columns - fieldnames)
        if missing_columns:
            raise ValueError(f"{input_file} is missing columns: {', '.join(missing_columns)}")

        for row in reader:
            timestamp = (row.get("Date") or "").strip()
            if not timestamp:
                continue
            candle_dt = parse_timestamp(timestamp)
            raw_rows.append(
                {
                    "dt": candle_dt,
                    "timestamp": format_timestamp(candle_dt),
                    "date": candle_dt.date().isoformat(),
                    "open_value": float(row["Open"]),
                    "high_value": float(row["High"]),
                    "low_value": float(row["Low"]),
                    "close_value": float(row["Close"]),
                    "volume_value": float(row["Volume"]),
                }
            )

    if not raw_rows:
        raise ValueError(f"No rows found in {input_file}")

    raw_rows.sort(key=lambda item: item["dt"])
    for current, previous in zip(raw_rows[1:], raw_rows[:-1]):
        if current["dt"] == previous["dt"]:
            raise ValueError(f"Duplicate timestamp detected: {current['timestamp']}")

    closes: list[float] = []
    rolling_sum = 0.0
    rows: list[PriceRow] = []
    for raw_row in raw_rows:
        close_value = raw_row["close_value"]
        closes.append(close_value)
        rolling_sum += close_value
        if len(closes) > ma_period:
            rolling_sum -= closes[-ma_period - 1]
        ma_value = None
        if len(closes) >= ma_period:
            ma_value = rolling_sum / ma_period
        rows.append(
            PriceRow(
                timestamp=raw_row["timestamp"],
                dt=raw_row["dt"],
                date=raw_row["date"],
                open_value=raw_row["open_value"],
                high_value=raw_row["high_value"],
                low_value=raw_row["low_value"],
                close_value=close_value,
                volume_value=raw_row["volume_value"],
                ma_value=ma_value,
            )
        )

    return rows


def filter_price_rows(rows: list[PriceRow], start_date: str, end_date: str) -> list[PriceRow]:
    filtered = rows
    if start_date:
        filtered = [row for row in filtered if row.date >= start_date]
    if end_date:
        filtered = [row for row in filtered if row.date <= end_date]
    return filtered


def parse_start_time(value: str) -> tuple[int, int]:
    hour_text, minute_text = value.split(":")
    return int(hour_text), int(minute_text)


def compute_activation_row(rows: list[PriceRow], initial_start_time: str) -> PriceRow:
    start_hour, start_minute = parse_start_time(initial_start_time)
    first_date = rows[0].date
    for row in rows:
        if row.date != first_date:
            break
        if (row.dt.hour, row.dt.minute) >= (start_hour, start_minute):
            return row
    raise ValueError(
        f"No row exists on first candidate date {first_date} at or after {initial_start_time} UTC"
    )


def make_trade_id(number: int) -> str:
    return f"T{number:05d}"


def make_gap_id(number: int) -> str:
    return f"G{number:04d}"


def missing_candle_count(
    previous_row: PriceRow,
    current_row: PriceRow,
    step_minutes: int,
) -> int:
    delta_minutes = int((current_row.dt - previous_row.dt).total_seconds() // 60)
    if delta_minutes <= step_minutes:
        return 0
    return (delta_minutes // step_minutes) - 1


def evaluate_entry(row: PriceRow, boundary_dt: dt.datetime, trade_id: str) -> ActiveTrade | None:
    if row.ma_value is None:
        return None
    if row.close_value > row.ma_value:
        direction = "LONG"
    elif row.close_value < row.ma_value:
        direction = "SHORT"
    else:
        return None

    return ActiveTrade(
        trade_id=trade_id,
        entry_date=boundary_dt.date().isoformat(),
        signal_timestamp=row.timestamp,
        entry_timestamp=format_timestamp(boundary_dt),
        direction=direction,
        entry_price=row.close_value,
        entry_price_text=format_number(row.close_value),
        entry_ma=row.ma_value,
        stop_ma=row.ma_value,
        entry_dt=boundary_dt,
    )


def candle_stop_hit(active_trade: ActiveTrade, row: PriceRow) -> bool:
    if active_trade.direction == "LONG":
        return row.low_value <= active_trade.stop_ma
    return row.high_value >= active_trade.stop_ma


def build_trade_result(
    active_trade: ActiveTrade,
    exit_candle_timestamp: str,
    exit_timestamp: str,
    exit_price: float,
    exit_reason: str,
    exit_ma: float,
    remarks: str = "",
) -> TradeResult:
    exit_date = exit_timestamp[:10]
    if active_trade.direction == "LONG":
        points_pnl = exit_price - active_trade.entry_price
    else:
        points_pnl = active_trade.entry_price - exit_price

    return TradeResult(
        trade_id=active_trade.trade_id,
        report_date=exit_date,
        entry_date=active_trade.entry_date,
        exit_date=exit_date,
        signal_timestamp=active_trade.signal_timestamp,
        entry_timestamp=active_trade.entry_timestamp,
        direction=active_trade.direction,
        entry_price_points=active_trade.entry_price_text,
        entry_ma=format_number(active_trade.entry_ma),
        exit_candle_timestamp=exit_candle_timestamp,
        exit_timestamp=exit_timestamp,
        exit_price_points=format_number(exit_price),
        exit_reason=exit_reason,
        exit_ma=format_number(exit_ma),
        points_pnl=format_number(points_pnl),
        holding_days=holding_days(active_trade.entry_date, exit_date),
        remarks=remarks,
    )


def extend_held_days(held_days: set[str], active_trade: ActiveTrade, exit_timestamp: str) -> None:
    exit_date = exit_timestamp[:10]
    held_days.update(date_strings_between(active_trade.entry_date, exit_date))


def run_backtest(
    spec: TimeframeSpec,
    input_file: Path,
    output_dir: Path,
    initial_start_time: str,
    start_date: str,
    end_date: str,
) -> TimeframeRun:
    logger = configure_logger(
        output_dir / LOG_FILENAME,
        f"btc_ma_continuous_multi_timeframe_{spec.timeframe}",
    )
    rows = load_price_rows(input_file, spec.ma_period)
    candidate_rows = filter_price_rows(rows, start_date, end_date)
    if not candidate_rows:
        raise SystemExit(f"{spec.timeframe}: no rows remain after applying the date filters.")

    first_ma_row = next((row for row in rows if row.ma_value is not None), None)
    if first_ma_row is None:
        raise SystemExit(
            f"{spec.timeframe}: the BTC dataset does not contain enough rows to compute MA {spec.ma_period}."
        )

    activation_row = compute_activation_row(candidate_rows, initial_start_time)
    activation_timestamp = activation_row.timestamp
    active_rows = [row for row in candidate_rows if row.dt >= activation_row.dt]
    if not active_rows:
        raise SystemExit(f"{spec.timeframe}: no rows remain after the activation threshold.")

    candidate_days = date_strings_between(candidate_rows[0].date, candidate_rows[-1].date)
    trade_results: list[TradeResult] = []
    gap_events: list[GapEvent] = []
    held_days: set[str] = set()
    active_trade: ActiveTrade | None = None
    prev_row: PriceRow | None = None
    last_processed_row: PriceRow | None = None
    trade_counter = 1
    gap_counter = 1

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
        if prev_row is not None:
            missing_candles = missing_candle_count(prev_row, row, spec.step_minutes)
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
                    gap_exit = build_trade_result(
                        active_trade=active_trade,
                        exit_candle_timestamp=prev_row.timestamp,
                        exit_timestamp=format_timestamp(gap_boundary_dt),
                        exit_price=prev_row.close_value,
                        exit_reason="gap_exit_missing_candles",
                        exit_ma=active_trade.stop_ma,
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

                gap_event = GapEvent(
                    event_id=make_gap_id(gap_counter),
                    report_date=report_date,
                    gap_start_timestamp=prev_row.timestamp,
                    gap_resume_timestamp=row.timestamp,
                    missing_candles=str(missing_candles),
                    had_active_trade="YES" if had_active_trade else "NO",
                    forced_exit_trade_id=forced_exit_trade_id,
                    pre_gap_close_points=format_number(prev_row.close_value),
                    pre_gap_ma=format_number(prev_row.ma_value) if prev_row.ma_value is not None else "",
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
            if candle_stop_hit(active_trade, row):
                stop_exit = build_trade_result(
                    active_trade=active_trade,
                    exit_candle_timestamp=row.timestamp,
                    exit_timestamp=format_timestamp(boundary_dt),
                    exit_price=active_trade.stop_ma,
                    exit_reason="stop_loss_ma_touch",
                    exit_ma=active_trade.stop_ma,
                )
                trade_results.append(stop_exit)
                extend_held_days(held_days, active_trade, stop_exit.exit_timestamp)
                logger.info(
                    "STOP_EXIT timeframe=%s trade_id=%s direction=%s exit=%s exit_price=%s",
                    spec.timeframe,
                    active_trade.trade_id,
                    active_trade.direction,
                    stop_exit.exit_timestamp,
                    stop_exit.exit_price_points,
                )
                active_trade = None
            elif row.ma_value is not None:
                active_trade.stop_ma = row.ma_value

        if active_trade is None and row.ma_value is not None:
            new_trade = evaluate_entry(row, boundary_dt, make_trade_id(trade_counter))
            if new_trade is not None:
                active_trade = new_trade
                trade_counter += 1
                logger.info(
                    "ENTRY timeframe=%s trade_id=%s direction=%s signal=%s entry=%s entry_price=%s stop_ma=%s",
                    spec.timeframe,
                    active_trade.trade_id,
                    active_trade.direction,
                    active_trade.signal_timestamp,
                    active_trade.entry_timestamp,
                    active_trade.entry_price_text,
                    format_number(active_trade.stop_ma),
                )

        prev_row = row
        last_processed_row = row

    if active_trade is not None and last_processed_row is not None:
        final_exit = build_trade_result(
            active_trade=active_trade,
            exit_candle_timestamp=last_processed_row.timestamp,
            exit_timestamp=format_timestamp(last_processed_row.dt + spec.step_delta),
            exit_price=last_processed_row.close_value,
            exit_reason="end_of_data",
            exit_ma=active_trade.stop_ma,
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
        "COMPLETED timeframe=%s trades=%s gaps=%s candidate_days=%s",
        spec.timeframe,
        len(trade_results),
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
    )


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def compute_max_consecutive_streaks(point_values: list[float]) -> tuple[int, int]:
    max_wins = 0
    max_losses = 0
    current_wins = 0
    current_losses = 0

    for value in point_values:
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


def summarize_trades(results: list[TradeResult]) -> dict[str, Any]:
    point_values = [float(result.points_pnl) for result in results]
    total_points = sum(point_values)
    max_wins, max_losses = compute_max_consecutive_streaks(point_values)
    max_drawdown = compute_max_drawdown(point_values)

    return {
        "trades": len(results),
        "long_trades": sum(1 for result in results if result.direction == "LONG"),
        "short_trades": sum(1 for result in results if result.direction == "SHORT"),
        "stop_exits": sum(1 for result in results if result.exit_reason == "stop_loss_ma_touch"),
        "gap_exits": sum(1 for result in results if result.exit_reason == "gap_exit_missing_candles"),
        "end_of_data_exits": sum(1 for result in results if result.exit_reason == "end_of_data"),
        "winning_trades": sum(1 for value in point_values if value > 0),
        "losing_trades": sum(1 for value in point_values if value < 0),
        "break_even_trades": sum(1 for value in point_values if value == 0),
        "total_points": total_points,
        "average_points": total_points / len(results) if results else 0.0,
        "max_profit": max(results, key=lambda result: float(result.points_pnl), default=None),
        "max_loss": min(results, key=lambda result: float(result.points_pnl), default=None),
        "max_consecutive_wins": max_wins,
        "max_consecutive_losses": max_losses,
        "max_drawdown_points": max_drawdown,
        "win_rate_pct": (sum(1 for value in point_values if value > 0) / len(results) * 100.0)
        if results
        else 0.0,
    }


def build_daywise_results(run: TimeframeRun) -> list[DayResult]:
    trades_by_day: dict[str, list[TradeResult]] = {}
    gaps_by_day: dict[str, list[GapEvent]] = {}
    for trade in run.trade_results:
        trades_by_day.setdefault(trade.report_date, []).append(trade)
    for gap_event in run.gap_events:
        gaps_by_day.setdefault(gap_event.report_date, []).append(gap_event)

    report_days = sorted(set(run.candidate_days) | set(trades_by_day) | set(gaps_by_day))
    rows: list[DayResult] = []
    for day in report_days:
        day_trades = trades_by_day.get(day, [])
        day_gaps = gaps_by_day.get(day, [])
        point_values = [float(result.points_pnl) for result in day_trades]
        total_points = sum(point_values)
        max_wins, max_losses = compute_max_consecutive_streaks(point_values)
        max_drawdown = compute_max_drawdown(point_values)

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
                gap_exits=str(
                    sum(1 for result in day_trades if result.exit_reason == "gap_exit_missing_candles")
                ),
                end_of_data_exits=str(
                    sum(1 for result in day_trades if result.exit_reason == "end_of_data")
                ),
                winning_trades=str(sum(1 for value in point_values if value > 0)),
                losing_trades=str(sum(1 for value in point_values if value < 0)),
                break_even_trades=str(sum(1 for value in point_values if value == 0)),
                total_points=format_number(total_points),
                average_points=format_number(total_points / len(day_trades) if day_trades else 0.0),
                max_profit_points=format_number(max(point_values)) if point_values else "",
                max_loss_points=format_number(min(point_values)) if point_values else "",
                max_consecutive_wins=str(max_wins),
                max_consecutive_losses=str(max_losses),
                max_drawdown_points=format_number(max_drawdown),
                remarks="; ".join(remarks_parts),
            )
        )

    return rows


def aggregate_day_results(period: str, rows: list[DayResult]) -> AggregateResult:
    traded_rows = [row for row in rows if int(row.trades) > 0]
    point_values = [float(row.total_points) for row in traded_rows]
    total_points = sum(point_values)
    max_wins, max_losses = compute_max_consecutive_streaks(point_values)
    max_drawdown = compute_max_drawdown(point_values)
    max_profit = max(traded_rows, key=lambda row: float(row.total_points), default=None)
    max_loss = min(traded_rows, key=lambda row: float(row.total_points), default=None)

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
        gap_exits=str(sum(int(row.gap_exits) for row in rows)),
        end_of_data_exits=str(sum(int(row.end_of_data_exits) for row in rows)),
        winning_days=str(sum(1 for value in point_values if value > 0)),
        losing_days=str(sum(1 for value in point_values if value < 0)),
        break_even_days=str(sum(1 for value in point_values if value == 0)),
        total_points=format_number(total_points),
        average_points=format_number(total_points / len(traded_rows) if traded_rows else 0.0),
        max_profit_date=max_profit.date if max_profit else "",
        max_profit_points=max_profit.total_points if max_profit else "",
        max_loss_date=max_loss.date if max_loss else "",
        max_loss_points=max_loss.total_points if max_loss else "",
        max_consecutive_wins=str(max_wins),
        max_consecutive_losses=str(max_losses),
        max_drawdown_points=format_number(max_drawdown),
    )


def aggregate_by_period(rows: list[DayResult], period_length: int) -> list[AggregateResult]:
    grouped: dict[str, list[DayResult]] = {}
    for row in rows:
        grouped.setdefault(row.date[:period_length], []).append(row)
    return [aggregate_day_results(period, grouped[period]) for period in sorted(grouped)]


def aggregate_table_lines(rows: list[AggregateResult]) -> list[str]:
    lines = [
        "| Period | Days | Held | Flat | Skipped | Trades | Gaps | Long | Short | Stops | Gap Exits | EOD | Win Days | Loss Days | Points | Avg Points | Max Profit | Max Loss | Max DD |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
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
            f"{row.long_trades} | "
            f"{row.short_trades} | "
            f"{row.stop_exits} | "
            f"{row.gap_exits} | "
            f"{row.end_of_data_exits} | "
            f"{row.winning_days} | "
            f"{row.losing_days} | "
            f"{row.total_points} | "
            f"{row.average_points} | "
            f"{row.max_profit_points} | "
            f"{row.max_loss_points} | "
            f"{row.max_drawdown_points} |"
        )
    return lines


def json_ready(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, set):
        return sorted(value)
    if isinstance(value, dt.datetime):
        return format_timestamp(value)
    if hasattr(value, "__dataclass_fields__"):
        return {key: json_ready(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {key: json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_ready(item) for item in value]
    return value


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
        f"# BTC {run.spec.timeframe} MA{run.spec.ma_period} Continuous Trailing Backtest",
        "",
        "## Strategy Details",
        "",
        f"- Dataset: `{display_path(run.input_file, repo_root)}`",
        f"- Tested UTC date range: `{daywise_results[0].date if daywise_results else 'N/A'}` through `{daywise_results[-1].date if daywise_results else 'N/A'}`",
        f"- Signal source: BTC-USD {run.spec.timeframe} close",
        f"- Initial activation: `{run.activation_timestamp}` (one-time UTC activation threshold)",
        "- No routine day-end exit; positions carry continuously until stopped, forced flat on a data gap, or exited at end of data.",
        f"- MA rule: {run.spec.ma_period}-SMA of {run.spec.timeframe} closes computed fresh from the BTC dataset",
        "- Direction rule: close above SMA -> long; close below SMA -> short; equal -> no entry",
        "- Stop rule: long exits when candle low touches the trailing SMA; short exits when candle high touches the trailing SMA",
        "- Re-entry rule: after a stop, the same completed candle may immediately open a new trade if the signal remains valid.",
        "- Gap rule: force flat at the last known boundary before a gap, then resume on the first post-gap candle and allow a new entry only after that candle completes.",
        "- Accounting: points only; no brokerage, slippage, leverage, or position sizing.",
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
        f"- Win rate: `{format_number(overall_trade_summary['win_rate_pct'])}%`",
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
            "- Opposite signals are ignored while a position is live; only the trailing SMA stop or a gap flat can close the trade.",
            "- The entry candle itself cannot stop a newly opened position.",
            "- Daywise results are grouped by realized exit date in UTC; held-only dates are preserved separately.",
            "- Monthly and yearly results are derived from daywise realized P&L in points.",
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
    overall_trade_summary = summarize_trades(run.trade_results)

    trades_path = run.output_dir / "trades.csv"
    gaps_path = run.output_dir / "gap_events.csv"
    daywise_path = run.output_dir / "daywise_summary.csv"
    monthly_path = run.output_dir / "monthly_summary.csv"
    yearly_path = run.output_dir / "yearly_summary.csv"
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
            "exit_candle_timestamp",
            "exit_timestamp",
            "exit_price_points",
            "exit_reason",
            "exit_ma",
            "points_pnl",
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
            "gap_exits",
            "end_of_data_exits",
            "winning_trades",
            "losing_trades",
            "break_even_trades",
            "total_points",
            "average_points",
            "max_profit_points",
            "max_loss_points",
            "max_consecutive_wins",
            "max_consecutive_losses",
            "max_drawdown_points",
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
            "gap_exits",
            "end_of_data_exits",
            "winning_days",
            "losing_days",
            "break_even_days",
            "total_points",
            "average_points",
            "max_profit_date",
            "max_profit_points",
            "max_loss_date",
            "max_loss_points",
            "max_consecutive_wins",
            "max_consecutive_losses",
            "max_drawdown_points",
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
            "gap_exits",
            "end_of_data_exits",
            "winning_days",
            "losing_days",
            "break_even_days",
            "total_points",
            "average_points",
            "max_profit_date",
            "max_profit_points",
            "max_loss_date",
            "max_loss_points",
            "max_consecutive_wins",
            "max_consecutive_losses",
            "max_drawdown_points",
        ],
    )

    output_files = [
        trades_path,
        gaps_path,
        daywise_path,
        monthly_path,
        yearly_path,
        summary_json_path,
        summary_md_path,
        log_path,
    ]

    summary_payload = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "strategy": "BTC local continuous trailing-MA backtest",
        "timeframe": run.spec.timeframe,
        "ma_period": run.spec.ma_period,
        "expected_candle_interval": run.spec.timeframe,
        "source_dataset": display_path(run.input_file, repo_root),
        "tested_utc_date_range": {
            "start": daywise_results[0].date if daywise_results else "",
            "end": daywise_results[-1].date if daywise_results else "",
        },
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
        "winning_trades": str(overall_trade_summary["winning_trades"]),
        "losing_trades": str(overall_trade_summary["losing_trades"]),
        "win_rate_pct": format_number(overall_trade_summary["win_rate_pct"]),
        "total_points": format_number(overall_trade_summary["total_points"]),
        "average_points": format_number(overall_trade_summary["average_points"]),
        "max_drawdown_points": format_number(overall_trade_summary["max_drawdown_points"]),
    }

    return {
        "run": run,
        "summary_row": summary_row,
        "summary_payload": summary_payload,
        "output_files": output_files,
    }


def build_timeframe_table_lines(rows: list[dict[str, str]]) -> list[str]:
    lines = [
        "| Timeframe | MA | Date Range | First MA Row | Activation | Gaps | Trades | Win Rate % | Total Points | Avg Points | Max DD |",
        "|---|---:|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"{row['timeframe']} | "
            f"{row['ma_period']} | "
            f"{row['tested_start_date']} -> {row['tested_end_date']} | "
            f"{row['first_ma_usable_timestamp']} | "
            f"{row['activation_timestamp']} | "
            f"{row['gap_events']} | "
            f"{row['total_trades']} | "
            f"{row['win_rate_pct']} | "
            f"{row['total_points']} | "
            f"{row['average_points']} | "
            f"{row['max_drawdown_points']} |"
        )
    return lines


def write_top_level_summary_markdown(
    output_path: Path,
    timeframe_rows: list[dict[str, str]],
    timeframe_artifacts: list[dict[str, Any]],
    output_files: list[Path],
    repo_root: Path,
) -> None:
    lines: list[str] = [
        "# BTC Local Multi-Timeframe Continuous MA Backtest",
        "",
        "## Strategy Details",
        "",
        "- Results are written under `btc/results`.",
        "- Tested mappings:",
        "  - `15m` with `MA 96`",
        "  - `30m` with `MA 48`",
        "  - `1h` with `MA 24`",
        "- Earlier `common-strategies` BTC outputs were not used for this run and were left untouched.",
        "- Each timeframe has its own subdirectory with detailed trades, gap events, daywise, monthly, yearly, and summary outputs.",
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
        lines.append(
            f"- `{run.spec.timeframe}`: `{display_path(run.output_dir, repo_root)}` "
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
            "- The multi-timeframe BTC-local workflow supersedes the placement of earlier BTC backtests under `common-strategies` for future runs.",
            "- All timestamps and grouping are UTC.",
            "- Accounting is in raw points only.",
            "- Gap handling is consistent across all selected timeframes: flat gaps log an event; live gaps force an exit at the last known boundary before the gap.",
        ]
    )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    results_root = args.results_dir
    run_name = args.run_name.strip() or (
        f"btc_ma_continuous_multi_timeframe_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}"
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
        timeframe_output_dir = output_dir / spec.subdir_name
        timeframe_output_dir.mkdir(parents=True, exist_ok=True)
        run = run_backtest(
            spec=spec,
            input_file=input_file,
            output_dir=timeframe_output_dir,
            initial_start_time=args.initial_start_time,
            start_date=args.start_date,
            end_date=args.end_date,
        )
        timeframe_artifacts.append(write_timeframe_outputs(run, repo_root))

    timeframe_summary_path = output_dir / "timeframe_summary.csv"
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
            "winning_trades",
            "losing_trades",
            "win_rate_pct",
            "total_points",
            "average_points",
            "max_drawdown_points",
        ],
    )

    top_level_output_files = [
        timeframe_summary_path,
        summary_json_path,
        summary_md_path,
        run_config_path,
    ]

    top_level_summary = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "strategy": "BTC local multi-timeframe continuous trailing-MA backtest",
        "results_root": display_path(output_dir, repo_root),
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
        "timeframe_runs": {
            artifact["run"].spec.timeframe: {
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
        },
        "resolved_paths": {
            "repo_root": str(repo_root.resolve()),
            "data_dir": str(args.data_dir.resolve()),
            "results_root": str(results_root.resolve()),
            "output_dir": str(output_dir.resolve()),
        },
        "timezone": "UTC",
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
        "per_timeframe_metadata": {
            artifact["run"].spec.timeframe: {
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
    )

    print(f"Results written to: {output_dir}")
    for row in timeframe_rows:
        print(
            f"{row['timeframe']}: MA{row['ma_period']}, trades={row['total_trades']}, "
            f"gaps={row['gap_events']}, total_points={row['total_points']}, "
            f"first_ma={row['first_ma_usable_timestamp']}"
        )


if __name__ == "__main__":
    main()
