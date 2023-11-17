import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, root_dir)

from pyfirmata2 import Arduino
from src.control.Servo import Servo


class RoboArm:
    """
    Class to control the RoboArm of RoboCore

    Attributes:
        servos (dict): Dictionary of servos with the name as the key and the servo object as the value
        PIN_BASE (int): Pin number for the base servo
        PIN_REACH (int): Pin number for the reach servo
        PIN_HEIGHT (int): Pin number for the height servo
        PIN_CLAW (int): Pin number for the claw servo
        SERVOS_LIMITS (dict): Dictionary of servo names and their limits as a list. The order is Base, Reach, Height, Claw

    Methods:
        control_servos(base: int, reach: int, height: int, claw: int): Control the servos by name
        print_servo_info(name: str): Print the servo info to the console
        get_servo_info(name: str): Get the servo info as a string
        close(): Close all the servos
    """

    PIN_BASE = 8
    PIN_REACH = 9
    PIN_HEIGHT = 10
    PIN_CLAW = 11

    SERVOS_LIMITS = {
        "Base": [10, 170],
        "Reach": [60, 160],
        "Height": [70, 170],
        "Claw": [100, 170],
    }

    ANGLE_CORRECTION_A = -0.75
    ANGLE_CORRECTION_B = 165

    def __init__(self, board: Arduino) -> None:
        self.servos = {
            "Base": Servo(board, self.PIN_BASE),
            "Reach": Servo(board, self.PIN_REACH),
            "Height": Servo(board, self.PIN_HEIGHT),
            "Claw": Servo(board, self.PIN_CLAW),
        }
        self.initialize_sensors()

    def initialize_sensors(self) -> None:
        for name, limits in self.SERVOS_LIMITS.items():
            self.servos[name].set_limit(0, limits[0])
            self.servos[name].set_limit(1, limits[1])
            if name == "Base":
                self.servos[name].attach(60)
            else:
                self.servos[name].attach()

    def control_servos(self, base: int, reach: int, height: int, claw: int) -> None:
        """
        Control a servo by name

        Args:
            base (int): Base servo angle
            reach (int): Reach servo angle
            height (int): Height servo angle
            claw (int): Claw servo angle

        Returns:
            None
        """
        self.control_servo("Base", base)
        self.control_servo("Reach", reach)
        self.control_servo("Height", height)
        self.control_servo("Claw", claw)

    def control_servo(self, name: str, angle: int) -> None:
        """
        Control a servo by name

        Args:
            name (str): Name of the servo to control
            angle (int): Angle to set the servo to

        Returns:
            None
        """
        if name in self.servos:
            if name == "Height":
                max_angle = self.servos["Reach"].read()
                max_angle = (
                    float(max_angle * self.ANGLE_CORRECTION_A) + self.ANGLE_CORRECTION_B
                )
                if angle < max_angle:
                    angle = max_angle
            elif name == "Reach":
                max_angle = self.servos["Height"].read()
                max_angle = (
                    float(max_angle) - self.ANGLE_CORRECTION_B
                ) / self.ANGLE_CORRECTION_A
                if angle < max_angle:
                    angle = max_angle
            self.servos[name].write(angle)

    def get_servo_info(self, name: str) -> str:
        """
        Get the servo info as a string

        Args:
            name (str): Name of the servo to get info for

        Returns:
            str: Servo info
        """
        if name in self.servos:
            return str(self.servos[name])

    def close(self) -> None:
        """
        Close all the servos

        Args:
            None

        Returns:
            None
        """
        for servo in self.servos.values():
            servo.detach()

    def __str__(self) -> str:
        board_info = self.board.__name__
        servos_info = ", ".join([str(servo) for servo in self.servos.values()])
        return "{} {{ {} }}".format(board_info, servos_info)
