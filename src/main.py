import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, root_dir)

import cv2
import numpy as np
import time
import sys
import threading

from pyfirmata2 import Arduino

from src.model.HandTracker import HandTracker
from src.control.RoboArm import RoboArm


class HandFollowerController:
    """
    Class to control the RoboArm to follow the hand

    Attributes:
        tracker (HandTracker): HandTracker object
        board (Arduino): Arduino object
        controller (RoboArm): RoboArm object
        image_shape (tuple): Image resolution (width, height)
        cap (cv2.VideoCapture): VideoCapture object
        servos_values (dict): Dictionary of servo names and their angles

    Methods:
        loop(): Main loop for tracking and controlling the RoboArm
        clear(): Clean up resources and close the webcam and detector
        draw_info(image, rect_color=(255, 51, 51), text_color=(0, 128, 255)): Draw a rectangle and servo angle information on the image
        follow_hand(landmark: int = 0): Control the RoboArm to follow the detected hand
    """

    def __init__(self, port: str, model: str, image_shape: tuple = (640, 480)) -> None:
        """
        Initialize the HandFollowerController class.

        Args:
            port (str): The port of the Arduino board.
            image_shape (tuple): The resolution of the webcam.
            model (str): The path to the model file.
        """
        # Initialize the HandTracker
        self.tracker = HandTracker(
            model=model,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        # Initialize the Arduino board and RoboArm
        try:
            self.board = Arduino(port)
            self.controller = RoboArm(self.board)
        except Exception as e:
            print(e)
            sys.exit(
                "ERROR: Unable to connect to the Arduino board. Please verify your Arduino port."
            )

        self.servos_values = {
            "base": 0,
            "height": 0,
            "reach": 0,
            "claw": 0,
        }

        # Set webcam parameters
        self.image_shape = image_shape
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, self.image_shape[1])
        self.cap.set(4, self.image_shape[0])

    def loop(self) -> None:
        """
        Main loop for tracking and controlling the RoboArm.
        """
        time.sleep(2)

        while self.cap.isOpened():
            success, image = self.cap.read()

            if not success:
                sys.exit(
                    "ERROR: Unable to read from the webcam. Please verify your webcam settings."
                )

            cv2.flip(image, 1, image)

            try:
                image = self.tracker.detect(image, draw=True)
                self.follow_hand()
                self.draw_info(image)
            except Exception as e:
                print(e)

            cv2.imshow("hand_landmarker", image)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        self.clear()

    def clear(self) -> None:
        """
        Clean up resources and close the webcam and detector.
        """
        self.tracker.detector.close()
        self.cap.release()
        cv2.destroyAllWindows()

    def draw_info(
        self,
        image: np.ndarray,
        rect_color: tuple = (255, 51, 51),
        text_color: tuple = (0, 128, 255),
    ) -> None:
        """
        Draw a rectangle and servo angle information on the image.

        Args:
            image (np.ndarray): The image to draw on.
            rect_color (tuple): The color of the rectangle.
            text_color (tuple): The color of the text.
        """
        # Get the height and width of the image
        height, width = self.image_shape

        # Define origin point and rectangle size
        x1, y1 = int(width * 0.021), int(height * 0.5)
        w, h = 180, 150
        x2, y2 = x1 + w, y1 + h

        # Draw the rectangle with rounded corners
        r, d, thickness = 20, 20, 3
        # Top left
        cv2.line(image, (x1 + r, y1), (x1 + r + d, y1), rect_color, thickness)
        cv2.line(image, (x1, y1 + r), (x1, y1 + r + d), rect_color, thickness)
        cv2.ellipse(image, (x1 + r, y1 + r), (r, r), 180, 0, 90, rect_color, thickness)
        # Top right
        cv2.line(image, (x2 - r, y1), (x2 - r - d, y1), rect_color, thickness)
        cv2.line(image, (x2, y1 + r), (x2, y1 + r + d), rect_color, thickness)
        cv2.ellipse(image, (x2 - r, y1 + r), (r, r), 270, 0, 90, rect_color, thickness)
        # Bottom left
        cv2.line(image, (x1 + r, y2), (x1 + r + d, y2), rect_color, thickness)
        cv2.line(image, (x1, y2 - r), (x1, y2 - r - d), rect_color, thickness)
        cv2.ellipse(image, (x1 + r, y2 - r), (r, r), 90, 0, 90, rect_color, thickness)
        # Bottom right
        cv2.line(image, (x2 - r, y2), (x2 - r - d, y2), rect_color, thickness)
        cv2.line(image, (x2, y2 - r), (x2, y2 - r - d), rect_color, thickness)
        cv2.ellipse(image, (x2 - r, y2 - r), (r, r), 0, 0, 90, rect_color, thickness)

        # Set the initial position of the text inside the rectangle
        text_x, text_y = x1 + int(w * 0.09), y1 + int(h * 0.25)
        # Write each line of text on the image
        for i, (name, servo) in enumerate(self.controller.servos.items()):
            cv2.putText(
                image,
                "{}: {}".format(name.title(), servo.read()),
                (text_x, text_y + i * 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                text_color,
                2,
            )

    def follow_hand(self, landmark: int = 0) -> None:
        """
        Control the RoboArm to follow the detected hand.

        Args:
            landmark (int): The index of the landmark to track.

        Returns:
            None
        """
        landmark = self.tracker.get_hand_landmarks(idxs=[landmark])

        if len(landmark) > 0:
            x, y = landmark[0].x, landmark[0].y
            z = self.tracker.get_approximate_depth()
            n_finger = np.sum(self.tracker.raised_fingers())

            self.servos_values["base"] = int(
                np.interp(
                    x * self.image_shape[1],
                    [0, self.image_shape[1]],
                    [
                        self.controller.servos["Base"].get_limit(1),
                        self.controller.servos["Base"].get_limit(0),
                    ],
                )
            )
            self.servos_values["height"] = int(
                np.interp(
                    y * self.image_shape[0],
                    [0, self.image_shape[0]],
                    [
                        self.controller.servos["Height"].get_limit(1),
                        self.controller.servos["Height"].get_limit(0),
                    ],
                )
            )
            self.servos_values["reach"] = int(
                np.interp(
                    z,
                    [30, 120],
                    [
                        self.controller.servos["Reach"].get_limit(1),
                        self.controller.servos["Reach"].get_limit(0),
                    ],
                )
            )
            self.servos_values["claw"] = int(
                np.interp(
                    n_finger,
                    [0, 5],
                    [
                        self.controller.servos["Claw"].get_limit(1),
                        self.controller.servos["Claw"].get_limit(0),
                    ],
                )
            )

            self.controller.control_servos(**self.servos_values)
        else:
            self.controller.initialize_sensors()


def main() -> None:
    image_shape = (640, 480)  # Change to match your webcam resolution
    port = Arduino.AUTODETECT  # Change to match your Arduino port
    model = os.path.join(root_dir, "res", "hand_landmarker.task")

    controller = HandFollowerController(port, model=model, image_shape=image_shape)
    controller.loop()


if __name__ == "__main__":
    main()
