"""
Run Open Low High backtests across multiple timeframes (5m, 15m, 30m, 1h).

This script tests the same strategy logic across different timeframes to compare
performance and identify which timeframe works best for the strategy.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import open_low_high_5m_strategy as olh


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Open Low High backtests across multiple timeframes",
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
    parser.add_argument("--capital", type=float, default=1000000.0)
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
        type=lambda x: olh.parse_clock(x),
        default=olh.parse_clock("09:15"),
    )
    parser.add_argument(
        "--exit-time",
        type=lambda x: olh.parse_clock(x),
        default=olh.parse_clock("15:20"),
    )
    parser.add_argument("--allow-missing-session-open", action="store_true")
    parser.add_argument("--allow-overnight", action="store_true")
    parser.add_argument(
        "--ambiguous-policy",
        choices=("stop_first", "target_first"),
        default="stop_first",
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
    print(f"Running Open Low High backtest for {timeframe} timeframe")
    print(f"{'=' * 60}")

    # Create args for the strategy
    strategy_args = argparse.Namespace(
        markets=args.markets,
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
        cost_multiplier=args.cost_multiplier,
        equity_slippage=args.equity_slippage,
        derivatives_slippage=args.derivatives_slippage,
        commodities_slippage=args.commodities_slippage,
        session_start=args.session_start,
        exit_time=args.exit_time,
        allow_missing_session_open=args.allow_missing_session_open,
        allow_overnight=args.allow_overnight,
        ambiguous_policy=args.ambiguous_policy,
        top_trade_count=args.top_trade_count,
        run_name=run_name,
    )

    # Temporarily modify the discover_data_files function to use our timeframe
    original_discover = olh.discover_data_files

    def timeframe_discover(repo_root: Path, markets: list[str]) -> list[Path]:
        return discover_data_files_for_timeframe(repo_root, markets, timeframe)

    olh.discover_data_files = timeframe_discover

    try:
        # Run the strategy
        config = olh.config_from_args(strategy_args)

        script_path = Path(__file__).resolve()
        repo_root = script_path.parents[2]
        common_root = script_path.parents[1]
        results_root = common_root / "results"
        default_prefix = f"open_low_high_{timeframe}"
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
        print(f"Running Open Low High backtest on {len(data_files)} files...")

        all_trades: list[dict[str, Any]] = []
        file_stats: list[dict[str, Any]] = []
        skip_counts: dict[str, int] = defaultdict(int)

        for path in data_files:
            trades, stats = olh.backtest_file(path, config, skip_counts)
            all_trades.extend(trades)
            file_stats.append(stats)
            print(
                f"{stats['market']}/{stats['instrument']}: "
                f"{stats['sessions']} sessions, {stats['trades']} trades"
            )

        equity_rows = olh.build_equity_curve(all_trades, config.capital)
        datewise_rows = olh.build_datewise_pnl(all_trades, config.capital)
        instrument_rows = olh.build_instrument_metrics(all_trades)
        best_worst_rows = olh.build_best_worst_trades(all_trades, config.top_trade_count)
        summary = olh.build_summary(
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
            "config": output_dir / "run_config.json",
            "markdown": output_dir / "summary.md",
        }

        olh.write_csv(output_paths["trades"], all_trades)
        olh.write_csv(output_paths["datewise_pnl"], datewise_rows)
        olh.write_csv(output_paths["equity_curve"], equity_rows)
        olh.write_csv(output_paths["instrument_metrics"], instrument_rows)
        olh.write_csv(output_paths["best_worst_trades"], best_worst_rows)
        output_paths["summary"].write_text(
            json.dumps(olh.json_ready(summary), indent=2), encoding="utf-8"
        )
        output_paths["config"].write_text(
            json.dumps(
                {
                    "markets": strategy_args.markets,
                    "timeframe": timeframe,
                    "config": olh.json_ready(config.__dict__),
                    "data_files": [str(path) for path in data_files],
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        output_paths["markdown"].write_text(
            build_simple_markdown_summary(summary, output_paths),
            encoding="utf-8",
        )

        print(f"\n✓ Results written to: {output_dir}")
        print(f"Total trades: {summary['total_trades']}")
        print(f"Net PnL: {summary['net_pnl']}")
        print(f"Win Rate: {summary['win_rate_pct']}%")
        print(f"Max Drawdown: {summary['max_drawdown_pct']}%")
        print(f"Profit Factor: {summary['profit_factor']}")

        # Return summary results
        return {
            "timeframe": timeframe,
            "success": True,
            "output_dir": str(output_dir),
            "data_files_count": len(data_files),
            "summary": summary,
        }

    finally:
        # Restore original function
        olh.discover_data_files = original_discover


def build_simple_markdown_summary(
    summary: dict[str, Any], output_paths: dict[str, Path]
) -> str:
    """Build a simple markdown summary for Open Low High strategy"""
    lines = [
        "# Open Low High Strategy Backtest Results",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Performance Summary",
        "",
        f"- **Total Trades:** {summary['total_trades']}",
        f"- **Net PnL:** {summary['net_pnl']}",
        f"- **Win Rate:** {summary['win_rate_pct']}%",
        f"- **Max Drawdown:** {summary['max_drawdown_pct']}%",
        f"- **Profit Factor:** {summary['profit_factor']}",
        f"- **Average Trade:** {summary['avg_trade']}",
        f"- **Total Sessions:** {summary['total_sessions']}",
        "",
        "## Trade Statistics",
        "",
        f"- **Winning Trades:** {summary['winning_trades']}",
        f"- **Losing Trades:** {summary['losing_trades']}",
        f"- **Average Win:** {summary['avg_win']}",
        f"- **Average Loss:** {summary['avg_loss']}",
        f"- **Largest Win:** {summary['largest_win']}",
        f"- **Largest Loss:** {summary['largest_loss']}",
        "",
        "## Output Files",
        "",
        for name, path in output_paths.items():
            if name != "markdown":
                lines.append(f"- [{name}]({path.name})")
        "",
        "## Configuration",
        "",
        f"- **Capital:** {summary.get('capital', 'N/A')}",
        f"- **Risk Per Trade:** {summary.get('risk_per_trade_pct', 'N/A')}%",
        "",
    ]
    return "\n".join(lines)


def build_multi_timeframe_summary(
    results: list[dict[str, Any]], args: argparse.Namespace
) -> str:
    """Build a summary markdown file comparing all timeframes"""
    lines = [
        "# Open Low High Multi-Timeframe Backtest Results",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Timeframes Tested:** {', '.join(args.timeframes)}",
        f"**Markets:** {', '.join(args.markets)}",
        f"**Cost Multiplier:** {args.cost_multiplier}",
        "",
        "## Timeframe Comparison",
        "",
    ]

    # Create comparison table
    lines.append("| Timeframe | Trades | Net PnL | Win Rate | Max DD | Profit Factor |")
    lines.append("|-----------|--------|---------|----------|--------|---------------|")

    for result in results:
        if not result["success"]:
            lines.append(
                f"| {result['timeframe']} | N/A | N/A | N/A | N/A | N/A |"
            )
            continue

        summary = result["summary"]
        lines.append(
            f"| {result['timeframe']} | "
            f"{summary['total_trades']} | "
            f"{summary['net_pnl']} | "
            f"{summary['win_rate_pct']}% | "
            f"{summary['max_drawdown_pct']}% | "
            f"{summary['profit_factor']} |"
        )

    lines.extend(["", "## Detailed Results", ""])

    for result in results:
        if result["success"]:
            lines.append(f"### {result['timeframe']} Timeframe")
            lines.append(f"- **Output Directory:** `{result['output_dir']}`")
            lines.append(f"- **Data Files:** {result['data_files_count']}")
            lines.append("")

            summary = result["summary"]
            lines.append("**Performance Metrics:**")
            lines.append(f"- Total Trades: {summary['total_trades']}")
            lines.append(f"- Net PnL: {summary['net_pnl']}")
            lines.append(f"- Win Rate: {summary['win_rate_pct']}%")
            lines.append(f"- Max Drawdown: {summary['max_drawdown_pct']}%")
            lines.append(f"- Profit Factor: {summary['profit_factor']}")
            lines.append("")

    return "\n".join(lines)


def main() -> None:
    args = parse_args()

    print("=" * 60)
    print("Open Low High Multi-Timeframe Backtest")
    print("=" * 60)
    print(f"Timeframes: {', '.join(args.timeframes)}")
    print(f"Markets: {', '.join(args.markets)}")
    print(f"Cost Multiplier: {args.cost_multiplier}")
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
    multi_summary_name = args.run_name or f"open_low_high_multi_timeframe_{timestamp}"
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
            summary = result["summary"]
            print(f"    Trades: {summary['total_trades']}, PnL: {summary['net_pnl']}, Win Rate: {summary['win_rate_pct']}%")
        else:
            print(f"  {result['timeframe']}: ✗ Failed - {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()