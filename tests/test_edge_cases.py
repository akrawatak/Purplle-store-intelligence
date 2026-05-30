# PROMPT:
# Generate edge-case tests for staff exclusion, empty store behavior,
# and re-entry event schema validation.
#
# CHANGES MADE:
# Adjusted payloads to match the implemented Store Intelligence event schema.

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_all_staff_events_do_not_break_metrics():
    payload = [
        {
            "event_id": "staff_evt_001",
            "store_id": "STAFF_TEST_STORE",
            "camera_id": "CAM_TEST",
            "visitor_id": "STAFF_001",
            "event_type": "ZONE_ENTER",
            "timestamp": "2026-05-30T10:00:00Z",
            "zone_id": "PRODUCT_ZONE",
            "dwell_ms": 0,
            "is_staff": True,
            "confidence": 0.88,
            "metadata": {}
        }
    ]

    client.post("/events/ingest", json=payload)

    funnel = client.get("/stores/STAFF_TEST_STORE/funnel").json()

    assert funnel["entry"] == 0
    assert funnel["zone_visit"] == 0


def test_reentry_event_schema_is_accepted():
    payload = [
        {
            "event_id": "reentry_evt_001",
            "store_id": "REENTRY_TEST_STORE",
            "camera_id": "CAM_ENTRY",
            "visitor_id": "VIS_REENTRY_001",
            "event_type": "REENTRY",
            "timestamp": "2026-05-30T10:05:00Z",
            "zone_id": None,
            "dwell_ms": 0,
            "is_staff": False,
            "confidence": 0.91,
            "metadata": {
                "reason": "same visitor seen after prior exit"
            }
        }
    ]

    response = client.post("/events/ingest", json=payload)

    assert response.status_code == 200
    assert "ingested" in response.json()


def test_empty_store_funnel_returns_zeroes():
    response = client.get("/stores/NO_TRAFFIC_STORE/funnel")

    assert response.status_code == 200
    assert response.json()["entry"] == 0
    assert response.json()["zone_visit"] == 0
    assert response.json()["billing_queue"] == 0