# PROMPT:
# Generate FastAPI tests for event ingestion, duplicate event handling,
# empty store metrics, funnel calculation, and anomaly response.
#
# CHANGES MADE:
# Adjusted test payload to match the Store Intelligence event schema.

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_ingest_event_success():
    payload = [
        {
            "event_id": "test_evt_001",
            "store_id": "TEST_STORE",
            "camera_id": "CAM_TEST",
            "visitor_id": "VIS_TEST_001",
            "event_type": "ENTRY",
            "timestamp": "2026-05-30T10:00:00Z",
            "zone_id": None,
            "dwell_ms": 0,
            "is_staff": False,
            "confidence": 0.95,
            "metadata": {}
        }
    ]

    response = client.post("/events/ingest", json=payload)

    assert response.status_code == 200
    assert "ingested" in response.json()


def test_duplicate_event_idempotency():
    payload = [
        {
            "event_id": "test_evt_duplicate",
            "store_id": "TEST_STORE",
            "camera_id": "CAM_TEST",
            "visitor_id": "VIS_TEST_002",
            "event_type": "ENTRY",
            "timestamp": "2026-05-30T10:00:00Z",
            "zone_id": None,
            "dwell_ms": 0,
            "is_staff": False,
            "confidence": 0.95,
            "metadata": {}
        }
    ]

    first = client.post("/events/ingest", json=payload)
    second = client.post("/events/ingest", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["duplicates"] >= 1


def test_empty_store_metrics():
    response = client.get("/stores/EMPTY_STORE/metrics")

    assert response.status_code == 200
    assert response.json()["unique_visitors"] == 0
    assert response.json()["entry_count"] == 0


def test_funnel_endpoint():
    response = client.get("/stores/TEST_STORE/funnel")

    assert response.status_code == 200
    assert "entry" in response.json()
    assert "zone_visit" in response.json()
    assert "billing_queue" in response.json()


def test_anomalies_endpoint():
    response = client.get("/stores/TEST_STORE/anomalies")

    assert response.status_code == 200
    assert "anomalies" in response.json()