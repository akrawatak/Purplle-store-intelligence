# CHOICES.md

## Decision 1: Detection Model Selection

### Options Considered

* YOLOv8n
* RT-DETR
* MediaPipe

### What AI Suggested

Use YOLOv8n because the challenge requires near real-time processing, multi-person detection, and operation on commodity hardware.

### Final Choice

YOLOv8n with built-in tracking.

### Why

YOLOv8n provided the best tradeoff between:

* inference speed
* acceptable detection quality
* easy deployment
* local execution without GPUs

RT-DETR was considered because of stronger accuracy, but inference latency was higher. MediaPipe was not suitable because it focuses more on landmarks rather than multi-person retail analytics.

### Tradeoffs

Pros:

* fast inference
* simple deployment
* good tracking integration

Cons:

* weaker small-object detection
* imperfect re-identification

---

## Decision 2: Event Schema Design

### Options Considered

1. Minimal schema

```text
visitor_id + event_type + timestamp
```

2. Rich schema

```text
visitor_id + zone + confidence + metadata + dwell + staff flag
```

### What AI Suggested

Use a richer schema because downstream analytics require more context than simple counts.

### Final Choice

Rich schema.

### Why

The richer schema enables:

* funnel analytics
* heatmaps
* anomaly detection
* confidence tracking
* session reconstruction
* staff exclusion

### Tradeoffs

Pros:

* extensible
* analytics-friendly

Cons:

* larger payload size
* more validation complexity

---

## Decision 3: API Architecture Choice

### Options Considered

* Batch analytics pipeline
* Event ingestion architecture

### What AI Suggested

Use real-time ingestion APIs with incremental metric computation.

### Final Choice

Event-driven ingestion API.

### Why

This architecture enables:

* live dashboards
* Prometheus monitoring
* near real-time analytics
* anomaly generation

### Tradeoffs

Pros:

* real-time metrics
* easier monitoring

Cons:

* higher operational complexity

---

## Tracking and Re-identification Choice

### Problem

Frame-level counting caused repeated visitor inflation.

### Final Choice

Use YOLO tracking IDs.

### Why

`track_id` based visitor IDs significantly reduce duplicate visitor counts while remaining lightweight.

### Limitation

Cross-camera re-identification remains limited.

---

## Staff Detection Choice

### Domain Knowledge Used

Staff members wear black clothing.

### Implementation

A color-based heuristic checks clothing regions and flags:

```text
is_staff = true
```

### Tradeoff

Pros:

* lightweight
* explainable
* fast

Cons:

* dark clothing customers may be misclassified

---

## Camera Mapping Decisions

* CAM 1 → Product browsing / zone activity
* CAM 2 → Secondary browsing angle
* CAM 3 → Entry / outside gate
* CAM 4 → Low-value operational area
* CAM 5 → Billing zone

Because billing footage had limited queue activity, billing events were partially validated using injected events.

---

## Privacy and Anonymisation

* Faces are already blurred
* No facial recognition used
* Visitor IDs are session-based
* Tracking focuses on anonymous analytics only


## Group Entry Handling

The pipeline emits one event per detected person bounding box. If YOLO detects three people entering together, three ENTRY events are emitted.

## Confidence Handling

Low-confidence detections are not silently discarded. Confidence is preserved in the event schema so downstream consumers can decide whether to use, down-weight, or inspect those events.

