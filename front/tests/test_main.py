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

def test_search():
    httpx_mock.add_response(
        url="http://itmogpt-back/generate",
        json="Текстик",
        status_code=200
    )
    response = await client.get("/?text=Hello")
    assert response.status_code == 200
    assert response.text == ''
