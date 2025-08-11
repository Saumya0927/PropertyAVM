from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import hashlib
import json

from services.database import get_db, Valuation, Property
from services.redis_client import redis_client
from services.ml_service import MLService

router = APIRouter()

class PropertyValuationRequest(BaseModel):
    property_id: Optional[str] = Field(None, description="Unique property identifier")
    property_type: str = Field(..., description="Type of property (Office, Retail, etc.)")
    city: str = Field(..., description="Property city")
    state: Optional[str] = Field("CA", description="Property state")
    square_feet: int = Field(..., ge=100, description="Total square footage")
    num_floors: Optional[int] = Field(1, ge=1, description="Number of floors")
    num_units: Optional[int] = Field(1, ge=1, description="Number of units")
    parking_spots: Optional[int] = Field(0, ge=0, description="Number of parking spots")
    occupancy_rate: float = Field(..., ge=0, le=1, description="Occupancy rate (0-1)")
    annual_revenue: float = Field(..., ge=0, description="Annual revenue")
    annual_expenses: float = Field(..., ge=0, description="Annual expenses")
    net_operating_income: float = Field(..., ge=0, description="Net operating income")
    cap_rate: float = Field(..., gt=0, le=1, description="Capitalization rate")
    walk_score: Optional[int] = Field(50, ge=0, le=100, description="Walk score")
    transit_score: Optional[int] = Field(50, ge=0, le=100, description="Transit score")
    building_age: Optional[int] = Field(10, ge=0, description="Building age in years")
    distance_to_downtown: Optional[float] = Field(5.0, ge=0, description="Distance to downtown (miles)")
    distance_to_highway: Optional[float] = Field(2.0, ge=0, description="Distance to highway (miles)")
    distance_to_public_transit: Optional[float] = Field(1.0, ge=0, description="Distance to public transit (miles)")
    crime_rate: Optional[float] = Field(50.0, ge=0, description="Crime rate index")
    school_rating: Optional[float] = Field(7.0, ge=0, le=10, description="School rating (0-10)")

class ValuationResponse(BaseModel):
    property_id: Optional[str]
    predicted_value: float
    confidence_interval: Dict[str, float]
    price_per_sqft: float
    valuation_date: str
    model_version: str
    processing_time_ms: Optional[float]
    cached: bool = False

class BatchValuationRequest(BaseModel):
    properties: List[PropertyValuationRequest]

class BatchValuationResponse(BaseModel):
    batch_id: str
    total_properties: int
    successful_valuations: int
    failed_valuations: int
    total_portfolio_value: float
    average_property_value: float
    results: List[Dict]
    processing_time_ms: float

