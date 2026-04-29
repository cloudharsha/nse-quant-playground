"""
Run the inverse Sniper Entry/Exit strategy on 5-minute data.

This is a thin wrapper over sniper_entry_exit_5m_strategy.py. It keeps every
indicator, stop, target, fee, and reporting rule the same, but flips the trade
side:

- Original BUY signal -> SHORT trade
- Original SELL signal -> LONG trade
"""

from __future__ import annotations

import sys

import sniper_entry_exit_5m_strategy as sniper


def main() -> None:
    if "--invert-signals" not in sys.argv:
        sys.argv.append("--invert-signals")
    sniper.main()


if __name__ == "__main__":
    main()
