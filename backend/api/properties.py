from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime

from services.database import get_db, Property

router = APIRouter()

class PropertyResponse(BaseModel):
    id: str
    property_id: str
    property_type: str
    city: str
    state: str
    square_feet: int
    property_value: Optional[float]
    price_per_sqft: Optional[float]
    occupancy_rate: Optional[float]
    cap_rate: Optional[float]
    created_at: datetime

@router.get("/", response_model=List[PropertyResponse])
async def list_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    property_type: Optional[str] = None,
    city: Optional[str] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    db: AsyncSession = Depends(get_db)
):
    """List properties with filters"""
    try:
        query = select(Property)
        
        # Apply filters
        filters = []
        if property_type:
            filters.append(Property.property_type == property_type)
        if city:
            filters.append(Property.city == city)
        if min_value:
            filters.append(Property.property_value >= min_value)
        if max_value:
            filters.append(Property.property_value <= max_value)
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        properties = result.scalars().all()
        
        return [
            PropertyResponse(
                id=str(p.id),
                property_id=p.property_id,
                property_type=p.property_type,
                city=p.city,
                state=p.state,
                square_feet=p.square_feet,
                property_value=p.property_value,
                price_per_sqft=p.price_per_sqft,
                occupancy_rate=p.occupancy_rate,
                cap_rate=p.cap_rate,
                created_at=p.created_at
            )
            for p in properties
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{property_id}")
async def get_property(
    property_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get property details"""
    try:
        result = await db.execute(
            select(Property).where(Property.property_id == property_id)
        )
        property_data = result.scalar_one_or_none()
        
        if not property_data:
            raise HTTPException(status_code=404, detail="Property not found")
        
        return {
            "id": str(property_data.id),
            "property_id": property_data.property_id,
            "property_type": property_data.property_type,
            "property_class": property_data.property_class,
            "city": property_data.city,
            "state": property_data.state,
            "latitude": property_data.latitude,
            "longitude": property_data.longitude,
            "year_built": property_data.year_built,
            "building_age": property_data.building_age,
            "square_feet": property_data.square_feet,
            "lot_size": property_data.lot_size,
            "num_floors": property_data.num_floors,
            "num_units": property_data.num_units,
            "parking_spots": property_data.parking_spots,
            "occupancy_rate": property_data.occupancy_rate,
            "annual_revenue": property_data.annual_revenue,
            "annual_expenses": property_data.annual_expenses,
            "net_operating_income": property_data.net_operating_income,
            "cap_rate": property_data.cap_rate,
            "distance_to_downtown": property_data.distance_to_downtown,
            "walk_score": property_data.walk_score,
            "transit_score": property_data.transit_score,
            "property_value": property_data.property_value,
            "price_per_sqft": property_data.price_per_sqft,
            "created_at": property_data.created_at.isoformat(),
            "updated_at": property_data.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/similar")
async def find_similar_properties(
    property_id: str,
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Find similar properties based on characteristics"""
    try:
        # Get reference property
        result = await db.execute(
            select(Property).where(Property.property_id == property_id)
        )
        reference = result.scalar_one_or_none()
        
        if not reference:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Find similar properties (simplified)
        query = select(Property).where(
            and_(
                Property.property_id != property_id,
                Property.property_type == reference.property_type,
                Property.square_feet.between(
                    reference.square_feet * 0.8,
                    reference.square_feet * 1.2
                )
            )
        ).limit(limit)
        
        result = await db.execute(query)
        similar = result.scalars().all()
        
        return {
            "reference_property": property_id,
            "similar_properties": [
                {
                    "property_id": p.property_id,
                    "similarity_score": 0.85,  # Simplified
                    "property_type": p.property_type,
                    "city": p.city,
                    "square_feet": p.square_feet,
                    "property_value": p.property_value
                }
                for p in similar
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

properties_router = router