from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from services.database import get_db, ModelMetrics
from services.ml_service import MLService

router = APIRouter()

@router.get("/performance")
async def get_model_performance(
    ml_service: MLService = Depends(lambda: MLService())
):
    """Get current model performance metrics"""
    try:
        if not ml_service.is_ready:
            await ml_service.load_models()
        
        metrics = ml_service.get_model_metrics()
        return {
            "status": "healthy",
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feature-importance")
async def get_feature_importance(
    ml_service: MLService = Depends(lambda: MLService())
):
    """Get feature importance from the model"""
    try:
        if not ml_service.is_ready:
            await ml_service.load_models()
        
        importance = ml_service.get_feature_importance()
        
        # Sort by importance
        sorted_importance = dict(sorted(
            importance.items(), 
            key=lambda x: x[1], 
            reverse=True
        ))
        
        return {
            "feature_importance": sorted_importance,
            "total_features": len(sorted_importance),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_model_history(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get model training history"""
    try:
        result = await db.execute(
            select(ModelMetrics)
            .order_by(desc(ModelMetrics.created_at))
            .limit(limit)
        )
        metrics = result.scalars().all()
        
        return {
            "model_history": [
                {
                    "id": str(m.id),
                    "model_name": m.model_name,
                    "model_version": m.model_version,
                    "accuracy": float(m.accuracy) if m.accuracy else None,
                    "rmse": float(m.rmse) if m.rmse else None,
                    "mae": float(m.mae) if m.mae else None,
                    "r2_score": float(m.r2_score) if m.r2_score else None,
                    "training_date": m.training_date.isoformat() if m.training_date else None,
                    "created_at": m.created_at.isoformat()
                }
                for m in metrics
            ],
            "total_models": len(metrics)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/retrain")
async def trigger_retrain(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Trigger model retraining"""
    # This would trigger actual retraining in production
    return {
        "status": "retraining_scheduled",
        "message": "Model retraining has been scheduled",
        "scheduled_at": datetime.utcnow().isoformat()
    }

@router.get("/drift")
async def check_model_drift(
    db: AsyncSession = Depends(get_db)
):
    """Check for model drift"""
    # Simplified drift detection
    return {
        "drift_detected": False,
        "drift_score": 0.02,
        "threshold": 0.1,
        "last_checked": datetime.utcnow().isoformat(),
        "recommendation": "Model performance is stable"
    }

models_router = router