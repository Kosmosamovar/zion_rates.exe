"""Compute USD (CCL) cross rates against other ARS-quoted currencies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

# CCL dollar (ARS per USD) is used as the bridge to build cross rates.
BASE_CURRENCY = "USDCCL"

ALL_CURRENCIES = ("ARS", "BRL", "BOB", "COP", "PYG", "PEN")


class MissingCurrencyError(RuntimeError):
    """Raised when a required currency is not present in the rates data."""


@dataclass(frozen=True)
class CrossRate:
    pair: str
    rate: float


def index_by_currency(rates_data: Iterable[dict]) -> dict[str, dict]:
    return {entry["currency"]: entry for entry in rates_data}


def compute_cross_rates(
    by_currency: Mapping[str, dict], currencies: Iterable[str] = ALL_CURRENCIES
) -> list[CrossRate]:
    """Build USD/XXX rates using the CCL dollar as the bridge through ARS."""
    if BASE_CURRENCY not in by_currency:
        raise MissingCurrencyError(f"'{BASE_CURRENCY}' not found in rates data")
    usd_ccl_ars = by_currency[BASE_CURRENCY]["sell"]

    results: list[CrossRate] = []
    for currency in currencies:
        if currency == "ARS":
            rate = usd_ccl_ars
        else:
            if currency not in by_currency:
                raise MissingCurrencyError(f"'{currency}' not found in rates data")
            currency_ars = by_currency[currency]["sell"]
            rate = usd_ccl_ars / currency_ars
        results.append(CrossRate(pair=f"USD/{currency}", rate=rate))
    return results
