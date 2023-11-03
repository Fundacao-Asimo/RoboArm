import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, root_dir)

from pyfirmata2 import Arduino
from src.control.Servo import Servo


def main() -> None:
    port = input("Enter port: ").strip()
    pin = int(input("Enter pin: ").strip())

    board = Arduino(port)
    servo = Servo(board, pin)

    while True:
        try:
            i = input("Enter angle: ").strip()

            if i == "q":
                print("finished")
                break

            servo.write(int(i))

            print(servo.read())
        except KeyboardInterrupt:
            break
    servo.detach()


if __name__ == "__main__":
    main()
