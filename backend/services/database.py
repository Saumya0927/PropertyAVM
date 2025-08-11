from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import os
import uuid

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://avm_user:avm_secure_pass_2024@postgres:5432/property_valuation')

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class Property(Base):
    __tablename__ = "properties"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(String(50), unique=True, nullable=False)
    property_type = Column(String(50), nullable=False)
    property_class = Column(String(10))
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    year_built = Column(Integer)
    building_age = Column(Integer)
    square_feet = Column(Integer, nullable=False)
    lot_size = Column(Float)
    num_floors = Column(Integer)
    num_units = Column(Integer)
    parking_spots = Column(Integer)
    occupancy_rate = Column(Float)
    annual_revenue = Column(Float)
    annual_expenses = Column(Float)
    net_operating_income = Column(Float)
    cap_rate = Column(Float)
    distance_to_downtown = Column(Float)
    distance_to_highway = Column(Float)
    distance_to_public_transit = Column(Float)
    walk_score = Column(Integer)
    transit_score = Column(Integer)
    crime_rate = Column(Float)
    school_rating = Column(Float)
    property_value = Column(Float)
    price_per_sqft = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Valuation(Base):
    __tablename__ = "valuations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(String(50), ForeignKey('properties.property_id'), nullable=False)
    predicted_value = Column(Float, nullable=False)
    confidence_lower = Column(Float)
    confidence_upper = Column(Float)
    confidence_level = Column(Float, default=95.0)
    model_version = Column(String(50))
    model_type = Column(String(50))
    prediction_metadata = Column(JSON)
    shap_values = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100))

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

class ModelMetrics(Base):
    __tablename__ = "model_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50))
    accuracy = Column(Float)
    rmse = Column(Float)
    mae = Column(Float)
    r2_score = Column(Float)
    mape = Column(Float)
    within_5_percent = Column(Float)
    within_10_percent = Column(Float)
    training_date = Column(DateTime)
    training_samples = Column(Integer)
    validation_samples = Column(Integer)
    test_samples = Column(Integer)
    feature_count = Column(Integer)
    hyperparameters = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class APIUsage(Base):
    __tablename__ = "api_usage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    endpoint = Column(String(255))
    method = Column(String(10))
    status_code = Column(Integer)
    response_time_ms = Column(Integer)
    request_body = Column(JSON)
    response_summary = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()