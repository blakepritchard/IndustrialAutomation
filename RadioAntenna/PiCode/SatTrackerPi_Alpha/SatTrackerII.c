
/* ==========================================================================

Amateur Radio Satellite Tracking System using Arduino
by Umesh Ghodke
https://sites.google.com/site/k6vugdiary/

Copyright (C) 2012 Umesh Ghodke, Amateur Call Sign K6VUG

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software 
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, 
MA 02110-1301, USA.

The content is covered under the Creative Commons Attribution-ShareAlike 3.0 
License (http://creativecommons.org/licenses/by-sa/3.0/)

========================================================================== */


/* ==========================================================================

EasyComm II Commands Supported:

AZ      - report AZ position
AZnnn.n - move AZ to nnn.n degrees (0 to 360)
EL      - report EL position
ELnnn.n - move EL to nnn.n degrees (0 to 180)
SA      - stop Az rotation
SE      - stop El rotation

Additional Commands Supported:

VE           - show version of this program
HELP         - show list of commands and current parameter values
SV AZPW nnn nnnn - sets AZ servo MIN/MAX pulsewidths (in milliseconds)
SV ELPW nnn nnnn - sets EL servo MIN/MAX pulsewidths (in milliseconds)
SV SPEED nn - sets the turning SPEED (in rpm) for both servos
SV DEFAULTS - sets all parameters to default values
SV          - report values of all parameters
ECHO ON/OFF - turns echoing characters ON/OFF, used for debugging


Feature set:
- Steps Servos by 1 degree until target angle is reached
- EEPROM stores calibration settings & configuration values
- Flip Mode implemented to achieve Azimuth 0 to 360 and Elevation 0 to 180 angles
- Used millis() function for better timing
- Optimised text and string usage to reduce program size
- Implemented parking position for servos on reset (AZ=90, EL=90)
- Added handling of BACKSPACE and TAB characters in commands
- Added Auto Power ON/OFF to save stalled servos
- Added Support for CW (Hitec) and CCW (Futaba) servos

========================================================================== */



// ----------------------------- INCLUDED LIBRARIES ---------------------------

#include <Servo.h>
#include <EEPROM.h>


// ----------------------------- CONSTANT DECLARATIONS ---------------------------

// Arduino pin assignments for servos
#define PIN_AZSERVO       9
#define PIN_ELSERVO       6

// default min/max pulse widths in microseconds
// (servo library defaults are 544/2400)
#define AZMIN_DEFAULT   500
#define AZMAX_DEFAULT  2500
#define ELMIN_DEFAULT   500
#define ELMAX_DEFAULT  2500

// microseconds
#define MINPW_MINVAL    300
#define MINPW_MAXVAL    900

// rpm
#define SPEED_MIN         1
#define SPEED_MAX        50
#define SPEED_DEFAULT    10

// seconds
#define TIMEOUT_MIN       1
#define TIMEOUT_MAX     120
#define TIMEOUT_DEFAULT  15

// degrees
#define AZ_PARKPOS       90
#define EL_PARKPOS       90

// Set the following "true" for CCW (Futaba) servos, and "false" for CW (Hitec) servos
#define CCW_SERVOS    false

//
#define BAUDRATE       4800

// Macro to calculate milliseconds per degree, slowest=175ms(1rpm) thru fastest=10ms(15rpm)
#define STEP_DELAY_EQUATION (1000 / (6 * curSpeed))

// Version string
String VersionString = "EasyComm II AZ/EL Rotator Servo Controller v1.14\r\nDeveloped by Umesh Ghodke, K6VUG";



// -------------------------------- PROGRAM VARIABLES ----------------------------------

// Azimuth and Elevation servo programming objects
Servo AzServo, ElServo;  // create servo object instances

// Servo control configuration parameters, also stored to EEPROM
unsigned int AzServoMin, AzServoMax, ElServoMin, ElServoMax, curSpeed;

// Variables
unsigned int curAz, newAz; // servo positions
unsigned int curEl, newEl; // servo positions
unsigned int stepDelay;    // step delay in microseconds corresponding speed in RPM
boolean FlipAz = false;

boolean echoCmds = false;

boolean servoPowerON = false;
unsigned int servoTimeout;  // seconds

// Loop timing variables
unsigned long previousMillis = 0; // the millisecond when motors were last stepped
unsigned long currentMillis = 0;  // the current millisecond

// Temporary variables
String command, str1, str2, str3; // command string from input
char carray[8];                   // character array for string to int manipulation
char inByte;                      // input byte from serial port

// --------------------------------------------------------------------------------------




void setup() {
  // initialize serial comm
  Serial.begin(BAUDRATE);
  Serial.flush();

  // -----------------------------------------
  // read values stored in EEPROM
  initParamsFromEEPROM();
  // -----------------------------------------

  // initialize servos
  AzServo.attach(PIN_AZSERVO,AzServoMin,AzServoMax); // attaches the AZ servo to the servo object
  delay(10);
  ElServo.attach(PIN_ELSERVO,ElServoMin,ElServoMax); // attaches the EL servo to the servo object
  delay(10);

  // initialize variables
  curAz = AzServo.read();      // get current AZ servo position
  newAz = curAz;
  if (curAz != AZ_PARKPOS) newAz = AZ_PARKPOS; // park Az servo

  curEl = ElServo.read();      // get current EL servo position
  newEl = curEl;
  if (curEl != EL_PARKPOS) newEl = EL_PARKPOS; // park El servo

  FlipAz = false;

  servoPowerON = false;

  // initialize the digital pin as an output. Pin 13 has an LED connected on most Arduino boards
  pinMode(13, OUTPUT);
  digitalWrite(13, LOW);   // turn the LED off

  // init timing counters
  previousMillis = millis();
  currentMillis  = millis();
}




void loop() {
  // -----------------------------------------
  // check if there are any new commands
  checkSerialPort();
  // -----------------------------------------

  // step motors per specified stepDelay milliseconds
  currentMillis = millis();
  if ((currentMillis - previousMillis) > stepDelay) {
    if (newAz != curAz) {
      if (servoPowerON == false) {
        //Serial.println("Powering on servos");
        digitalWrite(13, HIGH);  // set the LED on
        servoPowerON = true;
      }
      MoveAzServo();
      previousMillis = currentMillis;  // save the last time you moved
    }

    if (newEl != curEl) {
      if (servoPowerON == false) {
        //Serial.println("Powering on servos");
        digitalWrite(13, HIGH);  // set the LED on
        servoPowerON = true;
      }
      MoveElServo();
      previousMillis = currentMillis;  // save the last time you moved
    }
  }

  if ((currentMillis - previousMillis) > (servoTimeout * 1000)) {
    // power OFF servos
    if (servoPowerON == true) {
      //Serial.println("Powering off servos");
      digitalWrite(13, LOW);   // set the LED off
      servoPowerON = false;
    }
  }

} // end of loop








// ====================== SERIAL COMMUNICATION FUNCTIONS ====================

void checkSerialPort() {
  int n;

  // check serial port for new data
  if (Serial.available() > 0) {

    inByte = Serial.read();
    if (echoCmds) Serial.write(inByte);  // echo the character back

    // Support BACKSPACE(8)
    if (inByte == 8) {
        n = command.length();
        if (n > 0)
          command = command.substring(0,n-1);
    }

    // Convert TAB(9), COMMA(44) to SPACE(32)
    else if (inByte == 9 || inByte == 44) {
      command.concat(32);
    }

    // letters(A-Z,a-z), numbers(0-9), SPACE(32), PERIOD(46)
    else if (inByte == 32 || inByte == 46 || (inByte >= 48 && inByte <=57) || (inByte >= 65 && inByte <= 90) || (inByte >=97 && inByte <=122)) {
      command.concat(inByte);
    }

    // Process command when NL/CR received
    else if (inByte == 10 || inByte == 13) {
      inByte = 0;

      //Parse and respond to commands
      str1 = command;
      command = "";  // clear the string to accept next command

      parseCommands();

      Serial.println("");

    } // end of CR LF check
  } // end of serial port check
}






// =========================== MATH FUNCTIONS =============================

int getInt(String text) {
  int x;
  str3 = text;
  str3.trim();
  if ((str3 != "") && (str3.charAt(0) >= '0') && (str3.charAt(0) <= '9')) {
    str3.toCharArray(carray, 7);
    x = atoi(carray);
  }
  else {
    x = -1;
  }
  return x;
}

//////////////////////////////////////////////////////////////////////////////////////
