import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, root_dir)

from pyfirmata2 import Arduino
from src.control.RoboArm import RoboArm


def main() -> None:

    port = input("Enter port: ").strip()
    board = Arduino(port)
    arm = RoboArm(board)

    while True:
        try:
            base = input("Enter base angle: ").strip()
            reach = input("Enter reach angle: ").strip()
            height = input("Enter height angle: ").strip()
            claw = input("Enter claw angle: ").strip()

            arm.control_servos(int(base), int(reach), int(height), int(claw))

            print(arm.servos["Base"].read())
            print(arm.servos["Reach"].read())
            print(arm.servos["Height"].read())
            print(arm.servos["Claw"].read())
        except KeyboardInterrupt:
            break

    arm.close()


if __name__ == "__main__":
    main()
