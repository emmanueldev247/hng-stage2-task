from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from typing import Optional, Literal, List

from app.db import get_db
from app.models.country import Country
from app.schemas.country import CountryOut
from app.services.image import SUMMARY_PATH
from app.services.refresh import run_refresh

router = APIRouter(prefix="/countries", tags=["countries"])

@router.post("/refresh")
async def refresh_countries(db: Session = Depends(get_db)):
    result = await run_refresh(db)
    if not result.get("ok"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": "External data source unavailable", "details": result.get("error")},
        )
    # short summary
    return {
        "inserted": result["inserted"],
        "updated": result["updated"],
        "total": result["total"],
        "last_refreshed_at": result["refreshed_at"].strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

@router.get("/image")
async def get_summary_image():
    if not SUMMARY_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail={"error": "Summary image not found"},
        )
    return FileResponse(path=str(SUMMARY_PATH), media_type="image/png", filename="summary.png")

@router.get("", response_model=List[CountryOut])
def list_countries(
    region: Optional[str] = Query(default=None),
    currency: Optional[str] = Query(default=None),
    sort: Optional[Literal["gdp_desc", "gdp_asc", "name_asc", "name_desc"]] = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(Country)

    if region:
        stmt = stmt.where(func.lower(Country.region) == region.lower())

    if currency:
        stmt = stmt.where(func.upper(Country.currency_code) == currency.upper())

    if sort:
        if sort == "gdp_desc":
            stmt = stmt.order_by(Country.estimated_gdp.is_(None), Country.estimated_gdp.desc())
        elif sort == "gdp_asc":
            stmt = stmt.order_by(Country.estimated_gdp.is_(None), Country.estimated_gdp.asc())
        elif sort == "name_asc":
            stmt = stmt.order_by(func.lower(Country.name).asc())
        elif sort == "name_desc":
            stmt = stmt.order_by(func.lower(Country.name).desc())

    rows = db.execute(stmt).scalars().all()
    return [CountryOut.model_validate(r) for r in rows]

@router.get("/{name}", response_model=CountryOut)
def get_country(name: str, db: Session = Depends(get_db)):
    row = db.scalar(select(Country).where(func.lower(Country.name) == name.lower()))
    if not row:
        raise HTTPException(status_code=404, detail={"error": "Country not found"})
    return CountryOut.model_validate(row)

@router.delete("/{name}", status_code=204)
def delete_country(name: str, db: Session = Depends(get_db)):
    row = db.scalar(select(Country).where(func.lower(Country.name) == name.lower()))
    if not row:
        raise HTTPException(status_code=404, detail={"error": "Country not found"})
    db.delete(row)
    db.commit()
    return
