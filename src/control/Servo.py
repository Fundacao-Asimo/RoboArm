from pyfirmata2 import Arduino


class Servo:
    """
    Class to control a servo motor.

    Attributes:
        ROBOSERVO_MIN (int): Index for the minimum angle of the servo
        ROBOSERVO_MAX (int): Index for the maximum angle of the servo

    Methods:
        get_limit(index): Get the limit of the servo at the given index
        set_limit(index, angle): Set the limit of the servo at the given index
        attach(): Attach the servo
        detach(): Detach the servo
        get_max(): Get the maximum angle of the servo
        set_max(angle): Set the maximum angle of the servo
        get_min(): Get the minimum angle of the servo
        set_min(angle): Set the minimum angle of the servo
        write(angle): Write the given angle to the servo
        read(): Read the current angle of the servo
        __str__(): Get the string representation of the servo
    """

    ROBOSERVO_MIN = 0
    ROBOSERVO_MAX = 1

    def __init__(self, board: Arduino, pin: int) -> None:
        """
        Initialize the Servo class.

        Args:
            board (Arduino): The Arduino board.
            pin (int): The pin of the servo.
        """
        self._limits = [0, 180]  # Default values
        self._pin = board.get_pin("d:{}:s".format(pin))
        self.angle = 0

    def get_limit(self, index: int) -> int:
        """
        Get the limit of the servo at the given index

        Args:
            index (int): The index of the limit to get (0 for min, 1 for max)

        Returns:
            int: The limit of the servo at the given index
        """
        index = max(0, min(index, Servo.ROBOSERVO_MAX))
        return self._limits[index]

    def set_limit(self, index: int, angle: int) -> None:
        """
        Set the limit of the servo at the given index

        Args:
            index (int): The index of the limit to set (0 for min, 1 for max)
            angle (int): The angle of the limit to set

        Returns:
            None
        """
        index = max(0, min(index, Servo.ROBOSERVO_MAX))
        angle = max(0, min(angle, 180))
        self._limits[index] = angle
        if self._limits[Servo.ROBOSERVO_MAX] < self._limits[Servo.ROBOSERVO_MIN]:
            self._limits[Servo.ROBOSERVO_MIN], self._limits[Servo.ROBOSERVO_MAX] = (
                self._limits[Servo.ROBOSERVO_MAX],
                self._limits[Servo.ROBOSERVO_MIN],
            )

    def attach(self, angle: int = None) -> None:
        """Attach the servo with the mean of the limits as the initial angle"""
        if angle is None:
            angle = sum(self._limits) // 2
        self.write(angle)

    def detach(self) -> None:
        """Detach the servo"""
        self._pin.write(0)

    def get_max(self) -> int:
        return self.get_limit(Servo.ROBOSERVO_MAX)

    def set_max(self, angle: int) -> None:
        self.set_limit(Servo.ROBOSERVO_MAX, angle)

    def get_min(self) -> int:
        return self.get_limit(Servo.ROBOSERVO_MIN)

    def set_min(self, angle: int) -> None:
        self.set_limit(Servo.ROBOSERVO_MIN, angle)

    def write(self, angle: int) -> None:
        angle = max(
            self._limits[Servo.ROBOSERVO_MIN],
            min(angle, self._limits[Servo.ROBOSERVO_MAX]),
        )
        if angle != self.angle:
            self._pin.write(angle)
            self.angle = angle

    def read(self) -> int:
        return self.angle

    def __str__(self):
        return "{} {{ {} ; {} ; {} }}".format(self._pin.is_output(), *self._limits)
