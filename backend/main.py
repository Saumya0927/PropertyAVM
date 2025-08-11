from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
from typing import List, Optional
import asyncio
from datetime import datetime
import json

from api.auth import auth_router
from api.valuations import valuations_router
from api.models import models_router
from api.properties import properties_router
from api.analytics import analytics_router
from api.monitoring import monitoring_router
from services.database import init_db, get_db
from services.redis_client import redis_client
from services.ml_service import MLService
from services.websocket_manager import WebSocketManager
from middleware.logging import LoggingMiddleware
from middleware.metrics import MetricsMiddleware
from prometheus_client import make_asgi_app

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting AVM Backend Server...")
    await init_db()
    await redis_client.initialize()
    ml_service = MLService()
    await ml_service.load_models()
    app.state.ml_service = ml_service
    app.state.ws_manager = WebSocketManager()
    
    yield
    
    print("Shutting down AVM Backend Server...")
    await redis_client.close()

app = FastAPI(
    title="Property Valuation Model API",
    description="Advanced ML-powered commercial real estate valuation platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(MetricsMiddleware)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(valuations_router, prefix="/api/v1/valuations", tags=["Valuations"])
app.include_router(models_router, prefix="/api/v1/models", tags=["ML Models"])
app.include_router(properties_router, prefix="/api/v1/properties", tags=["Properties"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(monitoring_router, prefix="/api/v1/monitoring", tags=["Monitoring"])

@app.get("/")
async def root():
    return {
        "name": "Property Valuation Model API",
        "status": "operational",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "metrics": "/metrics"
        }
    }

@app.get("/health")
async def health_check():
    try:
        db_status = await check_database_health()
        redis_status = await redis_client.ping()
        ml_status = app.state.ml_service.is_ready if hasattr(app.state, 'ml_service') else False
        
        health_status = {
            "status": "healthy" if all([db_status, redis_status, ml_status]) else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": "healthy" if db_status else "unhealthy",
                "redis": "healthy" if redis_status else "unhealthy",
                "ml_models": "healthy" if ml_status else "unhealthy"
            }
        }
        
        status_code = 200 if health_status["status"] == "healthy" else 503
        return JSONResponse(content=health_status, status_code=status_code)
    except Exception as e:
        return JSONResponse(
            content={"status": "unhealthy", "error": str(e)},
            status_code=503
        )

async def check_database_health():
    try:
        from services.database import engine
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except:
        return False

@app.websocket("/ws/valuations")
async def websocket_valuations(websocket: WebSocket):
    await app.state.ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "valuation_request":
                property_data = message["data"]
                
                valuation_result = await app.state.ml_service.predict_with_confidence(
                    property_data
                )
                
                await app.state.ws_manager.send_personal_message(
                    json.dumps({
                        "type": "valuation_result",
                        "data": valuation_result
                    }),
                    websocket
                )
                
                await app.state.ws_manager.broadcast(
                    json.dumps({
                        "type": "market_update",
                        "data": {
                            "timestamp": datetime.utcnow().isoformat(),
                            "active_valuations": app.state.ws_manager.active_connections_count()
                        }
                    })
                )
    except WebSocketDisconnect:
        app.state.ws_manager.disconnect(websocket)
        await app.state.ws_manager.broadcast(
            json.dumps({
                "type": "connection_update",
                "data": {
                    "active_connections": app.state.ws_manager.active_connections_count()
                }
            })
        )

@app.on_event("startup")
async def startup_event():
    print("AVM API Server is ready!")
    print(f"Documentation available at: http://localhost:8000/docs")
    print(f"WebSocket endpoint: ws://localhost:8000/ws/valuations")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )