import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

with patch.dict(os.environ, {
    "YA_CATALOG_ID": "1234",
    "YA_API_KEY": "1234",
}):
    from yagpt import app

client = TestClient(app)

def test_add_document():
    with patch('yagpt.yandex_gpt.get_async_completion', new_callable=AsyncMock) as mock_completion:
        mock_completion.return_value = "Текстик"
        response = client.get("/generate?text=Hello")
        assert response.text == "Текстик"
