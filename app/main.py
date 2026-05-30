import csv
import time
import uuid
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, Request
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
from prometheus_client import Counter, Gauge, generate_latest

from app.database import SessionLocal, engine, Base
from app.models import EventDB


Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    trace_id = str(uuid.uuid4())
    start = time.time()

    response = await call_next(request)

    latency_ms = round((time.time() - start) * 1000, 2)

    print({
        "trace_id": trace_id,
        "endpoint": request.url.path,
        "method": request.method,
        "latency_ms": latency_ms,
        "status_code": response.status_code
    })

    return response


api_requests_total = Counter("api_requests_total", "Total API requests")

unique_visitors_gauge = Gauge("store_unique_visitors", "Unique visitors per store", ["store_id"])
entry_count_gauge = Gauge("store_entries_total", "Total entry events per store", ["store_id"])
zone_visit_gauge = Gauge("store_zone_visits_total", "Total zone visits per store", ["store_id"])
billing_queue_gauge = Gauge("store_billing_queue_total", "Billing queue visitors per store", ["store_id"])
dropoff_gauge = Gauge("store_funnel_dropoff_percent", "Funnel dropoff percentage per store", ["store_id"])
conversion_rate_gauge = Gauge("store_conversion_rate_percent", "Store conversion rate percentage", ["store_id"])
revenue_gauge = Gauge("store_revenue_inr", "Store revenue in INR", ["store_id"])
transaction_gauge = Gauge("store_transactions_total", "Total POS transactions", ["store_id"])


class Event(BaseModel):
    event_id: str
    store_id: str
    camera_id: str
    visitor_id: str
    event_type: str
    timestamp: str
    zone_id: Optional[str] = None
    dwell_ms: int = 0
    is_staff: bool = False
    confidence: float
    metadata: Dict[str, Any] = {}


