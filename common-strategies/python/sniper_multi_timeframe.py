"""
Run Sniper Entry/Exit backtests across multiple timeframes.

The runner keeps the Sniper strategy logic in sniper_entry_exit_5m_strategy.py,
but compares the same rules across 5m, 15m, 30m, and 1h data. Output is kept
compact: one detailed markdown summary, one JSON summary, one comparison CSV,
and an optional full trade audit CSV.
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from datetime import datetime, time
from pathlib import Path
from typing import Any

import open_low_high_5m_strategy as base
import sniper_entry_exit_5m_strategy as sniper


DEFAULT_TIMEFRAMES = ("5m", "15m", "30m", "1h")
DEFAULT_MARKETS = ("derivatives", "equity", "commodities", "usdinr")
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


def timeframe_sort_key(timeframe: str) -> tuple[int, str]:
    try:
        return DEFAULT_TIMEFRAMES.index(timeframe), timeframe
    except ValueError:
        return len(DEFAULT_TIMEFRAMES), timeframe


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Sniper Entry/Exit backtests across multiple timeframes.",
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
    parser.add_argument(
        "--run-name",
        default="",
        help="Custom run name.",
    )
    parser.add_argument(
        "--write-trade-audit",
        action="store_true",
        help="Also write one all_trades.csv audit file. Default keeps output to summaries only.",
    )
    return parser.parse_args()


def strategy_args_from_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        markets=args.markets,
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
        allow_missing_session_open=args.allow_missing_session_open,
        allow_overnight=args.allow_overnight,
        ambiguous_policy=args.ambiguous_policy,
        target_levels=args.target_levels,
        invert_signals=args.invert_signals,
        top_trade_count=args.top_trade_count,
        run_name=args.run_name,
    )


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


def sum_trade_value(trades: list[dict[str, Any]], key: str) -> float:
    return sum(float(trade.get(key, 0.0) or 0.0) for trade in trades)


def profit_factor_from_values(values: list[float]) -> float | str:
    gross_profit = sum(max(value, 0.0) for value in values)
    gross_loss = abs(sum(min(value, 0.0) for value in values))
    if gross_loss == 0:
        return "inf" if gross_profit > 0 else ""
    return gross_profit / gross_loss


def charge_breakdown_for_trade(
    trade: dict[str, Any],
    config: sniper.SniperConfig,
) -> dict[str, Any]:
    segment = base.charge_segment_for_market(trade["market"], trade["instrument"])
    return base.charge_breakdown_for_segment(
        abs(float(trade["entry_price"])) * int(trade["quantity"]),
        abs(float(trade["exit_price"])) * int(trade["quantity"]),
        segment,
        float(config.cost_multiplier),
    )


def annotate_trades(
    trades: list[dict[str, Any]],
    timeframe: str,
    config: sniper.SniperConfig,
) -> None:
    for trade in trades:
        trade["timeframe"] = timeframe
        charges = charge_breakdown_for_trade(trade, config)
        trade["charge_segment"] = charges["segment"]
        trade["charge_segment_label"] = charges["segment_label"]
        trade["turnover"] = charges["turnover"]
        trade["brokerage"] = charges["brokerage"]
        trade["stt"] = charges.get("stt", 0.0)
        trade["ctt"] = charges.get("ctt", 0.0)
        trade["exchange_charge"] = charges["exchange_charge"]
        trade["gst"] = charges["gst"]
        trade["sebi_charges"] = charges["sebi_charges"]
        trade["stamp_duty"] = charges["stamp_duty"]


def max_drawdown(equity_rows: list[dict[str, Any]], starting_capital: float) -> tuple[float, float]:
    equity_values = [starting_capital] + [float(row["equity"]) for row in equity_rows]
    return base.max_drawdown_from_equity(equity_values)


def summary_for_timeframe_target(
    timeframe: str,
    target_level: int,
    trades: list[dict[str, Any]],
    file_stats: list[dict[str, Any]],
    skip_counts: dict[str, int],
    config: sniper.SniperConfig,
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
        "strategy": (
            "Inverse Sniper Entry/Exit multi-timeframe backtest"
            if config.invert_signals
            else "Sniper Entry/Exit multi-timeframe backtest"
        ),
        "signal_mode": "inverse" if config.invert_signals else "normal",
        "timeframe": timeframe,
        "target_level": target_level,
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
        "target_level": summary["target_level"],
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
    grouped: dict[tuple[str, int, str, str], list[dict[str, Any]]] = defaultdict(list)
    for trade in trades:
        grouped[
            (
                str(trade["timeframe"]),
                int(trade["target_level"]),
                str(trade["market"]),
                str(trade["instrument"]),
            )
        ].append(trade)

    rows: list[dict[str, Any]] = []
    for (timeframe, target_level, market, instrument), group_trades in sorted(
        grouped.items(),
        key=lambda item: (timeframe_sort_key(item[0][0]), item[0][1], item[0][2], item[0][3]),
    ):
        net_values = [float(trade["net_pnl"]) for trade in group_trades]
        wins = [value for value in net_values if value > 0]
        rows.append(
            {
                "timeframe": timeframe,
                "target_level": target_level,
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
            }
        )
    return rows


def build_charge_rows(trades: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, int, str, str], list[dict[str, Any]]] = defaultdict(list)
    for trade in trades:
        grouped[
            (
                str(trade["timeframe"]),
                int(trade["target_level"]),
                str(trade.get("charge_segment", "")),
                str(trade.get("charge_segment_label", "")),
            )
        ].append(trade)

    rows: list[dict[str, Any]] = []
    for (timeframe, target_level, segment, label), group_trades in sorted(
        grouped.items(),
        key=lambda item: (timeframe_sort_key(item[0][0]), item[0][1], item[0][2], item[0][3]),
    ):
        turnover = sum_trade_value(group_trades, "turnover")
        total = sum_trade_value(group_trades, "costs")
        rows.append(
            {
                "timeframe": timeframe,
                "target_level": target_level,
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
    grouped: dict[tuple[str, int, str, str], list[dict[str, Any]]] = defaultdict(list)
    for trade in trades:
        grouped[
            (
                str(trade["timeframe"]),
                int(trade["target_level"]),
                str(trade["direction"]),
                str(trade["exit_reason"]),
            )
        ].append(trade)

    rows: list[dict[str, Any]] = []
    for (timeframe, target_level, direction, exit_reason), group_trades in sorted(
        grouped.items(),
        key=lambda item: (timeframe_sort_key(item[0][0]), item[0][1], item[0][2], item[0][3]),
    ):
        rows.append(
            {
                "timeframe": timeframe,
                "target_level": target_level,
                "direction": direction,
                "exit_reason": exit_reason,
                "trades": len(group_trades),
                "gross_pnl_before_brokerage": round(sum_trade_value(group_trades, "gross_pnl"), 2),
                "brokerage_and_charges": round(sum_trade_value(group_trades, "costs"), 2),
                "net_pnl_after_brokerage": round(sum_trade_value(group_trades, "net_pnl"), 2),
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
                    "target_level": trade["target_level"],
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
        traded_rows = [row for row in timeframe_rows if int(row["total_trades"]) > 0]
        if not traded_rows:
            rows.append(
                {
                    "timeframe": timeframe,
                    "best_target_level": "no_trades",
                    "trades": 0,
                    "gross_pnl_before_brokerage": 0,
                    "brokerage_and_charges": 0,
                    "net_pnl_after_brokerage": 0,
                    "win_rate_pct": 0.0,
                    "profit_factor": "",
                }
            )
            continue

        best = max(traded_rows, key=lambda row: float(row["net_pnl_after_brokerage"]))
        rows.append(
            {
                "timeframe": timeframe,
                "best_target_level": best["target_level"],
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
    rows: list[dict[str, Any]] = []
    for result in run_results:
        if not result.get("success"):
            rows.append(
                {
                    "timeframe": result["timeframe"],
                    "target_level": result.get("target_level", ""),
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
                    "target_level": result["target_level"],
                    "reason": reason,
                    "count": count,
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


def build_summary_markdown(payload: dict[str, Any], config: sniper.SniperConfig) -> str:
    comparison_rows = payload["timeframe_target_summary"]
    best_by_timeframe_rows = payload["best_by_timeframe"]
    instrument_rows = payload["what_traded_by_instrument"]
    charge_rows = payload["brokerage_by_segment"]
    direction_exit_rows = payload["direction_exit_summary"]
    best_worst_rows = payload["best_worst_trades"]
    skip_rows = payload["skipped_signals"]
    failed_runs = [result for result in payload["runs"] if not result.get("success")]
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
        "# Sniper Entry/Exit Multi-Timeframe Backtest",
        "",
        "## Executive Summary",
        "",
        f"- **generated_at**: {payload['generated_at']}",
        f"- **markets_tested**: {', '.join(payload['markets'])}",
        f"- **timeframes_tested**: {', '.join(payload['timeframes'])}",
        f"- **target_levels_tested**: TP{', TP'.join(str(level) for level in payload['target_levels'])}",
        f"- **signal_mode**: {payload['signal_mode']}",
        f"- **starting_capital**: {config.capital}",
        f"- **best_after_brokerage**: {best_net.get('timeframe', '')} / "
        f"TP{best_net.get('target_level', '')} = {best_net.get('net_pnl_after_brokerage', '')}",
        f"- **best_before_brokerage**: {best_gross.get('timeframe', '')} / "
        f"TP{best_gross.get('target_level', '')} = {best_gross.get('gross_pnl_before_brokerage', '')}",
        "- **pnl_note**: Before Brokerage includes configured slippage; After Brokerage subtracts segment-wise brokerage, taxes, and charges.",
        "",
        "## Timeframe And Target Results",
        "",
    ]
    append_markdown_table(
        lines,
        comparison_rows,
        [
            ("Timeframe", "timeframe"),
            ("Target", "target_level"),
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

    lines.extend(["", "## Best Target Per Timeframe", ""])
    append_markdown_table(
        lines,
        best_by_timeframe_rows,
        [
            ("Timeframe", "timeframe"),
            ("Best Target", "best_target_level"),
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
            ("Target", "target_level"),
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
            ("Target", "target_level"),
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
            ("Target", "target_level"),
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
            ("Target", "target_level"),
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

    lines.extend(
        [
            "",
            "## Backtest Rules",
            "",
            "- Signal uses EMA fast / EMA slow crossovers from the selected timeframe.",
            "- In inverse mode, original BUY signals are traded as SHORT and original SELL signals are traded as LONG."
            if config.invert_signals
            else "- Original BUY signals are traded as LONG and original SELL signals are traded as SHORT.",
            "- Entry is the next candle open after signal close to avoid lookahead.",
            "- Stop and TP levels are anchored to the signal candle close.",
            "- TP1 through TP5 are tested as separate full-position exits by default.",
            "- Trades also exit on stop, opposite signal, session end, or final bar.",
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
            ("Target", "target_level"),
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
                ("Target", "target_level"),
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


def run_timeframe(
    timeframe: str,
    data_files: list[Path],
    config: sniper.SniperConfig,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    run_results: list[dict[str, Any]] = []
    comparison_rows: list[dict[str, Any]] = []
    all_trades: list[dict[str, Any]] = []

    original_instrument_name = base.instrument_name

    def timeframe_instrument_name(path: Path) -> str:
        return instrument_name_for_timeframe(path, timeframe)

    base.instrument_name = timeframe_instrument_name
    try:
        for target_level in config.target_levels:
            print(f"\nTesting {timeframe} / TP{target_level}")
            trades, file_stats, skip_counts = sniper.backtest_target_level(
                data_files,
                target_level,
                config,
            )
            annotate_trades(trades, timeframe, config)
            summary = summary_for_timeframe_target(
                timeframe,
                target_level,
                trades,
                file_stats,
                skip_counts,
                config,
            )
            all_trades.extend(trades)
            comparison_rows.append(comparison_row(summary))
            run_results.append(
                {
                    "timeframe": timeframe,
                    "target_level": target_level,
                    "success": True,
                    "data_files_count": len(data_files),
                    "summary": summary,
                    "file_stats": file_stats,
                }
            )
            print(
                f"  {timeframe}/TP{target_level}: "
                f"trades={summary['total_trades']}, "
                f"before_brokerage={summary['gross_pnl_before_brokerage']}, "
                f"charges={summary['brokerage_and_charges']}, "
                f"after_brokerage={summary['net_pnl_after_brokerage']}, "
                f"pf={summary['profit_factor']}"
            )
    finally:
        base.instrument_name = original_instrument_name

    return all_trades, comparison_rows, run_results


def main() -> None:
    args = parse_args()
    timeframes = parse_timeframes(args.timeframes)
    config = sniper.config_from_args(strategy_args_from_args(args))

    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[2]
    common_root = script_path.parents[1]
    results_root = common_root / "results"
    run_name = args.run_name.strip() or (
        f"sniper_multi_timeframe_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    output_dir = results_root / run_name
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Sniper Entry/Exit Multi-Timeframe Backtest")
    print("=" * 60)
    print(f"Timeframes: {', '.join(timeframes)}")
    print(f"Markets: {', '.join(args.markets)}")
    print(f"Targets: TP{', TP'.join(str(level) for level in config.target_levels)}")
    print(f"Cost Multiplier: {args.cost_multiplier}")
    print(f"Invert Signals: {args.invert_signals}")
    print("=" * 60)

    all_trades: list[dict[str, Any]] = []
    comparison_rows: list[dict[str, Any]] = []
    run_results: list[dict[str, Any]] = []
    data_files_by_timeframe: dict[str, list[str]] = {}

    for timeframe in timeframes:
        data_files = discover_data_files_for_timeframe(repo_root, args.markets, timeframe)
        data_files_by_timeframe[timeframe] = [str(path) for path in data_files]
        if not data_files:
            error = f"No *_{timeframe}.csv files found in selected market data folders."
            print(f"\n{timeframe}: {error}")
            for target_level in config.target_levels:
                run_results.append(
                    {
                        "timeframe": timeframe,
                        "target_level": target_level,
                        "success": False,
                        "error": error,
                        "data_files_count": 0,
                    }
                )
            continue

        print(f"\n{timeframe}: found {len(data_files)} files")
        timeframe_trades, timeframe_rows, timeframe_results = run_timeframe(
            timeframe,
            data_files,
            config,
        )
        all_trades.extend(timeframe_trades)
        comparison_rows.extend(timeframe_rows)
        run_results.extend(timeframe_results)

    if not comparison_rows:
        raise SystemExit("No backtests ran because no data files were found.")

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "strategy": "Sniper Entry/Exit multi-timeframe backtest",
        "signal_mode": "inverse" if config.invert_signals else "normal",
        "markets": args.markets,
        "timeframes": list(timeframes),
        "target_levels": list(config.target_levels),
        "configuration": json_ready(config.__dict__),
        "cost_model": base.cost_model_summary(config),
        "data_files": data_files_by_timeframe,
        "timeframe_target_summary": comparison_rows,
        "best_by_timeframe": build_best_by_timeframe_rows(comparison_rows),
        "what_traded_by_instrument": build_instrument_rows(all_trades),
        "brokerage_by_segment": build_charge_rows(all_trades),
        "direction_exit_summary": build_direction_exit_rows(all_trades),
        "best_worst_trades": build_best_worst_trade_rows(all_trades, config.top_trade_count),
        "skipped_signals": build_skip_rows(run_results),
        "runs": run_results,
    }

    comparison_path = output_dir / "timeframe_target_summary.csv"
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
    markdown_path.write_text(build_summary_markdown(payload, config), encoding="utf-8")

    print("\n" + "=" * 60)
    print("Multi-Timeframe Backtest Completed")
    print("=" * 60)
    print(f"Results written to: {output_dir}")
    print("Timeframe/target comparison:")
    for row in comparison_rows:
        print(
            f"  {row['timeframe']}/TP{row['target_level']}: "
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
