
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


// Layout of the values stored in the EEPROM at word boundaries
#define EEPROM_AZMIN   0
#define EEPROM_AZMAX   2
#define EEPROM_ELMIN   4
#define EEPROM_ELMAX   6
#define EEPROM_SPEED   8
#define EEPROM_TIMEOUT 10



// ================= EEPROM READ/WRITE FUNCTIONS =====================


void initParamsFromEEPROM() {
  // Read all parameter values from EEPROM into global variables
  readAzServoMinMaxFromEEPROM();
  readElServoMinMaxFromEEPROM();
  readSpeedFromEEPROM();
  readTimeoutFromEEPROM();

  // Check for errors and set default values
  if ((AzServoMin < MINPW_MINVAL) || (AzServoMin > MINPW_MAXVAL)) {
    AzServoMin = AZMIN_DEFAULT;
    AzServoMax = AZMAX_DEFAULT;
    writeAzServoMinMaxToEEPROM();
  }
  if ((ElServoMin <= MINPW_MINVAL) || (ElServoMin > MINPW_MAXVAL)) {
    ElServoMin = ELMIN_DEFAULT;
    ElServoMax = ELMAX_DEFAULT;
    writeElServoMinMaxToEEPROM();
  }
  if ((curSpeed < SPEED_MIN) || (curSpeed > SPEED_MAX)) {
    curSpeed = SPEED_DEFAULT;
    writeSpeedToEEPROM(curSpeed);
  }
  if ((servoTimeout < TIMEOUT_MIN) || (servoTimeout > TIMEOUT_MAX)) {
    servoTimeout = TIMEOUT_DEFAULT;
    writeTimeoutToEEPROM(servoTimeout);
  }

  stepDelay = STEP_DELAY_EQUATION;
}


void readAzServoMinMaxFromEEPROM() {
  AzServoMin = readWordEEPROM(EEPROM_AZMIN);
  AzServoMax = readWordEEPROM(EEPROM_AZMAX);
}


void writeAzServoMinMaxToEEPROM() {
  writeWordEEPROM(EEPROM_AZMIN, AzServoMin);
  writeWordEEPROM(EEPROM_AZMAX, AzServoMax);
}


void readElServoMinMaxFromEEPROM() {
  ElServoMin = readWordEEPROM(EEPROM_ELMIN);
  ElServoMax = readWordEEPROM(EEPROM_ELMAX);
}


void writeElServoMinMaxToEEPROM() {
  writeWordEEPROM(EEPROM_ELMIN, ElServoMin);
  writeWordEEPROM(EEPROM_ELMAX, ElServoMax);
}


void readSpeedFromEEPROM() {
  curSpeed = readWordEEPROM(EEPROM_SPEED);
}


void writeSpeedToEEPROM(int newSpeed) {
  writeWordEEPROM(EEPROM_SPEED, newSpeed);
}


void readTimeoutFromEEPROM() {
  servoTimeout = readWordEEPROM(EEPROM_TIMEOUT);
}


void writeTimeoutToEEPROM(int newTimeout) {
  writeWordEEPROM(EEPROM_TIMEOUT, newTimeout);
}


void writeWordEEPROM(int addr, int intValue) {
  byte lsbValue = unsigned(intValue) & 0x00FF;
  byte msbValue = unsigned(intValue) >> 8;
  EEPROM.write(addr, lsbValue);
  EEPROM.write(addr+1, msbValue);
}


int readWordEEPROM(int addr) {
  byte lsbValue, msbValue;
  int intValue;
  lsbValue = EEPROM.read(addr);
  msbValue = EEPROM.read(addr+1);
  intValue = (msbValue << 8) + lsbValue;
  return intValue;
}


void writeDefaultsToEEPROM() {
  writeWordEEPROM(EEPROM_AZMIN, AZMIN_DEFAULT);
  writeWordEEPROM(EEPROM_AZMAX, AZMAX_DEFAULT);
  writeWordEEPROM(EEPROM_ELMIN, ELMIN_DEFAULT);
  writeWordEEPROM(EEPROM_ELMAX, ELMAX_DEFAULT);
  writeWordEEPROM(EEPROM_SPEED, SPEED_DEFAULT);
  writeWordEEPROM(EEPROM_TIMEOUT, TIMEOUT_DEFAULT);
}


// ================= END OF EEPROM ROUTINES =====================

//////////////////////////////////////////////////////////////////////////////////////
