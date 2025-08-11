from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from prometheus_client import Counter, Histogram, Gauge
import time

# Prometheus metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests in progress'
)

model_predictions_total = Counter(
    'model_predictions_total',
    'Total model predictions made',
    ['model_version', 'status']
)

valuation_values = Histogram(
    'valuation_values',
    'Distribution of property valuation values',
    buckets=(100000, 250000, 500000, 750000, 1000000, 2000000, 5000000, 10000000, float('inf'))
)

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Track in-progress requests
        http_requests_in_progress.inc()
        
        # Start timing
        start_time = time.time()
        
        # Get endpoint path (remove query params and path params)
        path = request.url.path
        if path.startswith('/api/v1/'):
            # Normalize paths with IDs
            path_parts = path.split('/')
            normalized_parts = []
            for part in path_parts:
                # Replace UUIDs and numeric IDs with placeholder
                if len(part) == 36 and '-' in part:  # Likely a UUID
                    normalized_parts.append('{id}')
                elif part.isdigit():  # Numeric ID
                    normalized_parts.append('{id}')
                else:
                    normalized_parts.append(part)
            endpoint = '/'.join(normalized_parts)
        else:
            endpoint = path
        
        try:
            # Process request
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)
            
            http_requests_total.labels(
                method=request.method,
                endpoint=endpoint,
                status=response.status_code
            ).inc()
            
            # Track specific endpoints
            if endpoint == '/api/v1/valuations/predict' and response.status_code == 200:
                model_predictions_total.labels(
                    model_version='v1.0.0',
                    status='success'
                ).inc()
            
            return response
            
        except Exception as e:
            # Record error metrics
            http_requests_total.labels(
                method=request.method,
                endpoint=endpoint,
                status=500
            ).inc()
            raise e
            
        finally:
            # Decrement in-progress counter
            http_requests_in_progress.dec()