from sqlalchemy import Column, Integer, String, BigInteger, Float, DateTime
from sqlalchemy.sql import func
from app.db import Base

class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(191), nullable=False, index=True, unique=True)
    capital = Column(String(191), nullable=True)
    region = Column(String(64), nullable=True)

    population = Column(BigInteger, nullable=False)

    currency_code = Column(String(16), nullable=True)       
    exchange_rate = Column(Float, nullable=True)            
    estimated_gdp = Column(Float, nullable=True)            
    
    flag_url = Column(String(512), nullable=True)

    last_refreshed_at = Column(DateTime(timezone=True), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
