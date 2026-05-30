from ultralytics import YOLO
import cv2
import requests
from uuid import uuid4
from datetime import datetime, timezone

model = YOLO("yolov8n.pt")

video_path = r"C:\Users\akraw\Desktop\CCTV Footage\CAM 3.mp4"
API_URL = "http://127.0.0.1:8000/events/ingest"

STORE_ID = "STORE_BLR_002"
CAMERA_ID = "CAM_ENTRY_01"

cap = cv2.VideoCapture(video_path)

# Tune this line based on CAM 3 frame.
# People crossing this vertical line are considered entry/exit.
LINE_X = 1450

track_last_x = {}
track_state = {}
exited_tracks = set()
session_seq = {}

frame_no = 0

while True:
    ret, frame = cap.read()

    if not ret:
        break

    frame_no += 1

    if frame_no % 15 != 0:
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
            confidence = float(box.conf[0])

            x1, y1, x2, y2 = box.xyxy[0]
            center_x = int((x1 + x2) / 2)

            previous_x = track_last_x.get(track_id)
            track_last_x[track_id] = center_x

            print(f"track={track_id}, previous_x={previous_x}, current_x={center_x}")

            if previous_x is None:
                continue

            visitor_id = f"VIS_{track_id}"

            if visitor_id not in session_seq:
                session_seq[visitor_id] = 0

            event_type = None

            # Direction logic:
            # left -> right = ENTRY
            # right -> left = EXIT
            if previous_x < LINE_X and center_x >= LINE_X:
                if track_state.get(track_id) == "EXITED":
                    event_type = "REENTRY"
                else:
                    event_type = "ENTRY"

                track_state[track_id] = "INSIDE"

            elif previous_x > LINE_X and center_x <= LINE_X:
                event_type = "EXIT"
                track_state[track_id] = "EXITED"
                exited_tracks.add(track_id)

            if event_type is None:
                continue

            session_seq[visitor_id] += 1

            event = {
                "event_id": str(uuid4()),
                "store_id": STORE_ID,
                "camera_id": CAMERA_ID,
                "visitor_id": visitor_id,
                "event_type": event_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "zone_id": None,
                "dwell_ms": 0,
                "is_staff": False,
                "confidence": confidence,
                "metadata": {
                    "frame_no": frame_no,
                    "track_id": track_id,
                    "line_x": LINE_X,
                    "previous_x": previous_x,
                    "current_x": center_x,
                    "session_seq": session_seq[visitor_id],
                    "source_video": "CAM 3.mp4",
                    "method": "line_crossing_direction"
                }
            }

            events.append(event)

    if events:
        response = requests.post(API_URL, json=events)
        print(f"Frame {frame_no}: sent {len(events)} events -> {response.json()}")
    else:
        print(f"Frame {frame_no}: no line crossing")

cap.release()