# Store Intelligence System

## Overview

This project builds an end-to-end retail intelligence pipeline that converts CCTV footage into structured retail analytics and operational insights.

Pipeline:

```text
CCTV Clips
   ↓
YOLO Detection + Tracking
   ↓
Structured Events
   ↓
FastAPI Intelligence API
   ↓
SQLite Storage
   ↓
Prometheus + Grafana + Streamlit
```

North Star Metric:

```text
Offline Store Conversion Rate
=
Purchasing Visitors / Unique Visitors
```

---

# Quick Start Guide

## 1. Clone Repository

```bash
git clone <your-private-repo-link>
cd store-intelligence
```

## 2. Create Virtual Environment

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

Linux / Mac:

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Start Infrastructure

```bash
docker compose up --build
```

This starts:

* FastAPI API
* Prometheus
* Grafana
* SQLite database persistence

## 5. Start Dashboard

Open another terminal:

```bash
streamlit run dashboard.py
```

## 6. Run Detection Pipelines

Open separate terminals.

Entry pipeline:

```bash
python pipeline/detect.py
```

Zone pipeline:

```bash
python pipeline/zone_pipeline.py
```

Billing pipeline:

```bash
python pipeline/billing_pipeline.py
```

Optional experimental entry/exit pipeline:

```bash
python pipeline/entry_exit_reentry.py
```

## 7. Run Tests

```bash
pytest
```

---

# Repository Structure

```text
store-intelligence/
├── app/
├── pipeline/
├── tests/
├── docs/
├── dashboard.py
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# URLs

Swagger Docs:

```text
http://127.0.0.1:8000/docs
```

Health:

```text
http://127.0.0.1:8000/health
```

Metrics:

```text
http://127.0.0.1:8000/stores/STORE_BLR_002/metrics
```

Prometheus:

```text
http://127.0.0.1:9090
```

Grafana Home:

```text
http://127.0.0.1:3000
```

Grafana Dashboard:

```text
http://localhost:3000/d/adxgbgd/c4749ca?orgId=1&from=now-6h&to=now&timezone=browser
```

Streamlit Dashboard:

```text
http://localhost:8501
```

Note:

```text
Grafana may require a few refreshes before metrics appear.
```

---

# Features

* Entry detection
* Zone analytics
* Billing analytics
* Staff filtering
* Funnel analytics
* Heatmaps
* Conversion metrics
* Anomaly detection
* Prometheus metrics
* Grafana monitoring

---

# Detection Design

Camera Mapping:

* CAM 1 → Product browsing
* CAM 2 → Secondary browsing angle
* CAM 3 → Entry / exit
* CAM 5 → Billing area

Detection outputs structured events into:

```text
POST /events/ingest
```

---

# Group Entry Handling

The system emits one event per detected person bounding box.

If three people enter together and YOLO detects three people, three ENTRY events are emitted.

---

# Confidence Calibration

Confidence scores are preserved in the event schema.

Low-confidence detections are not silently removed.

---

# Edge Case Coverage

Tests include:

* duplicate ingestion
* group entry
* low confidence events
* malformed payloads
* empty store behavior
* staff exclusion
* re-entry schema validation

---

# Known Limitations

* Exit detection is heuristic-based
* Cross-camera Re-ID is limited
* Re-entry logic is simplified
* Staff classification uses clothing heuristics
* Queue estimation depends on camera coverage

---

# Privacy

* Faces are blurred in source footage
* No facial recognition used
* Visitor IDs are session-based only

---

# Shutdown

```bash
docker compose down
```
