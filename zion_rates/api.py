"""Client for the Zion (zion.ar) public rates API."""

from __future__ import annotations

from typing import Iterable

import requests

API_BASE_URL = "https://zion.ar/api/v1"
REQUEST_TIMEOUT = 10


class ZionApiError(RuntimeError):
    """Raised when the Zion API returns an unexpected response."""


def fetch_rates() -> dict:
    """Fetch the latest exchange rates snapshot from the Zion API."""
    response = requests.get(f"{API_BASE_URL}/rates", timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    payload = response.json()
    if "data" not in payload:
        raise ZionApiError(f"Unexpected response shape from Zion API: {payload}")
    return payload


def fetch_rate_history(currency: str, date: str) -> dict:
    """Fetch the buy/sell rate for a single currency on a specific date."""
    url = f"{API_BASE_URL}/rates/{currency}/history"
    response = requests.get(url, params={"from": date, "to": date, "limit": 1}, timeout=REQUEST_TIMEOUT)
    if response.status_code == 404:
        raise ZionApiError(f"Unknown currency '{currency}'")
    response.raise_for_status()
    data = response.json().get("data") or []
    if not data:
        raise ZionApiError(f"No historical rate for '{currency}' on {date}")
    return data[0]


def fetch_rates_by_currency_for_date(date: str, currencies: Iterable[str]) -> dict[str, dict]:
    """Fetch historical rates for a date and index them by currency code."""
    return {currency: fetch_rate_history(currency, date) for currency in currencies}
