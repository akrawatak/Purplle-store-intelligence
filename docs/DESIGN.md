# DESIGN.md

## Architecture Overview

The system follows an event-driven retail intelligence architecture that converts CCTV footage into structured business analytics.

Pipeline Flow:

```text
CCTV Footage
    ↓
YOLO Detection + Tracking
    ↓
Structured Event Generation
    ↓
FastAPI Ingestion API
    ↓
SQLite Storage
    ↓
Analytics Layer
    ↓
Prometheus + Grafana + Streamlit
```

The architecture was designed around the challenge North Star metric:

```text
Offline Store Conversion Rate
=
Purchasing Visitors / Unique Visitors
```

Each component exists either to improve metric accuracy or improve metric usability.

---

## Detection Layer

The detection layer uses YOLOv8 with tracking enabled.

Responsibilities:

* person detection
* visitor tracking
* confidence scoring
* event generation
* staff filtering

Tracking IDs are used as temporary visitor identifiers.

Detection outputs structured events rather than directly generating analytics.

Reason:

Separating detection from analytics reduces coupling and allows replay of historical event streams.

---

## Tracking and Session Layer

Tracking is session-based.

Visitor IDs are generated from:

```text
track_id
+
camera context
+
session duration
```

This approach was chosen because:

* footage is anonymised
* face recognition is intentionally avoided
* tracking IDs are lightweight

Limitations:

* cross-camera re-identification is limited
* long disappearances may create new sessions

---

## Event Layer

Detection pipelines emit structured events:

Examples:

```text
ENTRY
ZONE_ENTER
ZONE_DWELL
BILLING_QUEUE_JOIN
EXIT
```

Events are pushed into:

```text
POST /events/ingest
```

Why event architecture?

Events decouple:

```text
Detection
≠
Storage
≠
Analytics
```

This improves scalability and testing.

---

## API Layer

FastAPI provides:

* ingestion
* deduplication
* metrics
* funnel analytics
* anomaly detection
* health monitoring

Design decision:

The challenge suggested multiple API modules, but the implementation keeps logic primarily in:

```text
app/main.py
```

Reason:

* faster iteration
* fewer moving parts
* easier debugging during rapid experimentation

Tradeoff:

Reduced modularity compared to larger production systems.

---

## Storage Layer

SQLite stores:

* events
* visitor sessions
* funnel state

Why SQLite?

Pros:

* zero setup
* portable
* simple Docker deployment

Cons:

* limited horizontal scalability

SQLite was selected because challenge scale is relatively small.

---

## Monitoring Layer

Prometheus collects:

* API metrics
* visitor metrics
* conversion metrics
* queue metrics

Grafana provides:

* operational monitoring
* KPI dashboards
* alert visualization

Streamlit provides:

* business-facing dashboards

This separation was intentional:

```text
Grafana → operators
Streamlit → business users
```

---

## AI-Assisted Decisions

### Decision 1

Problem:

Choose between faster vs more accurate detectors.

AI suggestion:

Use YOLOv8n.

What changed:

Accepted recommendation.

Reason:

Latency mattered more than marginal accuracy improvements.

---

### Decision 2

Problem:

Design API architecture.

AI suggestion:

Use event ingestion architecture.

What changed:

Adopted with SQLite-backed persistence.

Reason:

Enabled replayability and real-time dashboards.

---

### Decision 3

Problem:

Staff exclusion.

AI suggestion:

Use appearance-based heuristics.

What changed:

Modified heuristic to use black-clothing detection because staff uniforms follow domain rules.

Reason:

Cheaper and simpler than classification models.

---

## Privacy and Anonymisation

The system treats all visitors as anonymous entities.

Privacy protections:

* faces are blurred in source footage
* no facial recognition
* no biometric storage
* session-only identifiers

Visitor IDs are synthetic tracking identifiers rather than identities.

This keeps the system focused on retail analytics rather than surveillance.
