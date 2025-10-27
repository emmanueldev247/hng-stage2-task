from typing import Dict, Any, Optional
from random import randint
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.clients.external import fetch_countries_and_rates, ExternalClientError
from app.models.country import Country
from app.models.meta import MetaCache
from app.services.image import generate_summary_image
from app.utils.text import normalize_key


def _extract_currency_code(country: Dict[str, Any]) -> Optional[str]:
    """Extract the first currency code from the country payload"""
    currencies = country.get("currencies")
    if not isinstance(currencies, list) or not currencies:
        return None
    first = currencies[0] or {}
    code = first.get("code")
    if code and isinstance(code, str) and code.strip():
        return code.strip().upper()
    return None

def _safe_float(val) -> Optional[float]:
    try:
        if val is None:
            return None
        return float(val)
    except Exception:
        return None

async def run_refresh(db: Session) -> Dict[str, Any]:
    """
    Full refresh:
      - Fetch countries + rates
      - Upsert rows (match by name, case-insensitive)
      - Compute estimated_gdp per rules
      - Update global last_refreshed_at
      - Generate summary image
      - All DB writes happen only if both external fetches succeeded
    """
    # External fetches
    try:
        countries_payload, rates_map = await fetch_countries_and_rates()
    except ExternalClientError as e:
        return {"ok": False, "error": str(e), "source": "external"}

    now = datetime.now(timezone.utc)

    # Transactional upsert
    inserted = 0
    updated = 0

    with db.begin():
        existing_by_key = {
            (nk or ""): id_
            for (id_, nk) in db.execute(select(Country.id, Country.name_key)).all()
        }

        for c in countries_payload:
            name = (c.get("name") or "").strip()
            if not name:
                continue

            name_key = normalize_key(name)
            if not name_key:
                continue

            capital = (c.get("capital") or None)
            region = (c.get("region") or None)
            population = c.get("population")
            population = int(population or 0)
            flag_url = c.get("flag") or None

            currency_code = _extract_currency_code(c)
            exchange_rate = None
            estimated_gdp = None

            if currency_code is None:
                exchange_rate = None
                estimated_gdp = 0.0
            else:
                rate = rates_map.get(currency_code)
                if rate is None or _safe_float(rate) in (None, 0.0):
                    exchange_rate = None
                    estimated_gdp = None
                else:
                    exchange_rate = float(rate)
                    multiplier = randint(1000, 2000)
                    estimated_gdp = (population * multiplier) / exchange_rate if exchange_rate else None

            if name_key in existing_by_key:
                country_row: Country = db.scalar(
                    select(Country).where(Country.name_key == name_key)
                )
                if country_row:
                    country_row.name = name
                    country_row.name_key = name_key
                    country_row.capital = capital
                    country_row.region = region
                    country_row.population = population
                    country_row.currency_code = currency_code
                    country_row.exchange_rate = exchange_rate
                    country_row.estimated_gdp = estimated_gdp
                    country_row.flag_url = flag_url
                    country_row.last_refreshed_at = now
                    updated += 1
            else:
                new_row = Country(
                    name=name,
                    name_key=name_key,
                    capital=capital,
                    region=region,
                    population=population,
                    currency_code=currency_code,
                    exchange_rate=exchange_rate,
                    estimated_gdp=estimated_gdp,
                    flag_url=flag_url,
                    last_refreshed_at=now,
                )
                db.add(new_row)
                inserted += 1

        meta = db.scalar(select(MetaCache).where(MetaCache.id == 1))
        if not meta:
            meta = MetaCache(id=1, last_refreshed_at=now)
            db.add(meta)
        else:
            meta.last_refreshed_at = now

    top5 = db.execute(
        select(Country.name, Country.estimated_gdp)
        .where(Country.estimated_gdp.isnot(None))
        .order_by(Country.estimated_gdp.desc())
        .limit(5)
    ).all()
    top5_list = [(name, float(gdp)) for name, gdp in top5 if gdp is not None]

    total = db.scalar(select(func.count()).select_from(Country)) or 0
    generate_summary_image(total=total, top5=top5_list, ts=now)

    return {
        "ok": True,
        "inserted": inserted,
        "updated": updated,
        "total": total,
        "refreshed_at": now,
    }
