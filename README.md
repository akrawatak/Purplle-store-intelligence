# Store Intelligence System

## Overview

This project builds an end-to-end retail intelligence pipeline that converts CCTV footage into structured retail analytics and operational insights.

## Architecture Pipeline

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

## North Star Metric

```text
Offline Store Conversion Rate
=
Purchasing Visitors / Unique Visitors
```

---

# Tech Stack

| Layer            | Technology          |
| ---------------- | ------------------- |
| Detection        | YOLOv8              |
| API              | FastAPI             |
| Database         | SQLite              |
| Monitoring       | Prometheus          |
| Dashboard        | Grafana + Streamlit |
| Testing          | Pytest              |
| Containerization | Docker Compose      |

---

# Repository Structure

```text
Purplle-store-intelligence/
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

# Quick Start Guide

## Terminal 1 — Clone and Start Backend

Open PowerShell.

Clone repository:

```powershell
git clone https://github.com/akrawatak/Purplle-store-intelligence.git
cd Purplle-store-intelligence
```

Create virtual environment:

```powershell
python -m venv venv
```

Activate:

```powershell
venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Start infrastructure:

```powershell
docker compose up --build
```

If Docker container conflict happens:

```powershell
docker rm -f store-intelligence-api
docker rm -f store-prometheus
docker rm -f store-grafana
docker compose up --build
```

Keep this terminal running.

Services started:

* FastAPI API
* Prometheus
* Grafana
* SQLite storage

---

## Terminal 2 — Verify API

Open new terminal.

```powershell
cd Purplle-store-intelligence
venv\Scripts\activate
```

Health check:

```powershell
curl http://127.0.0.1:8000/health
```

Metrics:

```powershell
curl http://127.0.0.1:8000/stores/STORE_BLR_002/metrics
```

Expected:

* Health endpoint returns healthy response
* Metrics endpoint returns JSON

---

## Terminal 3 — Start Business Dashboard

Open new terminal:

```powershell
cd Purplle-store-intelligence
venv\Scripts\activate
streamlit run dashboard.py
```

Dashboard:

```text
http://localhost:8501
```

---

## Terminal 4 — Run Detection Pipelines

Open new terminal:

```powershell
cd Purplle-store-intelligence
venv\Scripts\activate
```

Run entry detection:

```powershell
python pipeline\detect.py
```

Run zone analytics:

```powershell
python pipeline\zone_pipeline.py
```

Run billing analytics:

```powershell
python pipeline\billing_pipeline.py
```

Optional experimental pipeline:

```powershell
python pipeline\entry_exit_reentry.py
```

All pipelines emit structured events into:

```text
POST /events/ingest
```

---

## Terminal 5 — Run Tests

Open new terminal:

```powershell
cd Purplle-store-intelligence
venv\Scripts\activate
pytest
```

Expected:

```text
all tests passed
```

---

# Monitoring URLs

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

Grafana:

```text
http://127.0.0.1:3000
```

Streamlit:

```text
http://localhost:8501
```

---

# Grafana Setup

Login:

```text
username: admin
password: admin
```

Add datasource:

```text
Connections
→ Data Sources
→ Add Data Source
→ Prometheus
```

Set URL:

```text
http://prometheus:9090
```

Prometheus Queries:

Unique Visitors:

```text
store_unique_visitors
```

Entries:

```text
store_entries_total
```

Revenue:

```text
store_revenue_inr
```

Transactions:

```text
store_transactions_total
```

Billing Queue:

```text
store_billing_queue_total
```

Conversion Rate:

```text
store_conversion_rate_percent
```

Dropoff:

```text
store_funnel_dropoff_percent
```

API Requests:

```text
api_requests_total
```

---

# Features

* Entry Detection
* Zone Analytics
* Billing Analytics
* Funnel Analytics
* Staff Filtering
* Heatmaps
* Conversion Metrics
* Prometheus Monitoring
* Grafana Monitoring
* Streamlit Dashboard
* Anomaly Detection

---

# Detection Design

Camera usage:

* CAM1 → Product browsing
* CAM2 → Secondary browsing
* CAM3 → Entry / Exit
* CAM5 → Billing

---

# Edge Case Handling

Implemented:

* Duplicate event ingestion
* Group entry handling
* Low confidence preservation
* Malformed payload checks
* Empty store handling
* Staff exclusion
* Schema validation

---

# Known Limitations

* Exit detection heuristic-based
* Re-entry logic simplified
* Cross-camera ReID limited
* Staff classification heuristic-based
* Queue estimation camera dependent

---

# Privacy

* Faces already blurred
* No facial recognition
* Visitor IDs are synthetic/session-based

---

# Shutdown

Stop services:

```powershell
docker compose down
```
