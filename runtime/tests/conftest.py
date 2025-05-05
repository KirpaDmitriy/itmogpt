import sys
import os
from pathlib import Path
import pytest

back_dir = Path(__file__).parent.parent
sys.path.append(str(back_dir))

@pytest.fixture(autouse=True)
def set_test_env():
    os.environ["YA_CATALOG_ID"] = "1234"
    os.environ["YA_API_KEY"] = "1234"
    yield
    os.environ.pop("YA_CATALOG_ID", None)
    os.environ.pop("YA_API_KEY", None)
