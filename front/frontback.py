from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

BACKEND_URL = "http://0.0.0.0:8001/generate"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, text: str = ""):
    bot_response = "No question asked yet."
    if text:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(BACKEND_URL, params={"text": text})
                response.raise_for_status()
                bot_response = response.json()
            except httpx.HTTPStatusError as exc:
                bot_response = f"HTTP Error: {exc.response.status_code}"
            except Exception as exc:
                bot_response = f"Error occurred: {str(exc)}"

    return templates.TemplateResponse("index.html", {"request": request, "bot_response": bot_response})
  
