import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
import os

with patch.dict(os.environ, {
    "BACKEND_URL": "1234",
}):
    from yagpt import app

client = TestClient(app)

def test_add_document():
    async def handle_request(request):
        if request.url.path == "/generate":
            return httpx.Response(
                status_code=200,
                json="Текстик"
            )
        return httpx.Response(status_code=404)
    
    mock_transport = httpx.MockTransport(handle_request)
    async with httpx.AsyncClient(transport=mock_transport) as client:
        response = client.get("/?text=Hello")
        assert response.text == ''
