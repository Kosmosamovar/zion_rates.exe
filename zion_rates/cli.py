"""Command line entry point for fetching USD (CCL) cross rates."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Optional

from .api import ZionApiError, fetch_rates
from .cross_rates import CrossRate, MissingCurrencyError, compute_cross_rates


def _build_result(cross_rates: list[CrossRate], updated_at: Optional[int]) -> dict:
    return {
        "source": "zion.ar",
        "base": "USD (CCL)",
        "updatedAt": updated_at,
        "updatedAtIso": (
            datetime.fromtimestamp(updated_at / 1000, tz=timezone.utc).isoformat()
            if updated_at
            else None
        ),
        "rates": [{"pair": cr.pair, "rate": round(cr.rate, 6)} for cr in cross_rates],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch USD (CCL) cross rates for ARS, BRL, BOB, COP, PYG, PEN from zion.ar"
    )
    parser.add_argument("-o", "--output", type=str, help="Path to write JSON output (default: stdout)")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        payload = fetch_rates()
        cross_rates = compute_cross_rates(payload)
    except ZionApiError as exc:
        print(f"Error calling Zion API: {exc}", file=sys.stderr)
        return 1
    except MissingCurrencyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # network errors, JSON decode errors, etc.
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1

    result = _build_result(cross_rates, payload.get("updatedAt"))
    text = json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Written to {args.output}")
    else:
        print(text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
