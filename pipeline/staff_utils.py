import cv2
import numpy as np


def is_black_clothing(frame, box):

    x1, y1, x2, y2 = box.xyxy[0]
    x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

    height = y2 - y1

    upper = y1 + int(height * 0.25)
    lower = y1 + int(height * 0.90)

    person_crop = frame[upper:lower, x1:x2]

    if person_crop.size == 0:
        return False

    hsv = cv2.cvtColor(
        person_crop,
        cv2.COLOR_BGR2HSV
    )

    black_mask = hsv[:, :, 2] < 60

    black_ratio = np.mean(
        black_mask
    )

    return bool(
        black_ratio > 0.70
    )