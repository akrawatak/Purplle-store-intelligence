from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")

video_path = "sample.mp4"   # replace later

cap = cv2.VideoCapture(video_path)

frame_count = 0

while cap.isOpened():

    ret, frame = cap.read()

    if not ret:
        break

    frame_count += 1

    if frame_count % 30 != 0:
        continue

    results = model(frame)

    for result in results:

        for box in result.boxes:

            cls = int(box.cls[0])

            if cls == 0:  # person

                print("PERSON DETECTED")

cap.release()