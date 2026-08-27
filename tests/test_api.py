from fastapi.testclient import TestClient

from watermark_lab.api import create_app
from watermark_lab.config import WatermarkConfig


def test_health_endpoint():
    client = TestClient(create_app(WatermarkConfig("test-secret")))
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
