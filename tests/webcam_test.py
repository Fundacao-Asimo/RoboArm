import os
import cv2
import numpy as np
import time
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, root_dir)

from src.model.HandTracker import HandTracker


def main() -> None:
    model = os.path.join(root_dir, "res", "hand_landmarker.task")
    tracker = HandTracker(
        model=model,
        num_hands=1,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    while True:
        success, image = cap.read()

        if not success:
            sys.exit(
                "ERROR: Unable to read from the webcam. Please verify your webcam settings."
            )

        cv2.flip(image, 1, image)

        try:
            image = tracker.detect(image, draw=True)

            dist_pixel = tracker.get_approximate_depth()

            print(dist_pixel)
        except Exception as e:
            print(e)

        cv2.imshow("HandTracker", image)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()


if __name__ == "__main__":
    main()
