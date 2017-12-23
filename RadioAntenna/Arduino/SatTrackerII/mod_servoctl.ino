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


/* ========================= SERVO CONTROL ROUTINES ========================= */

/*
 The program logic corresponds to commonly available toy RC servos. These 
 servos are capable of 180 degree end to end rotation, corresponding to 
 the minimum and maximum pulse width signals, typically between 500 and 2500 
 microseconds.

 So, to ensure proper operation, the MIN and MAX parameters have to be preset
 as part of the calibration process.
 
 The parameters AZMIN_DEFAULT, AZMAX_DEFAULT, ELMIN_DEFAULT, ELMAX_DEFAULT, 
 MINPW_MINVAL and MINPW_MAXVAL are defined in the main program file.

 If using different types of servos, the program may be have to be changed to 
 suit the specifications of the servos.
*/


// this function reinitializes the azimuth servo to updated min/max values
void reinitializeAzServo() {
  // save the new min/max parameters to EEPROM
  writeAzServoMinMaxToEEPROM();

  // set new min/max values for the servo attached
  AzServo.attach(PIN_AZSERVO,AzServoMin,AzServoMax);
  delay(20);

  // make sure the servo has aligned to the values
  MoveAzServo();
}


// this function reinitializes the elevation servo to updated min/max values
void reinitializeElServo() {
  // save the new min/max parameters to EEPROM
  writeElServoMinMaxToEEPROM();

  // set new min/max values for the servo attached
  ElServo.attach(PIN_ELSERVO,ElServoMin,ElServoMax);
  delay(20);

  // make sure the servo has aligned to the values
  MoveElServo();
}


// this function moves the azimuth servo by one degree in the correct direction
void MoveAzServo() {
  // calculate the next angle to move servo by 1 degree from its current position
  if (newAz > curAz) {
    curAz = curAz+1;
  }
  else if (newAz < curAz) {
    curAz = curAz-1;
  }

  // command the servo to move
  if (CCW_SERVOS)
    AzServo.write(curAz);
  else
    AzServo.write(180 - curAz);
}


// this function moves the elevation servo by one degree in the correct direction
void MoveElServo() {
  // calculate the next angle to move servo by 1 degree from its current position
  if (newEl > curEl) {
    curEl = curEl+1;
  }
  else if (newEl < curEl) {
    curEl = curEl-1;
  }

  // command the servo to move
  ElServo.write(curEl);
}

// ========================== END OF SERVO CONTROL ROUTINES =======================

//////////////////////////////////////////////////////////////////////////////////////
