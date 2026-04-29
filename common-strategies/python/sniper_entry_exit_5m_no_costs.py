"""
Run Sniper Entry/Exit backtests with no brokerage, charges, or slippage.

This runner executes both variants:

- normal Sniper: original BUY -> LONG, original SELL -> SHORT
- inverse Sniper: original BUY -> SHORT, original SELL -> LONG

It forces:

- cost_multiplier = 0
- equity_slippage = 0
- derivatives_slippage = 0
- commodities_slippage = 0

Any cost or run-name arguments passed by mistake are ignored and replaced so
the outputs remain clearly separated from the charged backtests.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

import sniper_entry_exit_5m_strategy as sniper


FORCED_OPTIONS = {
    "--cost-multiplier",
    "--equity-slippage",
    "--derivatives-slippage",
    "--commodities-slippage",
    "--run-name",
    "--invert-signals",
}


def strip_forced_options(args: list[str]) -> list[str]:
    cleaned: list[str] = []
    index = 0

    while index < len(args):
        arg = args[index]
        if any(arg == option or arg.startswith(f"{option}=") for option in FORCED_OPTIONS):
            if "=" not in arg and index + 1 < len(args) and not args[index + 1].startswith("--"):
                index += 2
            else:
                index += 1
            continue

        cleaned.append(arg)
        index += 1

    return cleaned


def parse_runner_args(argv: list[str]) -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description="Run normal and inverse Sniper Entry/Exit with zero costs.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--run-prefix",
        default="sniper_entry_exit_5m_no_costs",
        help="Prefix used for generated result folders.",
    )
    parser.add_argument("--skip-normal", action="store_true")
    parser.add_argument("--skip-inverse", action="store_true")
    return parser.parse_known_args(argv)


def run_sniper(mode: str, pass_through_args: list[str], timestamp: str, run_prefix: str) -> None:
    invert = mode == "inverse"
    run_name = f"{run_prefix}_{mode}_{timestamp}"
    argv = [
        "sniper_entry_exit_5m_strategy.py",
        *pass_through_args,
        "--cost-multiplier",
        "0",
        "--equity-slippage",
        "0",
        "--derivatives-slippage",
        "0",
        "--commodities-slippage",
        "0",
        "--run-name",
        run_name,
    ]
    if invert:
        argv.append("--invert-signals")

    print("")
    print(f"Running {mode} no-cost Sniper backtest -> {run_name}")
    original_argv = sys.argv
    try:
        sys.argv = argv
        sniper.main()
    finally:
        sys.argv = original_argv


def main() -> None:
    runner_args, unknown_args = parse_runner_args(sys.argv[1:])
    if runner_args.skip_normal and runner_args.skip_inverse:
        raise SystemExit("Nothing to run: both --skip-normal and --skip-inverse were supplied.")

    pass_through_args = strip_forced_options(unknown_args)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if not runner_args.skip_normal:
        run_sniper("normal", pass_through_args, timestamp, runner_args.run_prefix)
    if not runner_args.skip_inverse:
        run_sniper("inverse", pass_through_args, timestamp, runner_args.run_prefix)


if __name__ == "__main__":
    main()
