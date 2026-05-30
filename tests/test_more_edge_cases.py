# PROMPT:
# Generate additional edge case tests for duplicate handling,
# low-confidence events, group entry, and malformed requests.
#
# CHANGES MADE:
# Adjusted assertions to match current FastAPI implementation.

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_group_entry_multiple_people_counted_separately():
    payload = [
        {
            "event_id": "group_evt_001",
            "store_id": "GROUP_TEST_STORE",
            "camera_id": "CAM_ENTRY",
            "visitor_id": "VIS_GROUP_001",
            "event_type": "ENTRY",
            "timestamp": "2026-05-30T10:00:00Z",
            "zone_id": None,
            "dwell_ms": 0,
            "is_staff": False,
            "confidence": 0.90,
            "metadata": {"group_test": True}
        },
        {
            "event_id": "group_evt_002",
            "store_id": "GROUP_TEST_STORE",
            "camera_id": "CAM_ENTRY",
            "visitor_id": "VIS_GROUP_002",
            "event_type": "ENTRY",
            "timestamp": "2026-05-30T10:00:01Z",
            "zone_id": None,
            "dwell_ms": 0,
            "is_staff": False,
            "confidence": 0.87,
            "metadata": {"group_test": True}
        },
        {
            "event_id": "group_evt_003",
            "store_id": "GROUP_TEST_STORE",
            "camera_id": "CAM_ENTRY",
            "visitor_id": "VIS_GROUP_003",
            "event_type": "ENTRY",
            "timestamp": "2026-05-30T10:00:02Z",
            "zone_id": None,
            "dwell_ms": 0,
            "is_staff": False,
            "confidence": 0.83,
            "metadata": {"group_test": True}
        }
    ]

    response = client.post("/events/ingest", json=payload)
    assert response.status_code == 200

    metrics = client.get("/stores/GROUP_TEST_STORE/metrics").json()
    assert metrics["entry_count"] == 3
    assert metrics["unique_visitors"] == 3


def test_low_confidence_event_is_not_rejected():
    payload = [
        {
            "event_id": "low_conf_evt_001",
            "store_id": "LOW_CONF_STORE",
            "camera_id": "CAM_ENTRY",
            "visitor_id": "VIS_LOW_CONF",
            "event_type": "ENTRY",
            "timestamp": "2026-05-30T10:00:00Z",
            "zone_id": None,
            "dwell_ms": 0,
            "is_staff": False,
            "confidence": 0.31,
            "metadata": {"confidence_bucket": "LOW"}
        }
    ]

    response = client.post("/events/ingest", json=payload)

    assert response.status_code == 200
    assert "ingested" in response.json()


def test_malformed_event_missing_required_field_returns_422():
    payload = [
        {
            "store_id": "BAD_STORE",
            "camera_id": "CAM_ENTRY",
            "visitor_id": "VIS_BAD",
            "event_type": "ENTRY",
            "timestamp": "2026-05-30T10:00:00Z",
            "confidence": 0.90
        }
    ]

    response = client.post("/events/ingest", json=payload)

    assert response.status_code == 422


def test_duplicate_payload_safe_to_send_twice():
    payload = [
        {
            "event_id": "safe_duplicate_evt_001",
            "store_id": "DUPLICATE_TEST_STORE",
            "camera_id": "CAM_ENTRY",
            "visitor_id": "VIS_DUPLICATE",
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