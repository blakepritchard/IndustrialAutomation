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


// ===================== COMMON TEXT RESPONSE FUNCTIONS =====================

// Sends the version string back to the PC
void printVersionInfo() {
  Serial.println(VersionString);
}


// Sends the current azimuth angle back to the PC
void printCurrentAzimuth() {
    Serial.print("AZ");
    if (FlipAz == true)
      Serial.print((180 - curAz) + 180); // compensate for the 180 degree flip mode
    else
      Serial.print(180 - curAz);
}


// Sends the current elevation angle back to the PC
void printCurrentElevation() {
  Serial.print("EL");
  if (FlipAz == true)
    Serial.print(180 - curEl);   // compensate for the 180 degree flip mode
  else
    Serial.print(curEl);
}


// Sends the current values of the system parameters back to the PC
void printSetParameters() {
  Serial.println("System Parameters:");
  printAZServoParameters();
  Serial.println();
  printELServoParameters();
  Serial.println();
  printSpeedRPM();
  Serial.println();
  printTimeout();
  Serial.println();
}


// Sends the current parameters of the azimuth servo back to the PC
void printAZServoParameters() {
  Serial.print("AZ Servo Min/Max Pulse Widths (microseconds):");
  Serial.print(AzServoMin);
  Serial.print("/");
  Serial.print(AzServoMax);
}


// Sends the current parameters of the elevation servo back to the PC
void printELServoParameters() {
  Serial.print("EL Servo Min/Max Pulse Widths (microseconds):");
  Serial.print(ElServoMin);
  Serial.print("/");
  Serial.print(ElServoMax);
}


// Sends the current speed in rpm back to the PC
void printSpeedRPM() {
  Serial.print("Rotational Speed (rpm):");
  Serial.print(curSpeed);
}


// Sends the power timeout parameter in seconds, back to the PC
void printTimeout() {
  Serial.print("Servo Timeout (sec):");
  Serial.print(servoTimeout);
}

// ================== END OF TEXT RESPONSE FUNCTIONS ========================

//////////////////////////////////////////////////////////////////////////////////////
