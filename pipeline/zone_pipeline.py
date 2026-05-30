from ultralytics import YOLO
import cv2
import requests
from uuid import uuid4
from datetime import datetime, timezone
from staff_utils import is_black_clothing
model = YOLO("yolov8n.pt")

video_path = r"C:\Users\akraw\Desktop\CCTV Footage\CAM 1.mp4"
API_URL = "http://127.0.0.1:8000/events/ingest"

cap = cv2.VideoCapture(video_path)

frame_no = 0
seen_track_ids = set()

while True:
    ret, frame = cap.read()

    if not ret:
        break

    frame_no += 1

    if frame_no % 30 != 0:
        continue

    results = model.track(frame, persist=True)

    events = []

    for result in results:
        for box in result.boxes:

            if int(box.cls[0]) != 0:
                continue

            if box.id is None:
                continue

            track_id = int(box.id[0])

            if track_id in seen_track_ids:
                continue

            seen_track_ids.add(track_id)

            event = {
                "event_id": str(uuid4()),
                "store_id": "STORE_BLR_002",
                "camera_id": "CAM_PRODUCT_01",
                "visitor_id": f"VIS_{track_id}",
                "event_type": "ZONE_ENTER",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "zone_id": "PRODUCT_ZONE",
                "dwell_ms": 0,
                "is_staff": is_black_clothing(frame, box),
                "confidence": float(box.conf[0]),
                "metadata": {
                    "frame_no": frame_no,
                    "track_id": track_id,
                    "source_video": "CAM 1.mp4",
                    "sku_zone": "GENERAL_PRODUCTS"
                }
            }

            events.append(event)

    if events:
        response = requests.post(API_URL, json=events)
        print(f"Frame {frame_no}: sent {len(events)} ZONE_ENTER events -> {response.json()}")
    else:
        print(f"Frame {frame_no}: no new zone visitors")

cap.release()