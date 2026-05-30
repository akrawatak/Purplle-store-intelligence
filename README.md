#Overview

This project builds an end-to-end retail intelligence pipeline that converts CCTV footage into structured retail analytics and operational insights. 
Pipeline: CCTV Clips 
             ↓ 
    YOLO Detection + Tracking 
             ↓ 
    Structured Events
            ↓
    FastAPI Intelligence API 
            ↓
    SQLite Storage 
           ↓  
  Prometheus + Grafana + Streamlit North Star Metric: Offline Store Conversion Rate = Purchasing Visitors / Unique Visitors

# Quick Start Guide

This guide explains how to run the project from a fresh clone.

---

## Terminal 1: Clone Project and Start Backend

Open PowerShell.

### 1. Clone repository

```
git clone https://github.com/akrawatak/Purplle-store-intelligence.git
cd Purplle-store-intelligence

```

### 2. Create virtual environment

```
python -m venv venv

```

### 3. Activate virtual environment

```
venv\Scripts\activate

```

After activation, terminal should show:

```
(venv)

```

### 4. Install dependencies

```
pip install -r requirements.txt

```

### 5. Start Docker services

Make sure Docker Desktop is open and running.

```
docker compose up --build

```

Keep this terminal open.

This starts:

* FastAPI API
* Prometheus
* Grafana
* SQLite event storage

---

## Terminal 2: Verify API

Open a new PowerShell terminal.

Go to the project folder:

```
cd <path-to-your-folder>\Purplle-store-intelligence

```

Example:

```
cd C:\Users\akraw\Desktop\reviewer-test\Purplle-store-intelligence

```

Activate virtual environment again:

```
venv\Scripts\activate

```

Check API health:

```
curl http://127.0.0.1:8000/health

```

Check store metrics:

```
curl http://127.0.0.1:8000/stores/STORE_BLR_002/metrics

```

Expected:

* `/health` returns service status
* `/metrics` returns visitor, funnel, staff, revenue, and conversion metrics

---

## Terminal 3: Start Streamlit Dashboard

Open another PowerShell terminal.

Go to the project folder:

```
cd <path-to-your-folder>\Purplle-store-intelligence

```

Activate virtual environment:

```
venv\Scripts\activate

```

Start Streamlit:

```
streamlit run dashboard.py

```

Open:

```
http://localhost:8501

```

---

## Terminal 4: Run Detection Pipelines

Open another PowerShell terminal.

Go to the project folder:

```
cd <path-to-your-folder>\Purplle-store-intelligence

```

Activate virtual environment:

```
venv\Scripts\activate

```

Run entry detection:

```
python pipeline\detect.py

```

Run product-zone detection:

```
python pipeline\zone_pipeline.py

```

Run billing-zone detection:

```
python pipeline\billing_pipeline.py

```

Optional experimental entry / exit / re-entry detection:

```
python pipeline\entry_exit_reentry.py

```

All detection scripts emit events into:

```
POST /events/ingest

```

---

## Terminal 5: Run Tests

Open another PowerShell terminal.

Go to the project folder:

```
cd <path-to-your-folder>\Purplle-store-intelligence

```

Activate virtual environment:

```
venv\Scripts\activate

```

Run tests:

```
pytest

```

Expected:

```
all tests passed

```

---

## Useful URLs

Swagger API Docs:

```
http://127.0.0.1:8000/docs

```

Health Endpoint:

```
http://127.0.0.1:8000/health

```

Metrics Endpoint:

```
http://127.0.0.1:8000/stores/STORE_BLR_002/metrics

```

Prometheus:

```
http://127.0.0.1:9090

```

Grafana Home:

```
http://127.0.0.1:3000

```

Grafana Dashboard:

```
http://localhost:3000/d/adxgbgd/c4749ca?orgId=1&from=now-6h&to=now&timezone=browser

```

Streamlit Dashboard:

```
http://localhost:8501

```

Note:

Grafana may take a few seconds and a refresh before showing metrics.

---

## Shutdown

In Terminal 1, press:

```
CTRL + C

```

Then run:

```
docker compose down

```

```powershell
```
Note: Grafana may require a few refreshes before metrics appear. Features Entry detection Zone analytics Billing analytics Staff filtering Funnel analytics Heatmaps Conversion metrics Anomaly detection Prometheus metrics Grafana monitoring Detection Design Camera Mapping: CAM 1 → Product browsing CAM 2 → Secondary browsing angle CAM 3 → Entry / exit CAM 5 → Billing area Detection outputs structured events into: POST /events/ingest Group Entry Handling The system emits one event per detected person bounding box. If three people enter together and YOLO detects three people, three ENTRY events are emitted. Confidence Calibration Confidence scores are preserved in the event schema. Low-confidence detections are not silently removed. Edge Case Coverage Tests include: duplicate ingestion group entry low confidence events malformed payloads empty store behavior staff exclusion re-entry schema validation Known Limitations Exit detection is heuristic-based Cross-camera Re-ID is limited Re-entry logic is simplified Staff classification uses clothing heuristics Queue estimation depends on camera coverage Privacy Faces are blurred in source footage No facial recognition used Visitor IDs are session-based only Shutdown docker compose down this steps in read.md not working properly sequentially
