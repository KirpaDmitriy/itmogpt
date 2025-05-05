import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import os
import httpx

with patch.dict(os.environ, {
    "BACKEND_URL": "http://itmogpt-back",
}):
    from frontback import app

client = TestClient(app)

def test_search(httpx_mock):
    httpx_mock.add_response(
        url=r"http://itmogpt-back/generate?text=Hello",
        json="Текстик",
        status_code=200
    )
    response = client.get("/?text=Hello")
    assert response.status_code == 200
    assert response.text == """  + <!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ИТМО GPT</title>
    <link rel="stylesheet" href="/static/styles.css">
    <link rel="icon" type="image/x-icon" href="/static/images/favicon.jpg">
</head>
<body>
    <div class="container">
        <h1>Спроси ИТМО GPT</h1>
        <form action="/" method="get" class="form">
            <input type="text" name="text" id="inputText" placeholder="Введи вопрос">
            <button type="submit" class="button">Спросить</button>
        </form>
        <div id="response" class="response-box">
            <span>ИТМО GPT:</span> Error occurred: No response can be found for GET request on http://itmogpt-back/generate?text=Hello amongst: Match any request on http://itmogpt-back/generate
        </div>
    </div>
</body>
</html>"""
