"""Client for the Zion (zion.ar) public rates API."""

from __future__ import annotations

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
