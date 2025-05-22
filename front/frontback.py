
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx
from fastapi.staticfiles import StaticFiles
import os
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time

app = FastAPI()

REQUEST_COUNT = Counter(
    'app_request_count', 
    'Application Request Count',
    ['endpoint', 'method', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds', 
    'Application Request Latency',
    ['endpoint', 'method']
)
BACKEND_REQUEST_COUNT = Counter(
    'app_backend_request_count', 
    'Backend Request Count',
    ['status']
)
BACKEND_REQUEST_LATENCY = Histogram(
    'app_backend_request_latency_seconds', 
    'Backend Request Latency'
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

BACKEND_URL = f"{os.environ['BACKEND_URL']}/generate"

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    path = request.url.path
    method = request.method
    
    start_time = time.time()
    
    response = await call_next(request)
    
    status_code = response.status_code
    
    if not path.startswith("/static"):
        REQUEST_COUNT.labels(
            endpoint=path, 
            method=method, 
            http_status=status_code
        ).inc()
        
        REQUEST_LATENCY.labels(
            endpoint=path, 
            method=method
        ).observe(time.time() - start_time)
    
    return response

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, text: str = ""):
    bot_response = "Задай свой вопрос"
    if text:
        async with httpx.AsyncClient() as client:
            start_time = time.time()
            try:
                response = await client.get(BACKEND_URL, params={"text": text})
                response.raise_for_status()
                bot_response = response.json()
                BACKEND_REQUEST_COUNT.labels(status="success").inc()
            except httpx.HTTPStatusError as exc:
                bot_response = f"HTTP Error: {exc.response.status_code}"
                BACKEND_REQUEST_COUNT.labels(status="http_error").inc()
            except Exception as exc:
                bot_response = f"Error occurred: {str(exc)}"
                BACKEND_REQUEST_COUNT.labels(status="exception").inc()
            finally:
                BACKEND_REQUEST_LATENCY.observe(time.time() - start_time)

    return templates.TemplateResponse("index.html", {"request": request, "bot_response": bot_response})

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
