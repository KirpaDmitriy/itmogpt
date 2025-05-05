from yandex_gpt import YandexGPT, YandexGPTConfigManagerForAPIKey
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os

config = YandexGPTConfigManagerForAPIKey(
    model_type="yandexgpt",
    catalog_id=os.environ['YA_CATALOG_ID'],
    api_key=os.environ['YA_API_KEY'],
)

yandex_gpt = YandexGPT(config_manager=config)

app = FastAPI()

@app.get("/generate")
async def generate_response(text: str):
    try:
        messages = [{"role": "user", "text": text}]
        response = await yandex_gpt.get_async_completion(messages=messages, timeout=60)
        print(response)
        return response
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
