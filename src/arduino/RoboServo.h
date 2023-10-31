#ifndef ROBOSERVO_H
#define ROBOSERVO_H


#define ROBOSERVO_MIN 0
#define ROBOSERVO_MAX 1

#include <Servo.h>

class RoboServo : public Printable, public Servo {
    private:
        int _limits[2]; // [min, max]
        int _pin;
        // Get an angle limit
        // @params {index}: the desired limit [byte]
        // @returns [int]
        int getLimit(byte index) {
            if (index == ROBOSERVO_MAX)
                return _limits[ROBOSERVO_MAX];
            else
                return _limits[ROBOSERVO_MIN];
        }
        // Set an agle limit
        // @ params {index, angle}: the desired limit [byte], the desired angle [int]
        // @returns [void]
        void setLimit(byte index, int angle) {
            // Checks the index
            if (index > ROBOSERVO_MAX)
                return;
            // Limits the angle value
            if (angle < 0)
                angle = 0;
            if (angle > 180)
                angle = 180;
            _limits[index] = angle;
            // If necessary, changes the limits
            if (_limits[ROBOSERVO_MAX] < _limits[ROBOSERVO_MIN]) {
                int aux = _limits[ROBOSERVO_MIN];
                _limits[ROBOSERVO_MIN] = _limits[ROBOSERVO_MAX];
                _limits[ROBOSERVO_MAX] = aux;
            }
        }
    public:
        // Constructor
        RoboServo(int pin) : Servo() {
            _limits[ROBOSERVO_MIN] = 0;   // Default value
            _limits[ROBOSERVO_MAX] = 180; // Default value
            _pin = pin;
            pinMode(_pin, INPUT);         // Turns the pin an input
        }
        // Attach the servo to the predefined pin
        // @params {void}
        // @returns [uint8_t]
        uint8_t attach() {
            uint8_t res = Servo::attach(_pin);
            int mean = _limits[ROBOSERVO_MIN] + _limits[ROBOSERVO_MAX];
            mean /= 2;
            Servo::write(mean); // Default angle
            return res;
        }
        // Get the MAX limit
        // @params {void}
        // @returns [int]
        int getMAX() {
            return getLimit(ROBOSERVO_MAX);
        }
        // Set the MAX limit
        // @params {angle}: the maximum angle [int]
        // @returns [void]
        void setMAX(int angle) {
            return setLimit(ROBOSERVO_MAX, angle);
        }
        // Get the MIN limit
        // @params {void}
        // @returns [int]
        int getMIN() {
            return getLimit(ROBOSERVO_MIN);
        }
        // Set the MIN limit
        // @params {angle}: the minimum angle [int]
        // @returns [void]
        void setMIN(int angle) {
            return setLimit(ROBOSERVO_MIN, angle);
        }
        // Writes the angle
        // @params {angle}: the desired angle [int]
        // @returns [void]
        void write(int angle) {
            if (angle < _limits[ROBOSERVO_MIN])
                angle = _limits[ROBOSERVO_MIN];
            if (angle > _limits[ROBOSERVO_MAX])
                angle = _limits[ROBOSERVO_MAX];
            Servo::write(angle);
        }
        // Overrides the print method
        // @params {print}: object of Print
        // @returns [size_t]
        size_t printTo(Print &print) const {
            size_t size = 0;
            size += print.print(attached());
            size += print.print(F(" { "));
            size += print.print(_limits[ROBOSERVO_MIN]);
            size += print.print(F(" ; "));
            size += print.print(read());
            size += print.print(F(" ; "));
            size += print.print(_limits[ROBOSERVO_MAX]);
            size += print.println(F(" }"));
            return size;
        }
};

#endif