@router.post("/predict", response_model=ValuationResponse)
async def predict_valuation(
    request: PropertyValuationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    ml_service: MLService = Depends(lambda: MLService())
):
    """
    Predict property valuation using ensemble ML model
    """
    start_time = datetime.utcnow()
    
    try:
        # Generate cache key
        request_dict = request.dict()
        cache_key = hashlib.md5(json.dumps(request_dict, sort_keys=True).encode()).hexdigest()
        
        # Check cache
        cached_result = await redis_client.get_cached_valuation(cache_key)
        if cached_result:
            cached_result['cached'] = True
            cached_result['processing_time_ms'] = (datetime.utcnow() - start_time).total_seconds() * 1000
            return ValuationResponse(**cached_result)
        
        # Ensure ML service is ready
        if not ml_service.is_ready:
            await ml_service.load_models()
        
        # Make prediction
        prediction = await ml_service.predict_with_confidence(request_dict)
        
        # Prepare response
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        response = ValuationResponse(
            property_id=request.property_id,
            predicted_value=prediction['predicted_value'],
            confidence_interval=prediction['confidence_interval'],
            price_per_sqft=prediction['price_per_sqft'],
            valuation_date=datetime.utcnow().isoformat(),
            model_version=prediction.get('model_version', 'v1.0.0'),
            processing_time_ms=processing_time,
            cached=False
        )
        
        # Cache the result
        await redis_client.cache_valuation(cache_key, response.dict(), ttl=3600)
        
        # Save to database in background
        background_tasks.add_task(
            save_valuation_to_db,
            db,
            request.property_id,
            prediction,
            request_dict
        )
        
        # Track API usage
        await redis_client.track_api_call('/api/v1/valuations/predict')
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch", response_model=BatchValuationResponse)
async def batch_valuation(
    request: BatchValuationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    ml_service: MLService = Depends(lambda: MLService())
):
    """
    Process batch property valuations
    """
    start_time = datetime.utcnow()
    batch_id = f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Ensure ML service is ready
        if not ml_service.is_ready:
            await ml_service.load_models()
        
        results = []
        total_value = 0
        successful = 0
        
        for property_data in request.properties:
            try:
                prediction = await ml_service.predict_with_confidence(property_data.dict())
                
                result = {
                    'property_id': property_data.property_id,
                    'status': 'success',
                    'valuation': {
                        'predicted_value': prediction['predicted_value'],
                        'confidence_interval': prediction['confidence_interval'],
                        'price_per_sqft': prediction['price_per_sqft']
                    }
                }
                
                total_value += prediction['predicted_value']
                successful += 1
                results.append(result)
                
            except Exception as e:
                results.append({
                    'property_id': property_data.property_id,
                    'status': 'error',
                    'error': str(e)
                })
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        response = BatchValuationResponse(
            batch_id=batch_id,
            total_properties=len(request.properties),
            successful_valuations=successful,
            failed_valuations=len(request.properties) - successful,
            total_portfolio_value=total_value,
            average_property_value=total_value / max(successful, 1),
            results=results,
            processing_time_ms=processing_time
        )
        
        # Track API usage
        await redis_client.track_api_call('/api/v1/valuations/batch')
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{valuation_id}/explain")
async def explain_valuation(
    valuation_id: str,
    db: AsyncSession = Depends(get_db),
    ml_service: MLService = Depends(lambda: MLService())
):
    """
    Get SHAP explanation for a valuation
    """
    try:
        # Get valuation from database
        result = await db.execute(
            select(Valuation).where(Valuation.id == valuation_id)
        )
        valuation = result.scalar_one_or_none()
        
        if not valuation:
            raise HTTPException(status_code=404, detail="Valuation not found")
        
        # Get property data
        property_result = await db.execute(
            select(Property).where(Property.property_id == valuation.property_id)
        )
        property_data = property_result.scalar_one_or_none()
        
        if not property_data:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Get SHAP values
        shap_explanation = await ml_service.get_shap_values(property_data.__dict__)
        
        return {
            'valuation_id': str(valuation_id),
            'property_id': valuation.property_id,
            'predicted_value': float(valuation.predicted_value),
            'explanation': shap_explanation,
            'feature_importance': ml_service.get_feature_importance()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent")
async def get_recent_valuations(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent valuations across all properties
    """
    try:
        result = await db.execute(
            select(Valuation, Property)
            .join(Property, Valuation.property_id == Property.property_id)
            .order_by(Valuation.created_at.desc())
            .limit(limit)
        )
        valuations_with_properties = result.all()
        
        return {
            'recent_valuations': [
                {
                    'id': str(v.Valuation.id),
                    'property_id': v.Valuation.property_id,
                    'predicted_value': float(v.Valuation.predicted_value),
                    'confidence_lower': float(v.Valuation.confidence_lower) if v.Valuation.confidence_lower else None,
                    'confidence_upper': float(v.Valuation.confidence_upper) if v.Valuation.confidence_upper else None,
                    'price_per_sqft': round(float(v.Valuation.predicted_value) / v.Property.square_feet, 2) if v.Property.square_feet else None,
                    'model_version': v.Valuation.model_version,
                    'created_at': v.Valuation.created_at.isoformat(),
                    'property': {
                        'property_type': v.Property.property_type,
                        'city': v.Property.city,
                        'state': v.Property.state,
                        'square_feet': v.Property.square_feet,
                        'year_built': v.Property.year_built
                    }
                }
                for v in valuations_with_properties
            ],
            'total_count': len(valuations_with_properties),
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{property_id}")
async def get_valuation_history(
    property_id: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get valuation history for a property
    """
    try:
        result = await db.execute(
            select(Valuation)
            .where(Valuation.property_id == property_id)
            .order_by(Valuation.created_at.desc())
            .limit(limit)
        )
        valuations = result.scalars().all()
        
        return {
            'property_id': property_id,
            'valuations': [
                {
                    'id': str(v.id),
                    'predicted_value': float(v.predicted_value),
                    'confidence_lower': float(v.confidence_lower) if v.confidence_lower else None,
                    'confidence_upper': float(v.confidence_upper) if v.confidence_upper else None,
                    'model_version': v.model_version,
                    'created_at': v.created_at.isoformat()
                }
                for v in valuations
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def save_valuation_to_db(
    db: AsyncSession,
    property_id: Optional[str],
    prediction: Dict,
    property_data: Dict
):
    """
    Save valuation to database (background task)
    """
    try:
        if property_id:
            # Check if property exists
            result = await db.execute(
                select(Property).where(Property.property_id == property_id)
            )
            existing_property = result.scalar_one_or_none()
            
            if not existing_property:
                # Create property record
                new_property = Property(
                    property_id=property_id,
                    **{k: v for k, v in property_data.items() if k != 'property_id' and hasattr(Property, k)}
                )
                db.add(new_property)
            
            # Create valuation record
            new_valuation = Valuation(
                property_id=property_id,
                predicted_value=prediction['predicted_value'],
                confidence_lower=prediction['confidence_interval']['lower'],
                confidence_upper=prediction['confidence_interval']['upper'],
                model_version=prediction.get('model_version', 'v1.0.0'),
                model_type='ensemble',
                prediction_metadata=prediction
            )
            db.add(new_valuation)
            
            await db.commit()
    except Exception as e:
        print(f"Error saving valuation to database: {e}")
        await db.rollback()

valuations_router = router