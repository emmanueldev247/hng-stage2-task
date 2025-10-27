from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core import errors as err_handlers
from app.db import get_db
from app.models.country import Country
from app.models.meta import MetaCache
from app.routers.countries import router as countries_router
from app.schemas.status import StatusOut


app = FastAPI(
    title="HNG Stage 2 - Country Currency & Exchange API",
    version="1.0",
)

# error handlers
app.add_exception_handler(RequestValidationError, err_handlers.handle_validation_error)
app.add_exception_handler(StarletteHTTPException, err_handlers.handle_http_exception)
app.add_exception_handler(Exception, err_handlers.handle_unexpected_error)

# routers
app.include_router(countries_router)

@app.get("/", tags=["meta"])
async def root():
    return {"service": "stage2-api", "version": "1.0"}

@app.get("/healthz", tags=["meta"])
async def healthz():
    return {"status": "ok"}

@app.get("/status", response_model=StatusOut, tags=["meta"])
async def status(db: Session = Depends(get_db)):
    total = db.scalar(select(func.count()).select_from(Country)) or 0
    meta = db.scalar(select(MetaCache).where(MetaCache.id == 1))
    last_ts = meta.last_refreshed_at if meta else None
    return StatusOut(total_countries=total, last_refreshed_at=last_ts)