def get_pos_metrics(store_id: str):

    total_transactions = 0
    revenue_inr = 0

    try:
        with open("pos_transactions.csv", "r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            for row in reader:
                csv_store_id = row.get("store_id", "").strip()

                if csv_store_id != store_id:
                    continue

                total_transactions += 1

                amount = row.get("basket_value_inr", "0")

                amount = str(amount).replace(",", "").strip()

                try:
                    revenue_inr += float(amount)
                except ValueError:
                    continue

    except FileNotFoundError:
        pass

    return total_transactions, round(revenue_inr, 2)
@app.get("/")
def home():
    return {"message": "Store Intelligence API running"}


@app.get("/health")
def health():
    db: Session = SessionLocal()

    stores = db.query(EventDB.store_id).distinct().all()
    store_status = []

    for store in stores:
        store_id = store[0]

        latest_event = db.query(EventDB).filter(
            EventDB.store_id == store_id
        ).order_by(EventDB.timestamp.desc()).first()

        store_status.append({
            "store_id": store_id,
            "last_event_timestamp": latest_event.timestamp if latest_event else None,
            "warning": "STALE_FEED_CHECK_MANUAL"
        })

    db.close()

    return {
        "status": "healthy",
        "stores": store_status
    }


@app.post("/events/ingest")
def ingest(events: List[Event]):
    db: Session = SessionLocal()

    ingested = 0
    duplicates = 0

    for event in events:
        existing = db.query(EventDB).filter(
            EventDB.event_id == event.event_id
        ).first()

        if existing:
            duplicates += 1
            continue

        db_event = EventDB(
            event_id=event.event_id,
            store_id=event.store_id,
            camera_id=event.camera_id,
            visitor_id=event.visitor_id,
            event_type=event.event_type,
            timestamp=event.timestamp,
            zone_id=event.zone_id,
            dwell_ms=event.dwell_ms,
            is_staff=event.is_staff,
            confidence=event.confidence
        )

        db.add(db_event)
        ingested += 1

    db.commit()
    db.close()

    return {
        "status": "success",
        "ingested": ingested,
        "duplicates": duplicates
    }


@app.get("/stores/{store_id}/metrics")
def metrics(store_id: str):
    db: Session = SessionLocal()

    events = db.query(EventDB).filter(
        EventDB.store_id == store_id
    ).all()

    visitors = set()
    entry_count = 0
    exit_count = 0
    staff_ids = set()

    for event in events:
        visitors.add(event.visitor_id)

        if event.event_type == "ENTRY":
            entry_count += 1

        if event.event_type == "EXIT":
            exit_count += 1

        if event.is_staff:
            staff_ids.add(event.visitor_id)

    db.close()

    total_transactions, revenue_inr = get_pos_metrics(store_id)

    conversion_rate = 0
    if len(visitors) > 0:
        conversion_rate = round((total_transactions / len(visitors)) * 100, 2)

    return {
        "store_id": store_id,
        "unique_visitors": len(visitors),
        "entry_count": entry_count,
        "exit_count": exit_count,
        "staff_events": len(staff_ids),
        "conversion_rate": conversion_rate,
        "total_transactions": total_transactions,
        "revenue_inr": revenue_inr
    }


@app.get("/stores/{store_id}/funnel")
def funnel(store_id: str):
    db: Session = SessionLocal()

    events = db.query(EventDB).filter(
        EventDB.store_id == store_id
    ).all()

    entry_visitors = set()
    zone_visitors = set()
    billing_visitors = set()

    for event in events:
        if event.is_staff:
            continue

        if event.event_type == "ENTRY":
            entry_visitors.add(event.visitor_id)

        if event.event_type in ["ZONE_ENTER", "ZONE_DWELL"]:
            zone_visitors.add(event.visitor_id)

        if event.event_type == "BILLING_QUEUE_JOIN":
            billing_visitors.add(event.visitor_id)

    entry_count = len(entry_visitors)
    zone_count = len(zone_visitors)
    billing_count = len(billing_visitors)

    dropoff_pct = 0
    if entry_count > 0:
        dropoff_pct = round(
            ((entry_count - min(zone_count, entry_count)) / entry_count) * 100,
            2
        )

    db.close()

    return {
        "entry": entry_count,
        "zone_visit": zone_count,
        "billing_queue": billing_count,
        "dropoff_after_entry_pct": dropoff_pct
    }


@app.get("/stores/{store_id}/heatmap")
def heatmap(store_id: str):
    db: Session = SessionLocal()

    events = db.query(EventDB).filter(
        EventDB.store_id == store_id
    ).all()

    zone_stats = {}

    for event in events:
        if event.is_staff:
            continue

        if event.event_type not in ["ZONE_ENTER", "ZONE_DWELL"]:
            continue

        if event.zone_id is None:
            continue

        if event.zone_id not in zone_stats:
            zone_stats[event.zone_id] = {
                "visits": 0,
                "total_dwell_ms": 0
            }

        zone_stats[event.zone_id]["visits"] += 1
        zone_stats[event.zone_id]["total_dwell_ms"] += event.dwell_ms or 0

    max_visits = max(
        [data["visits"] for data in zone_stats.values()],
        default=1
    )

    heatmap_data = []

    for zone_id, data in zone_stats.items():
        avg_dwell_ms = 0

        if data["visits"] > 0:
            avg_dwell_ms = round(
                data["total_dwell_ms"] / data["visits"],
                2
            )

        score = round((data["visits"] / max_visits) * 100, 2)

        heatmap_data.append({
            "zone_id": zone_id,
            "visits": data["visits"],
            "avg_dwell_ms": avg_dwell_ms,
            "heat_score": score,
            "data_confidence": "LOW" if data["visits"] < 20 else "HIGH"
        })

    db.close()

    return {
        "store_id": store_id,
        "heatmap": heatmap_data
    }


@app.get("/stores/{store_id}/anomalies")
def anomalies(store_id: str):
    db: Session = SessionLocal()

    events = db.query(EventDB).filter(
        EventDB.store_id == store_id
    ).all()

    customer_events = [
        event for event in events
        if not event.is_staff
    ]

    entry_visitors = set()
    zone_visitors = set()
    billing_visitors = set()
    anomalies_list = []

    for event in customer_events:
        if event.event_type == "ENTRY":
            entry_visitors.add(event.visitor_id)

        if event.event_type in ["ZONE_ENTER", "ZONE_DWELL"]:
            zone_visitors.add(event.visitor_id)

        if event.event_type == "BILLING_QUEUE_JOIN":
            billing_visitors.add(event.visitor_id)

    entry_count = len(entry_visitors)
    zone_count = len(zone_visitors)
    billing_count = len(billing_visitors)

    if entry_count > 0 and zone_count == 0:
        anomalies_list.append({
            "type": "DEAD_ZONE",
            "severity": "WARN",
            "message": "Visitors entered the store but no product-zone visits were detected.",
            "suggested_action": "Check floor camera coverage and zone detection configuration."
        })

    if zone_count > billing_count:
        anomalies_list.append({
            "type": "NO_BILLING_ACTIVITY",
            "severity": "INFO",
            "message": "Product-zone activity exists, but no billing queue activity was detected.",
            "suggested_action": "Validate billing camera coverage or confirm whether no customers reached billing."
        })

    if entry_count > 0:
        zone_dropoff_pct = round(
            ((entry_count - min(zone_count, entry_count)) / entry_count) * 100,
            2
        )

        if zone_dropoff_pct > 50:
            anomalies_list.append({
                "type": "HIGH_ENTRY_DROPOFF",
                "severity": "WARN",
                "message": f"{zone_dropoff_pct}% of visitors did not reach product-zone activity.",
                "suggested_action": "Review entrance flow, camera overlap, and product-zone detection."
            })

    db.close()

    return {
        "store_id": store_id,
        "anomalies": anomalies_list
    }


@app.get("/prometheus")
def prometheus_metrics():
    api_requests_total.inc()

    db: Session = SessionLocal()

    store_ids = db.query(EventDB.store_id).distinct().all()

    for store in store_ids:
        store_id = store[0]

        events = db.query(EventDB).filter(
            EventDB.store_id == store_id,
            EventDB.is_staff == False
        ).all()

        visitors = set()
        entry_visitors = set()
        zone_visitors = set()
        billing_visitors = set()

        for event in events:
            visitors.add(event.visitor_id)

            if event.event_type == "ENTRY":
                entry_visitors.add(event.visitor_id)

            if event.event_type in ["ZONE_ENTER", "ZONE_DWELL"]:
                zone_visitors.add(event.visitor_id)

            if event.event_type == "BILLING_QUEUE_JOIN":
                billing_visitors.add(event.visitor_id)

        entry_count = len(entry_visitors)
        zone_count = len(zone_visitors)
        billing_count = len(billing_visitors)

        dropoff_pct = 0
        if entry_count > 0:
            dropoff_pct = round(
                ((entry_count - min(zone_count, entry_count)) / entry_count) * 100,
                2
            )

        total_transactions, revenue_inr = get_pos_metrics(store_id)

        conversion_rate = 0
        if len(visitors) > 0:
            conversion_rate = round(
                (total_transactions / len(visitors)) * 100,
                2
            )

        unique_visitors_gauge.labels(store_id=store_id).set(len(visitors))
        entry_count_gauge.labels(store_id=store_id).set(entry_count)
        zone_visit_gauge.labels(store_id=store_id).set(zone_count)
        billing_queue_gauge.labels(store_id=store_id).set(billing_count)
        dropoff_gauge.labels(store_id=store_id).set(dropoff_pct)
        conversion_rate_gauge.labels(store_id=store_id).set(conversion_rate)
        revenue_gauge.labels(store_id=store_id).set(revenue_inr)
        transaction_gauge.labels(store_id=store_id).set(total_transactions)

    db.close()

    return Response(
        generate_latest(),
        media_type="text/plain"
    )