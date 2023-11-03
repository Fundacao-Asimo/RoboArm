import time
import math

import cv2
import numpy as np
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2

class HandTracker:
    def __init__(
        self,
        model: str,
        num_hands: int,
        min_hand_detection_confidence: float,
        min_hand_presence_confidence: float,
        min_tracking_confidence: float,
    ):
        """
        Initialize a HandTracker instance.

        Args:
            model (str): The path to the model for hand tracking.
            num_hands (int): Maximum number of hands to detect.
            min_hand_detection_confidence (float): Minimum confidence value ([0.0, 1.0]) for successful hand detection.
            min_hand_presence_confidence (float): Minimum confidence value ([0.0, 1.0]) for presence of a hand to be tracked.
            min_tracking_confidence (float): Minimum confidence value ([0.0, 1.0]) for successful hand landmark tracking.
        """
        self.model = model

        self.detector = self.initialize_detector(
            num_hands,
            min_hand_detection_confidence,
            min_hand_presence_confidence,
            min_tracking_confidence,
        )

        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.fps_avg_frame_count = 30

        self.COUNTER, self.FPS = 0, 0
        self.START_TIME = time.time()
        self.DETECTION_RESULT = None

        self.tipIds = [4, 8, 12, 16, 20]

        # x is the raw distance y is the value in cm
        # x = [170, 132, 104, 92, 82, 72]
        # y = [20, 25, 30, 35, 40, 45]
        x = np.array([300, 245, 200, 170, 145, 130, 112, 103, 93, 87, 80, 75, 70, 67, 62, 59, 57]) / 1.5
        y = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
        self.coff = np.polyfit(x, y, 2)  # y = Ax^2 + Bx + C

    def save_result(self, result: landmark_pb2.NormalizedLandmarkList, unused_output_image, timestamp_ms: int):
        """
        Saves the result of the detection.

        Args:
            result (mediapipe.framework.formats.landmark_pb2.NormalizedLandmarkList): Result of the detection.
            unused_output_image (mediapipe.framework.formats.image_frame.ImageFrame): Unused.
            timestamp_ms (int): Timestamp of the detection.

        Returns:
            None
        """
        if self.COUNTER % self.fps_avg_frame_count == 0:
            self.FPS = self.fps_avg_frame_count / (time.time() - self.START_TIME)
            self.START_TIME = time.time()

        if len(result.handedness):
            self.DETECTION_RESULT = result
        else:
            self.DETECTION_RESULT = None

        self.COUNTER += 1

    def initialize_detector(
        self,
        num_hands: int,
        min_hand_detection_confidence: float,
        min_hand_presence_confidence: float,
        min_tracking_confidence: float,
    ):
        """
        Initializes the HandLandmarker instance.

        Args:
            num_hands (int): Maximum number of hands to detect.
            min_hand_detection_confidence (float): Minimum confidence value ([0.0, 1.0]) for hand detection to be considered successful.
            min_hand_presence_confidence (float): Minimum confidence value ([0.0, 1.0]) for the presence of a hand for the hand landmarks to be considered tracked successfully.
            min_tracking_confidence (float): Minimum confidence value ([0.0, 1.0]) for the hand landmarks to be considered tracked successfully.

        Returns:
            mediapipe.HandLandmarker: HandLandmarker instance.
        """
        base_options = python.BaseOptions(model_asset_path=self.model)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.LIVE_STREAM,
            num_hands=num_hands,
            min_hand_detection_confidence=min_hand_detection_confidence,
            min_hand_presence_confidence=min_hand_presence_confidence,
            min_tracking_confidence=min_tracking_confidence,
            result_callback=self.save_result,
        )
        return vision.HandLandmarker.create_from_options(options)

    def draw_landmarks(
        self,
        image: np.ndarray,
        text_color: tuple = (0, 0, 0),
        font_size: int = 1,
        font_thickness: int = 1,
    ) -> np.ndarray:
        """
        Draws the landmarks and handedness on the image.

        Args:
            image (numpy.ndarray): Image on which to draw the landmarks.
            text_color (tuple, optional): Color of the text. Defaults to (0, 0, 0).
            font_size (int, optional): Size of the font. Defaults to 1.
            font_thickness (int, optional): Thickness of the font. Defaults to 1.

        Returns:
            numpy.ndarray: Image with the landmarks drawn.
        """

        # Show the FPS
        fps_text = "FPS = {:.1f}".format(self.FPS)

        cv2.putText(
            image,
            fps_text,
            (24, 30),
            cv2.FONT_HERSHEY_DUPLEX,
            font_size,
            text_color,
            font_thickness,
            cv2.LINE_AA,
        )

        HANDEDNESS_TEXT_COLOR = (88, 205, 54)  # vibrant green

        if self.DETECTION_RESULT:
            # Landmark visualization parameters.
            MARGIN = 10  # pixels
            FONT_SIZE = 1
            FONT_THICKNESS = 1
            # Draw landmarks and indicate handedness.
            for idx in range(len(self.DETECTION_RESULT.hand_landmarks)):
                hand_landmarks = self.DETECTION_RESULT.hand_landmarks[idx]
                handedness = self.DETECTION_RESULT.handedness[idx]

                # Draw the hand landmarks.
                hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                hand_landmarks_proto.landmark.extend(
                    [
                        landmark_pb2.NormalizedLandmark(
                            x=landmark.x, y=landmark.y, z=landmark.z
                        )
                        for landmark in hand_landmarks
                    ]
                )
                self.mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks_proto,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style(),
                )

                # Get the top left corner of the detected hand's bounding box.
                height, width, _ = image.shape
                x_coordinates = [landmark.x for landmark in hand_landmarks]
                y_coordinates = [landmark.y for landmark in hand_landmarks]
                text_x = int(min(x_coordinates) * width)
                text_y = int(min(y_coordinates) * height) - MARGIN

                # Draw handedness (left or right hand) on the image.
                cv2.putText(
                    image,
                    f"{handedness[0].category_name}",
                    (text_x, text_y),
                    cv2.FONT_HERSHEY_DUPLEX,
                    FONT_SIZE,
                    HANDEDNESS_TEXT_COLOR,
                    FONT_THICKNESS,
                    cv2.LINE_AA,
                )

        return image

    def detect(self, frame: np.ndarray, draw: bool = False) -> np.ndarray:
        """
        Detects hands in the image.

        Args:
            frame (numpy.ndarray): Image in which to detect the hands.
            draw (bool, optional): Whether to draw the landmarks on the image. Defaults to False.

        Returns:
            numpy.ndarray: Image with the landmarks drawn if draw is True, else the original image.
        """
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
        self.detector.detect_async(mp_image, time.time_ns() // 1_000_000)

        return self.draw_landmarks(frame) if draw else frame

    def raised_fingers(self) -> list[int]:
        """
        Counts the number of raised fingers.

        Returns:
            list: List of 1s and 0s, where 1 indicates a raised finger and 0 indicates a lowered finger.
        """
        fingers = []
        if self.DETECTION_RESULT:
            for idx, hand_landmarks in enumerate(
                self.DETECTION_RESULT.hand_world_landmarks
            ):
                if self.DETECTION_RESULT.handedness[idx][0].category_name == "Right":
                    if (
                        hand_landmarks[self.tipIds[0]].x
                        > hand_landmarks[self.tipIds[0] - 1].x
                    ):
                        fingers.append(1)
                    else:
                        fingers.append(0)
                else:
                    if (
                        hand_landmarks[self.tipIds[0]].x
                        < hand_landmarks[self.tipIds[0] - 1].x
                    ):
                        fingers.append(1)
                    else:
                        fingers.append(0)

                for id in range(1, 5):
                    if (
                        hand_landmarks[self.tipIds[id]].y
                        < hand_landmarks[self.tipIds[id] - 2].y
                    ):
                        fingers.append(1)
                    else:
                        fingers.append(0)
        return fingers

    def get_approximate_depth(
        self, hand_idx: int = 0, width: int = 640, height: int = 480
    ) -> float:
        """
        Calculates the depth of each finger landmark.

        Returns:
            numpy.ndarray: Mean of the depth of each finger landmark.
        """
        if self.DETECTION_RESULT is not None:
            x1, y1 = (
                self.DETECTION_RESULT.hand_landmarks[hand_idx][5].x * width,
                self.DETECTION_RESULT.hand_landmarks[hand_idx][5].y * height,
            )
            x2, y2 = (
                self.DETECTION_RESULT.hand_landmarks[hand_idx][17].x * width,
                self.DETECTION_RESULT.hand_landmarks[hand_idx][17].y * height,
            )

            distance = math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
            A, B, C = self.coff
        
            return A * distance**2 + B * distance + C
        else:
            0

    def get_hand_world_landmarks(self, hand_idx: int = 0):
        """
        Returns the hand world landmarks.

        Args:
            hand_idx (int, optional): Index of the hand for which to return the landmarks. Defaults to 0.
            0 = Right hand
            1 = Left hand

        Returns:
            list: List of hand world landmarks.
        """
        return (
            self.DETECTION_RESULT.hand_world_landmarks[hand_idx]
            if self.DETECTION_RESULT is not None
            else []
        )

    def get_hand_landmarks(self, hand_idx: int = 0, idxs: list = None) -> list:
        """
        Returns the hand landmarks.

        Args:
            hand_idx (int, optional): Index of the hand for which to return the landmarks. Defaults to 0.
            0 = Right hand
            1 = Left hand
            idxs (list, optional): List of indices of the landmarks to return. Defaults to None.

        Returns:
            list: List of hand world landmarks.
        """
        if self.DETECTION_RESULT is not None:
            if idxs is None:
                return self.DETECTION_RESULT.hand_landmarks[hand_idx]
            else:
                return [
                    self.DETECTION_RESULT.hand_landmarks[hand_idx][idx] for idx in idxs
                ]
            
        else:
            return []

    def get_landmark_distance(self, idx1: int, idx2: int, hand_idx: int = 0):
        """
        Returns the distance between two landmarks.

        Args:
            idx1 (int): Index of the first landmark.
            idx2 (int): Index of the second landmark.
            hand_idx (int, optional): Index of the hand for which to return the landmarks. Defaults to 0.
            0 = Right hand
            1 = Left hand

        Returns:
            float: Distance between the two landmarks.
        """
        if self.DETECTION_RESULT is not None:
            x1, y1 = (
                self.DETECTION_RESULT.hand_landmarks[hand_idx][idx1].x,
                self.DETECTION_RESULT.hand_landmarks[hand_idx][idx1].y,
            )
            x2, y2 = (
                self.DETECTION_RESULT.hand_landmarks[hand_idx][idx2].x,
                self.DETECTION_RESULT.hand_landmarks[hand_idx][idx2].y,
            )
            return math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2), (x1, y1), (x2, y2)
        else:
            return tuple(0, 0, 0)
