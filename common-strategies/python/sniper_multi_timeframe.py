"""
Run Sniper Entry/Exit backtests across multiple timeframes (5m, 15m, 30m, 1h).

This script tests the same strategy logic across different timeframes to compare
performance and identify which timeframe works best for the strategy.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import sniper_entry_exit_5m_strategy as sniper


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Sniper Entry/Exit backtests across multiple timeframes",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--timeframes",
        nargs="+",
        default=["5m", "15m", "30m", "1h"],
        help="Timeframes to test (e.g., 5m 15m 30m 1h)",
    )
    parser.add_argument(
        "--markets",
        nargs="+",
        default=["derivatives", "equity", "commodities"],
        help="Markets to test (e.g., derivatives equity commodities)",
    )
    # Strategy parameters
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
        type=lambda x: sniper.base.parse_clock(x),
        default=sniper.base.parse_clock("09:15"),
    )
    parser.add_argument(
        "--exit-time",
        type=lambda x: sniper.base.parse_clock(x),
        default=sniper.base.parse_clock("15:20"),
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
        help="Custom run name (default: auto-generated)",
    )
    return parser.parse_args()


def discover_data_files_for_timeframe(
    repo_root: Path, markets: list[str], timeframe: str
) -> list[Path]:
    """Discover data files for a specific timeframe"""
    files: list[Path] = []
    for market in markets:
        data_dir = repo_root / market / "data"
        if data_dir.exists():
            pattern = f"*_{timeframe}.csv"
            files.extend(sorted(data_dir.glob(pattern)))
    return sorted(files)


def run_backtest_for_timeframe(
    timeframe: str,
    args: argparse.Namespace,
    run_name: str,
) -> dict[str, Any]:
    """Run backtest for a specific timeframe"""
    print(f"\n{'=' * 60}")
    print(f"Running Sniper Entry/Exit backtest for {timeframe} timeframe")
    print(f"{'=' * 60}")

    # Create args for the strategy
    strategy_args = argparse.Namespace(
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
        run_name=run_name,
    )

    # Temporarily modify the discover_data_files function to use our timeframe
    import open_low_high_5m_strategy as base

    original_discover = base.discover_data_files

    def timeframe_discover(repo_root: Path, markets: list[str]) -> list[Path]:
        return discover_data_files_for_timeframe(repo_root, markets, timeframe)

    base.discover_data_files = timeframe_discover

    try:
        # Run the strategy
        config = sniper.config_from_args(strategy_args)

        script_path = Path(__file__).resolve()
        repo_root = script_path.parents[2]
        common_root = script_path.parents[1]
        results_root = common_root / "results"
        default_prefix = (
            f"sniper_entry_exit_inverse_{timeframe}"
            if config.invert_signals
            else f"sniper_entry_exit_{timeframe}"
        )
        final_run_name = run_name or f"{default_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        output_dir = results_root / final_run_name
        output_dir.mkdir(parents=True, exist_ok=True)

        data_files = discover_data_files_for_timeframe(repo_root, strategy_args.markets, timeframe)
        if not data_files:
            print(f"⚠ No data files found for {timeframe} timeframe")
            return {
                "timeframe": timeframe,
                "success": False,
                "error": f"No data files found for {timeframe} timeframe",
                "data_files_count": 0,
            }

        print(f"Found {len(data_files)} data files for {timeframe} timeframe")

        strategy_label = (
            "Inverse Sniper Entry/Exit" if config.invert_signals else "Sniper Entry/Exit"
        )
        print(f"Running {strategy_label} backtest on {len(data_files)} files...")

        summaries: dict[str, dict[str, Any]] = {}
        comparison_rows: list[dict[str, Any]] = []

        for target_level in config.target_levels:
            print(f"\nTesting TP{target_level} full-exit variant")
            trades, file_stats, skip_counts = sniper.backtest_target_level(
                data_files,
                target_level,
                config,
            )
            datewise_rows = base.build_datewise_pnl(trades, config.capital)
            equity_rows = base.build_equity_curve(trades, config.capital)
            market_rows = sniper.build_market_metrics(trades)
            instrument_rows = base.build_instrument_metrics(trades)
            best_worst_rows = base.build_best_worst_trades(trades, config.top_trade_count)
            summary = sniper.summary_for_target(
                target_level, trades, file_stats, skip_counts, config
            )
            summaries[str(target_level)] = summary
            comparison_rows.append(sniper.comparison_row(summary))

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
        summary_path.write_text(
            json.dumps(sniper.json_ready(summaries), indent=2), encoding="utf-8"
        )
        config_path.write_text(
            json.dumps(
                {
                    "markets": strategy_args.markets,
                    "timeframe": timeframe,
                    "config": sniper.json_ready(config.__dict__),
                    "data_files": [str(path) for path in data_files],
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        markdown_path.write_text(
            sniper.build_markdown_summary(comparison_rows, summaries, config, []),
            encoding="utf-8",
        )

        print(f"\n✓ Results written to: {output_dir}")

        # Return summary results
        return {
            "timeframe": timeframe,
            "success": True,
            "output_dir": str(output_dir),
            "data_files_count": len(data_files),
            "summaries": summaries,
            "comparison_rows": comparison_rows,
        }

    finally:
        # Restore original function
        base.discover_data_files = original_discover


def build_multi_timeframe_summary(
    results: list[dict[str, Any]], args: argparse.Namespace
) -> str:
    """Build a summary markdown file comparing all timeframes"""
    lines = [
        "# Sniper Entry/Exit Multi-Timeframe Backtest Results",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Timeframes Tested:** {', '.join(args.timeframes)}",
        f"**Markets:** {', '.join(args.markets)}",
        f"**Cost Multiplier:** {args.cost_multiplier}",
        f"**Invert Signals:** {args.invert_signals}",
        "",
        "## Timeframe Comparison",
        "",
    ]

    # Create comparison table
    lines.append("| Timeframe | TP Level | Trades | Net PnL | Win Rate | Max DD | Profit Factor |")
    lines.append("|-----------|----------|--------|---------|----------|--------|---------------|")

    for result in results:
        if not result["success"]:
            lines.append(
                f"| {result['timeframe']} | N/A | N/A | N/A | N/A | N/A | N/A |"
            )
            continue

        for row in result["comparison_rows"]:
            lines.append(
                f"| {result['timeframe']} | TP{row['target_level']} | "
                f"{row['total_trades']} | {row['net_pnl']} | "
                f"{row['win_rate_pct']}% | {row['max_drawdown_pct']}% | "
                f"{row['profit_factor']} |"
            )

    lines.extend(["", "## Detailed Results", ""])

    for result in results:
        if result["success"]:
            lines.append(f"### {result['timeframe']} Timeframe")
            lines.append(f"- **Output Directory:** `{result['output_dir']}`")
            lines.append(f"- **Data Files:** {result['data_files_count']}")
            lines.append("")

            if result["comparison_rows"]:
                best_tp = max(
                    result["comparison_rows"], key=lambda x: x["net_pnl"]
                )
                lines.append(f"**Best Target Level:** TP{best_tp['target_level']}")
                lines.append(f"- Net PnL: {best_tp['net_pnl']}")
                lines.append(f"- Win Rate: {best_tp['win_rate_pct']}%")
                lines.append(f"- Max Drawdown: {best_tp['max_drawdown_pct']}%")
                lines.append(f"- Profit Factor: {best_tp['profit_factor']}")
                lines.append("")

    return "\n".join(lines)


def main() -> None:
    args = parse_args()

    print("=" * 60)
    print("Sniper Entry/Exit Multi-Timeframe Backtest")
    print("=" * 60)
    print(f"Timeframes: {', '.join(args.timeframes)}")
    print(f"Markets: {', '.join(args.markets)}")
    print(f"Cost Multiplier: {args.cost_multiplier}")
    print(f"Invert Signals: {args.invert_signals}")
    print("=" * 60)

    results: list[dict[str, Any]] = []

    for timeframe in args.timeframes:
        try:
            result = run_backtest_for_timeframe(
                timeframe=timeframe,
                args=args,
                run_name=args.run_name,
            )
            results.append(result)
        except Exception as e:
            print(f"✗ Error running backtest for {timeframe}: {str(e)}")
            results.append(
                {
                    "timeframe": timeframe,
                    "success": False,
                    "error": str(e),
                    "data_files_count": 0,
                }
            )

    # Write multi-timeframe summary
    script_path = Path(__file__).resolve()
    common_root = script_path.parents[1]
    results_root = common_root / "results"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    multi_summary_name = args.run_name or f"sniper_multi_timeframe_{timestamp}"
    multi_output_dir = results_root / multi_summary_name
    multi_output_dir.mkdir(parents=True, exist_ok=True)

    summary_markdown = build_multi_timeframe_summary(results, args)
    summary_path = multi_output_dir / "multi_timeframe_summary.md"
    summary_path.write_text(summary_markdown, encoding="utf-8")

    # Save results as JSON
    results_path = multi_output_dir / "multi_timeframe_results.json"
    results_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print("\n" + "=" * 60)
    print("Multi-Timeframe Backtest Completed!")
    print("=" * 60)
    print(f"Summary written to: {summary_path}")
    print(f"Results saved to: {results_path}")

    # Print summary
    print("\nQuick Summary:")
    for result in results:
        if result["success"]:
            print(f"  {result['timeframe']}: ✓ Success")
            if result["comparison_rows"]:
                best = max(result["comparison_rows"], key=lambda x: x["net_pnl"])
                print(f"    Best: TP{best['target_level']} with PnL={best['net_pnl']}")
        else:
            print(f"  {result['timeframe']}: ✗ Failed - {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()