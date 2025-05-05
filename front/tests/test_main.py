import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import os
import httpx

with patch.dict(os.environ, {
    "BACKEND_URL": "1234",
}):
    from frontback import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_search():
    async def handle_request(request):
        if request.url.path == "/":
            return httpx.Response(
                status_code=200,
                json="Текстик"
            )
        return httpx.Response(status_code=404)
    
    mock_transport = httpx.MockTransport(handle_request)
    async with httpx.AsyncClient(transport=mock_transport) as client:
        response = await client.get("/?text=Hello")
        assert response.status_code == 200
        assert response.text == ''
