from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True, nullable=True)
    title = Column(String, index=True, nullable=False)
    price = Column(Integer, nullable=False)
    location = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    brand = Column(String, nullable=True)
    model = Column(String, nullable=True)
    url = Column(String, nullable=False)
    image_url = Column(Text, nullable=True)
    source = Column(String, default="marketplace")
    
    score = Column(String, default="ROJO") # VERDE, AMARILLO, ROJO, INVALIDO
    estimated_market_price = Column(Integer, default=0)
    mechanical_cushion = Column(Integer, default=500000)
    transfer_tax = Column(Integer, default=0)
    calculated_roi = Column(Float, default=0.0) # ROI %
    calculated_margin = Column(Integer, default=0) # Margin in CLP

    # Mercado Chileautos
    score_chileautos = Column(String, default="PENDIENTE")
    estimated_market_price_chileautos = Column(Integer, default=0)
    transfer_tax_chileautos = Column(Integer, default=0)
    margin_chileautos = Column(Integer, default=0)
    samples_count_chileautos = Column(Integer, default=0)
    min_price_chileautos = Column(Integer, default=0)
    max_price_chileautos = Column(Integer, default=0)
    avg_price_chileautos = Column(Integer, default=0)

    # Mercado Facebook Marketplace
    score_mp = Column(String, default="PENDIENTE")
    estimated_market_price_mp = Column(Integer, default=0)
    transfer_tax_mp = Column(Integer, default=0)
    margin_mp = Column(Integer, default=0)
    samples_count_mp = Column(Integer, default=0)
    min_price_mp = Column(Integer, default=0)
    max_price_mp = Column(Integer, default=0)
    avg_price_mp = Column(Integer, default=0)
    
    discarded_reason = Column(String, nullable=True)
    raw_description = Column(Text, nullable=True)
    
    is_approved_for_export = Column(Boolean, default=False)
    exported_to_sheets = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class SentinelConfig(Base):
    __tablename__ = "sentinel_config"

    id = Column(Integer, primary_key=True, index=True)
    search_query = Column(String, default="autos")
    max_budget = Column(Integer, default=20000000)
    min_budget = Column(Integer, default=500000)
    locations = Column(String, default="Valparaíso, Región Metropolitana")
    interval_hours = Column(Integer, default=3)
    mechanical_cushion_default = Column(Integer, default=500000)
    transfer_tax_percent = Column(Float, default=1.5)
    
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)

class FilterKeyword(Base):
    __tablename__ = "filter_keywords"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, default="general") # prenda, choque, documento, fallas
    is_active = Column(Boolean, default=True)
