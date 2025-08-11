from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        request_body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                request_body = body.decode('utf-8') if body else None
                # Need to recreate the request with the body for downstream processing
                from starlette.datastructures import Headers
                from starlette.requests import Request as StarletteRequest
                
                async def receive():
                    return {"type": "http.request", "body": body}
                
                request = StarletteRequest(request.scope, receive)
            except:
                pass
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = (time.time() - start_time) * 1000
        
        # Log the request/response
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'method': request.method,
            'path': request.url.path,
            'query_params': dict(request.query_params),
            'status_code': response.status_code,
            'process_time_ms': round(process_time, 2),
            'client_host': request.client.host if request.client else None,
            'user_agent': request.headers.get('user-agent', '')
        }
        
        if request_body and len(request_body) < 1000:  # Don't log huge bodies
            try:
                log_data['request_body'] = json.loads(request_body)
            except:
                log_data['request_body'] = request_body[:100]
        
        # Log level based on status code
        if response.status_code >= 500:
            logger.error(json.dumps(log_data))
        elif response.status_code >= 400:
            logger.warning(json.dumps(log_data))
        else:
            logger.info(json.dumps(log_data))
        
        # Add custom headers
        response.headers["X-Process-Time"] = str(process_time)
        
        return response