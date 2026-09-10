"""Command line entry point for fetching USD (CCL) cross rates."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Optional

from .api import ZionApiError, fetch_rates, fetch_rates_by_currency_for_date
from .cross_rates import (
    ALL_CURRENCIES,
    BASE_CURRENCY,
    CrossRate,
    MissingCurrencyError,
    compute_cross_rates,
    index_by_currency,
)


def _parse_pairs(raw_pairs: Optional[list[str]]) -> list[str]:
    """Parse --pairs values (currency codes or USD/XXX pairs) into currency codes."""
    if not raw_pairs:
        return list(ALL_CURRENCIES)

    currencies: list[str] = []
    for item in raw_pairs:
        for token in item.split(","):
            token = token.strip().upper()
            if not token:
                continue
            if "/" in token:
                _, token = token.split("/", 1)
            if token not in ALL_CURRENCIES:
                raise ValueError(
                    f"Unknown currency/pair '{token}'. "
                    f"Supported: {', '.join('USD/' + c for c in ALL_CURRENCIES)}"
                )
            currencies.append(token)

    seen: set[str] = set()
    unique: list[str] = []
    for currency in currencies:
        if currency not in seen:
            seen.add(currency)
            unique.append(currency)
    return unique


def _validate_date(date_str: str) -> str:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(f"Invalid date '{date_str}', expected format YYYY-MM-DD") from exc
    return date_str


def _build_result(cross_rates: list[CrossRate], updated_at: Optional[int], date: Optional[str]) -> dict:
    return {
        "source": "zion.ar",
        "base": "USD (CCL)",
        "date": date,
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
    parser.add_argument(
        "-d",
        "--date",
        type=str,
        help="Rate date in YYYY-MM-DD format (default: latest available rates)",
    )
    parser.add_argument(
        "-p",
        "--pairs",
        type=str,
        nargs="+",
        help=(
            "Currencies or pairs to include, space or comma separated, "
            "e.g. BRL COP or USD/BRL,USD/COP (default: all - ARS BRL BOB COP PYG PEN)"
        ),
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        currencies = _parse_pairs(args.pairs)
        date = _validate_date(args.date) if args.date else None
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    try:
        if date:
            needed = {BASE_CURRENCY} | {currency for currency in currencies if currency != "ARS"}
            by_currency = fetch_rates_by_currency_for_date(date, needed)
            updated_at = None
        else:
            payload = fetch_rates()
            by_currency = index_by_currency(payload["data"])
            updated_at = payload.get("updatedAt")

        cross_rates = compute_cross_rates(by_currency, currencies)
    except ZionApiError as exc:
        print(f"Error calling Zion API: {exc}", file=sys.stderr)
        return 1
    except MissingCurrencyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # network errors, JSON decode errors, etc.
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1

    result = _build_result(cross_rates, updated_at, date)
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
