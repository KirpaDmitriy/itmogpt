import pytest
from fastapi.testclient import TestClient
from yagpt import app
from unittest.mock import AsyncMock, patch

client = TestClient(app)

def test_add_document():
    with patch('yagpt.yandex_gpt.get_async_completion', new_callable=AsyncMock) as mock_completion:
        mock_completion.return_value = "Текстик"
        response = client.get("/generate?text=Hello")
        assert response.text == "Текстик"
