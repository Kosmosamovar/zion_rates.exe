"""Compute USD (CCL) cross rates against other ARS-quoted currencies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

# CCL dollar (ARS per USD) is used as the bridge to build cross rates.
BASE_CURRENCY = "USDCCL"

TARGET_CURRENCIES = ("ARS", "BRL", "BOB", "COP", "PYG", "PEN")


class MissingCurrencyError(RuntimeError):
    """Raised when a required currency is not present in the API response."""


@dataclass(frozen=True)
class CrossRate:
    pair: str
    rate: float


def _index_by_currency(rates_data: Iterable[dict]) -> dict[str, dict]:
    return {entry["currency"]: entry for entry in rates_data}


def compute_cross_rates(rates_payload: dict) -> list[CrossRate]:
    """Build USD/XXX rates using the CCL dollar as the bridge through ARS."""
    by_currency = _index_by_currency(rates_payload["data"])

    if BASE_CURRENCY not in by_currency:
        raise MissingCurrencyError(f"'{BASE_CURRENCY}' not found in Zion API response")
    usd_ccl_ars = by_currency[BASE_CURRENCY]["sell"]

    results: list[CrossRate] = []
    for currency in TARGET_CURRENCIES:
        if currency == "ARS":
            rate = usd_ccl_ars
        else:
            if currency not in by_currency:
                raise MissingCurrencyError(f"'{currency}' not found in Zion API response")
            currency_ars = by_currency[currency]["sell"]
            rate = usd_ccl_ars / currency_ars
        results.append(CrossRate(pair=f"USD/{currency}", rate=rate))
    return results
