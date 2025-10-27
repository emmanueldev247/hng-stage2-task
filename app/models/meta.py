from sqlalchemy import Column, Integer, DateTime
from app.db import Base

class MetaCache(Base):
    """Single-row table storing global metadata for the cache."""
    __tablename__ = "meta_cache"

    id = Column(Integer, primary_key=True, autoincrement=False, default=1)
    last_refreshed_at = Column(DateTime(timezone=True), nullable=True)
