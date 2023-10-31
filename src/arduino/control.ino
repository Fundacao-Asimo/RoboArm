#include <Servo.h>
#include <EEPROM.h>
#include "RoboServo.h");

#define SERVO_STEP 10
#define ROBOSERVO_MIN 0
#define ROBOSERVO_MAX 1

// Global variables:

enum Motor { Base , Reach , Height , Claw };
RoboServo servos[] = { RoboServo(8) , RoboServo(9) , RoboServo(10) , RoboServo(11) };

int current_motor = Motor::Base;

const int delay_loop = 5; // [ms]

// Note: the string sent by Python MUST be in the following formatting: 000 111 222 333 -> Base Reach Height Claw

int valueSent;

void setup() {
  // Configure the serial output
  Serial.begin(9600);
  #ifndef RESET_CONFIG
    Serial.println(F("Reading EEPROM configuration"));
    ReadConfig();
  #endif
  // Attach the servos and get the current angles
  for(int i=0 ; i <= Motor::Claw ; i++){
    servos[i].attach();
  }
}

void loop() {
  if (Serial.available()) {
    String str = Serial.readStringUntil('\n');
    if (str == "I"){
      Serial.println("Information: ");
      Serial.print(F("Left: "));
      Serial.print(F("Right: "));
      Serial.println(F("-----"));
      for (int x = 0; x < 4; x++) {
        Serial.print("[");
        Serial.print(x);
        Serial.print("] ");
        servos[x].printTo(Serial);
      }
    }
    if (str.length() == 15) {
      for (int i = 0; i <= Motor::Claw; i++) {
      	valueSent = str.substring(4*i, 4*i+3).toInt();
        int angle = servos[i].read();
        int aux = angle - valueSent;
        angle += aux;
        angle = AngleCorrection(static_cast<Motor>(i), angle); // Validate the angle
        servos[i].write(angle);
        delay(delay_loop / 5);
      }
     }
  }
  delay(delay_loop);
}

// Functions:

// Note: height = (1/a) * reach + b
#define ANGLE_CORRECTION_A -0.75
#define ANGLE_CORRECTION_B 165

#ifdef RESET_CONFIG
#define DISABLE_ANGLE_CORRECTION
#endif

// Correct the angle according to the motor
//  @params {motor, angle} : the motor being controlled [Motor], the angle being sent [int]
//  @returns the corrected angle [int]
int AngleCorrection(Motor motor, int angle) {
#ifndef DISABLE_ANGLE_CORRECTION
  if (motor == Height) {
    int max_angle = servos[Reach].read();
    max_angle = (float)max_angle * ANGLE_CORRECTION_A;
    max_angle += ANGLE_CORRECTION_B;
    if (angle < max_angle)
      angle = max_angle;
  } else if (motor == Reach) {
    int max_angle = servos[Height].read();
    max_angle -= ANGLE_CORRECTION_B;
    max_angle = (float)max_angle / ANGLE_CORRECTION_A;
    if(angle < max_angle)
      angle = max_angle;
  }
#endif // DISABLE_ANGLE_CORRECTION
  // Checks angle limits
  if (angle > servos[motor].getMAX())
    angle = servos[motor].getMAX();
  if (angle < servos[motor].getMIN())
    angle = servos[motor].getMIN();
  return angle;
}

//

#define EEPROM_ADDRESS_START      10
#define EEPROM_DEFAULT_MIN_BASE   10
#define EEPROM_DEFAULT_MIN_REACH  60
#define EEPROM_DEFAULT_MIN_HEIGHT 60
#define EEPROM_DEFAULT_MIN_CLAW   100
#define EEPROM_DEFAULT_MAX_BASE   170
#define EEPROM_DEFAULT_MAX_REACH  170
#define EEPROM_DEFAULT_MAX_HEIGHT 170
#define EEPROM_DEFAULT_MAX_CLAW   170

// Read the configuration data from the EEPROM
void ReadConfig(void) {
  int address = EEPROM_ADDRESS_START;
  byte v1 = EEPROM.read(address++);
  byte v2 = EEPROM.read(address++);
  bool blank = ((v1 == 131) && (v2 == 237)) ? false : true;
  if (blank) { // Writes data
    EEPROM.write(address++, EEPROM_DEFAULT_MIN_BASE);
    EEPROM.write(address++, EEPROM_DEFAULT_MIN_REACH);
    EEPROM.write(address++, EEPROM_DEFAULT_MIN_HEIGHT);
    EEPROM.write(address++, EEPROM_DEFAULT_MIN_CLAW);
    EEPROM.write(address++, EEPROM_DEFAULT_MAX_BASE);
    EEPROM.write(address++, EEPROM_DEFAULT_MAX_REACH);
    EEPROM.write(address++, EEPROM_DEFAULT_MAX_HEIGHT);
    EEPROM.write(address++, EEPROM_DEFAULT_MAX_CLAW);
    // Reset
    address = EEPROM_ADDRESS_START;
    EEPROM.write(address++, 131);
    EEPROM.write(address++, 237);
  }
  // Reads data
  servos[Base].setMIN(EEPROM.read(address++));
  servos[Reach].setMIN(EEPROM.read(address++));
  servos[Height].setMIN(EEPROM.read(address++));
  servos[Claw].setMIN(EEPROM.read(address++));
  servos[Base].setMAX(EEPROM.read(address++));
  servos[Reach].setMAX(EEPROM.read(address++));
  servos[Height].setMAX(EEPROM.read(address++));
  servos[Claw].setMAX(EEPROM.read(address++));
}

#undef EEPROM_ADDRESS_START
