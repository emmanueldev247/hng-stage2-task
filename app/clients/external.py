import httpx
from typing import Tuple, Dict, Any, List
from app.core.config import settings

class ExternalClientError(Exception):
    pass

async def fetch_countries_and_rates() -> Tuple[List[Dict[str, Any]], Dict[str, float]]:
    timeout = httpx.Timeout(settings.EXTERNAL_TIMEOUT)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            countries_resp = await client.get(settings.EXTERNAL_COUNTRIES_URL)
            countries_resp.raise_for_status()
        except Exception as e:
            raise ExternalClientError(f"Could not fetch data from restcountries")

        try:
            rates_resp = await client.get(settings.EXTERNAL_RATES_URL)
            rates_resp.raise_for_status()
        except Exception as e:
            raise ExternalClientError(f"Could not fetch data from open.er-api")

    countries = countries_resp.json()
    rates_payload = rates_resp.json()
    rates_map = rates_payload.get("rates") or {}
    if not isinstance(rates_map, dict):
        rates_map = {}

    rates: Dict[str, float] = {}
    for code, val in rates_map.items():
        try:
            rates[code] = float(val)
        except Exception:
            continue

    if not isinstance(countries, list):
        countries = []

    return countries, rates
