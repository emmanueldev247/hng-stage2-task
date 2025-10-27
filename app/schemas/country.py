from datetime import datetime, timezone
from pydantic import BaseModel, field_serializer, ConfigDict

class CountryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    capital: str | None
    region: str | None
    population: int
    currency_code: str | None
    exchange_rate: float | None
    estimated_gdp: float | None
    flag_url: str | None
    last_refreshed_at: datetime | None

    @field_serializer("last_refreshed_at", when_used="json")
    def _ser_z(self, v: datetime | None):
        if v is None:
            return None
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        else:
            v = v.astimezone(timezone.utc)
        return v.strftime("%Y-%m-%dT%H:%M:%SZ")
