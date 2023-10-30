import os
import sys
import cv2
from HandTracker import HandTracker

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model = os.path.join(base_dir, "hand_landmarker.task")
    tracker = HandTracker(
        model=model,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            sys.exit(
                "ERROR: Unable to read from webcam. Please verify your webcam settings."
            )

        try:
            image = tracker.detect(image, draw=True)
            fingers = tracker.count_raised_fingers()
            print(fingers)

        except Exception as e:
            print(e)
            break

        cv2.imshow("hand_landmarker", image)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    tracker.detector.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
