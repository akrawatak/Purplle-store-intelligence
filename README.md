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
