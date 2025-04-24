import pytest
from fastapi.testclient import TestClient
from main.runtime import app

client = TestClient(app)=

def test_add_document():
    assert 1 == 1
