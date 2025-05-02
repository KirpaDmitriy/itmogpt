import pytest
from fastapi.testclient import TestClient
from runtime.yagpt import app

client = TestClient(app)

def test_add_document():
    assert 1 == 1
