from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.core import CollectorRegistry
from prometheus_client.multiprocess import MultiProcessCollector
import time
from functools import wraps
from fastapi import Request, Response
from typing import Callable

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

GPT_REQUESTS = Counter(
    'gpt_requests_total',
    'Total GPT API requests',
    ['status']  # success, error
)

TELEGRAM_MESSAGES = Counter(
    'telegram_messages_total',
    'Total Telegram messages processed',
    ['type']  # received, sent
)

class PrometheusMetrics:
    def __init__(self):
        self.REQUEST_COUNT = REQUEST_COUNT
        self.REQUEST_DURATION = REQUEST_DURATION
        self.GPT_REQUESTS = GPT_REQUESTS
        self.TELEGRAM_MESSAGES = TELEGRAM_MESSAGES
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Записываем метрики HTTP запроса"""
        self.REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
        
        self.REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def record_gpt_request(self, success: bool):
        """Записываем метрики GPT запроса"""
        status = "success" if success else "error"
        self.GPT_REQUESTS.labels(status=status).inc()
    
    def record_telegram_message(self, message_type: str):
        """Записываем метрики Telegram сообщений"""
        self.TELEGRAM_MESSAGES.labels(type=message_type).inc()

metrics = PrometheusMetrics()

def metrics_middleware():
    """Middleware для автоматического сбора метрик HTTP запросов"""
    async def middleware(request: Request, call_next: Callable):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        endpoint = request.url.path
        method = request.method
        status_code = response.status_code
        
        metrics.record_request(method, endpoint, status_code, duration)
        
        return response
    
    return middleware

def get_metrics():
    """Возвращает метрики в формате Prometheus"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
