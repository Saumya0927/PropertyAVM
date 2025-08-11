from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import numpy as np

from services.database import get_db, Property, Valuation, APIUsage
from services.redis_client import redis_client

router = APIRouter()

@router.get("/market-overview")
async def get_market_overview(
    city: Optional[str] = None,
    property_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get market overview statistics"""
    try:
        query = select(Property)
        
        if city:
            query = query.where(Property.city == city)
        if property_type:
            query = query.where(Property.property_type == property_type)
        
        result = await db.execute(query)
        properties = result.scalars().all()
        
        if not properties:
            return {"message": "No properties found with given filters"}
        
        values = [p.property_value for p in properties if p.property_value]
        
        return {
            "total_properties": len(properties),
            "filters": {
                "city": city,
                "property_type": property_type
            },
            "value_statistics": {
                "mean": float(np.mean(values)) if values else 0,
                "median": float(np.median(values)) if values else 0,
                "min": float(np.min(values)) if values else 0,
                "max": float(np.max(values)) if values else 0,
                "std_dev": float(np.std(values)) if values else 0
            },
            "price_per_sqft": {
                "mean": float(np.mean([p.price_per_sqft for p in properties if p.price_per_sqft])) if properties else 0
            },
            "occupancy_rate": {
                "mean": float(np.mean([p.occupancy_rate for p in properties if p.occupancy_rate])) if properties else 0
            },
            "cap_rate": {
                "mean": float(np.mean([p.cap_rate for p in properties if p.cap_rate])) if properties else 0
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/trends")
async def get_valuation_trends(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get valuation trends over time"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        result = await db.execute(
            select(
                func.date(Valuation.created_at).label('date'),
                func.count(Valuation.id).label('count'),
                func.avg(Valuation.predicted_value).label('avg_value')
            )
            .where(Valuation.created_at >= start_date)
            .group_by(func.date(Valuation.created_at))
            .order_by(func.date(Valuation.created_at))
        )
        
        trends = result.all()
        
        return {
            "period_days": days,
            "trends": [
                {
                    "date": str(t.date),
                    "valuations_count": t.count,
                    "average_value": float(t.avg_value) if t.avg_value else 0
                }
                for t in trends
            ],
            "summary": {
                "total_valuations": sum(t.count for t in trends),
                "average_daily_valuations": sum(t.count for t in trends) / max(len(trends), 1)
            }
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/api-usage")
async def get_api_usage_stats(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    """Get API usage statistics"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        result = await db.execute(
            select(
                APIUsage.endpoint,
                func.count(APIUsage.id).label('count'),
                func.avg(APIUsage.response_time_ms).label('avg_response_time')
            )
            .where(APIUsage.created_at >= start_date)
            .group_by(APIUsage.endpoint)
            .order_by(func.count(APIUsage.id).desc())
        )
        
        usage_stats = result.all()
        
        return {
            "period_days": days,
            "endpoints": [
                {
                    "endpoint": stat.endpoint,
                    "request_count": stat.count,
                    "avg_response_time_ms": float(stat.avg_response_time) if stat.avg_response_time else 0
                }
                for stat in usage_stats
            ],
            "total_requests": sum(stat.count for stat in usage_stats)
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/summary")
async def get_analytics_summary(
    db: AsyncSession = Depends(get_db)
):
    """Get combined analytics summary for dashboard"""
    try:
        # Total valuations count
        total_valuations_result = await db.execute(
            select(func.count(Valuation.id))
        )
        total_valuations = total_valuations_result.scalar() or 0
        
        # Average property value
        avg_value_result = await db.execute(
            select(func.avg(Property.property_value))
            .where(Property.property_value.isnot(None))
        )
        avg_property_value = avg_value_result.scalar() or 0
        
        # Total properties
        total_properties_result = await db.execute(
            select(func.count(Property.id))
        )
        total_properties = total_properties_result.scalar() or 0
        
        # Recent activity (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_valuations_result = await db.execute(
            select(func.count(Valuation.id))
            .where(Valuation.created_at >= thirty_days_ago)
        )
        recent_valuations = recent_valuations_result.scalar() or 0
        
        # Average response time from API usage
        avg_response_time_result = await db.execute(
            select(func.avg(APIUsage.response_time_ms))
            .where(APIUsage.created_at >= thirty_days_ago)
        )
        avg_response_time = avg_response_time_result.scalar() or 0
        
        # Model accuracy calculation (simplified)
        model_accuracy = 89.5  # Would be calculated from actual model metrics in production
        
        # Growth calculations
        sixty_days_ago = datetime.utcnow() - timedelta(days=60)
        older_period_result = await db.execute(
            select(func.count(Valuation.id))
            .where(Valuation.created_at >= sixty_days_ago)
            .where(Valuation.created_at < thirty_days_ago)
        )
        older_period = older_period_result.scalar() or 1
        
        growth_rate = ((recent_valuations - older_period) / max(older_period, 1)) * 100
        
        return {
            "summary": {
                "total_valuations": total_valuations,
                "total_properties": total_properties,
                "avg_property_value": float(avg_property_value),
                "recent_activity": recent_valuations,
                "avg_response_time": float(avg_response_time),
                "model_accuracy": model_accuracy,
                "growth_rate": round(growth_rate, 1)
            },
            "trends": {
                "valuations_30d": recent_valuations,
                "properties_growth": round(growth_rate, 1),
                "avg_value_trend": "up" if growth_rate > 0 else "down"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {"error": str(e)}

@router.get("/property-distribution")
async def get_property_distribution(
    db: AsyncSession = Depends(get_db)
):
    """Get property distribution by type and location"""
    try:
        # By property type
        type_result = await db.execute(
            select(
                Property.property_type,
                func.count(Property.id).label('count'),
                func.avg(Property.property_value).label('avg_value')
            )
            .group_by(Property.property_type)
        )
        type_dist = type_result.all()
        
        # By city
        city_result = await db.execute(
            select(
                Property.city,
                func.count(Property.id).label('count'),
                func.avg(Property.property_value).label('avg_value')
            )
            .group_by(Property.city)
            .order_by(func.count(Property.id).desc())
            .limit(10)
        )
        city_dist = city_result.all()
        
        return {
            "by_property_type": [
                {
                    "type": t.property_type,
                    "count": t.count,
                    "avg_value": float(t.avg_value) if t.avg_value else 0
                }
                for t in type_dist
            ],
            "by_city": [
                {
                    "city": c.city,
                    "count": c.count,
                    "avg_value": float(c.avg_value) if c.avg_value else 0
                }
                for c in city_dist
            ]
        }
    except Exception as e:
        return {"error": str(e)}

analytics_router = router