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


// A simple EasyComm II Command Parser

// A command parser may be constructed in many ways, following  code represents a 
// very simple version that works by progressively splitting the command string 
// into words and by checking just the first 2 characters of the first word
//
// Understanding the angle swapping due to flip mode operation is a little bit
// difficult. The main project website listed above provides detailed explanation.



void parseCommands(){
  int n, iResult;
      str1.trim();
      str1.toUpperCase();
      while (str1 != "") {
        // extract one command word from input string (separator is SPACE)
        n = str1.indexOf(' ');
        if (n > 0) {
          str2 = str1.substring(0,n); // command word
          str1 = str1.substring(n+1); // remaining part of the command string
          str1.trim();
        }
        else {
          str2 = str1; // copy the last word
          str1 = "";   // clear command string
        }

        str2.trim();  // remove leading and trailing spaces


        // identify the command by checking the first two letters

        if (str2.startsWith("VE")) {
          // report version info
          printVersionInfo();
        }

        // --------------------------------------------------------------------

        else if (str2.startsWith("HE")) {
          // report help info
          printHelpInfo();
        }

        // --------------------------------------------------------------------

        else if (str2.startsWith("SA")) {
          // stop Azimuth rotation
          newAz = curAz;
          printCurrentAzimuth();
        }

        // --------------------------------------------------------------------

        else if (str2.startsWith("SE")) {
          // stop Elevation rotation
          newEl = curEl;
          printCurrentElevation();
        }

        // --------------------------------------------------------------------

        else if (str2.startsWith("AZ")) {
          // process AZ command
          str2 = str2.substring(2); // check for parameters
          if (str2 == "") {
            printCurrentAzimuth();  // if there are no parameters, respond with current azimuth
          }
          else {
            // process the move command, and respond with new position
            Serial.print("AZ");
            Serial.print(str2);

            // validate parameter value
            iResult = getInt(str2);  // convert string to integer
            if (iResult >= 0) {      // accept only positive converted values
              newAz = iResult;       // save it as the new target position
              while (newAz > 360) { newAz = newAz-360; } // map all angles 0 to 360 degrees

              // if AZ is more than 180, flip AZ servo
              if (newAz > 180) {
                newAz = newAz - 180;
                // and if necessary, also flip EL servo
                if (FlipAz == false) {
                  FlipAz = true;
                  newEl = 180 - newEl;
                }
              }
              else {
                // reset flip mode if it was previously set
                if (FlipAz == true) {
                  FlipAz = false;
                  newEl = 180 - newEl;  // flipback EL servo
                }
              }
              newAz = 180 - newAz;      // *** 180 deg flip for servo polarity ***
            }

            else {
              // ignore command if conversion failed (-1) and all negative values including overflow
            }
          }
        } // end of AZ command processing

        // --------------------------------------------------------------------

        else if (str2.startsWith("EL")) {
          str2 = str2.substring(2);
          if (str2 == "") {
            printCurrentElevation();
          }
          else {
            // process move command & respond with new position
            Serial.print("EL");
            Serial.print(str2);

            // save the new position as the target position
            iResult = getInt(str2);  // convert string to integer
            if (iResult >= 0) {
              newEl = iResult;  // accept only positive values
              while (newEl > 90) { newEl = newEl - 90; }  // map all angles to under 90 degrees
              if (FlipAz == true) newEl = 180 - newEl;   // 90 deg flip in flip mode
            }
            else{
              // ignore command if conversion failed (-1) and all negative values including overflow
            }
          }
        } // end of EL command processing

        // --------------------------------------------------------------------

        else if (str2.startsWith("SV")) {
          // take the whole comand line
          processSETcommands();  // uses globals str1 and str2
          str1 = "";
        } // end of SET command

        // --------------------------------------------------------------------

        else if (str2.startsWith("ECHO")) {
          //str2 = str2.substring(4);
          echoCmds = str1.equalsIgnoreCase("ON");
        } // end of ECHO command processing

        // --------------------------------------------------------------------

        else {
          // ignore the rest
          //Serial.print(str2);
          //Serial.print("? ");
        }

        // --------------------------------------------------------------------

        Serial.print(" ");

      } // end of while

}



// ======================== Command Processing Routines =======================



void processSETcommands() {

  Serial.println(str1); // first, echo the command back

  // --------------------------------------------------------------------

  // Command Syntax: SET AZPW min max
  if (str1.startsWith("AZPW")) {
    str1 = str1.substring(5);
    int n = str1.indexOf(' ');
    if (n > 0) {
      str2 = str1.substring(0,n); // get min
      str2.trim();
      str1 = str1.substring(n+1); // get max
      str1.trim();
      int newMin = getInt(str2);
      int newMax = getInt(str1);
      if ((newMin > 300) && (newMax < 3000) && (newMin < newMax)) {
        AzServoMin = newMin;
        AzServoMax = newMax;
        reinitializeAzServo(); // saves new value to EEPROM and reinitilizes servo library
      }
    }
    // send response
    printAZServoParameters();
  } // end of SET AZPW


  // --------------------------------------------------------------------

  // Command Syntax: SET ELPW min max
  else if (str1.startsWith("ELPW")) {
    str1 = str1.substring(5);
    int n = str1.indexOf(' ');
    if (n > 0) {
      str2 = str1.substring(0,n); // get min
      str2.trim();
      str1 = str1.substring(n+1); // get max
      str1.trim();
      int newMin = getInt(str2);
      int newMax = getInt(str1);
      if ((newMin > 300) && (newMax < 3000) && (newMin < newMax)) {
        ElServoMin = newMin;
        ElServoMax = newMax;
        reinitializeElServo(); // saves new value to EEPROM and reinitilizes servo library
      }
    }
    // send response
    printELServoParameters();
  } // end of SET ELPW


  // --------------------------------------------------------------------

  // Command Syntax: SET SPEED NNN
  else if (str1.startsWith("SPEED")) {
    str1 = str1.substring(6);  // as RPM
    str1.trim();
    if (str1 != "") {
      curSpeed = getInt(str1);
      // make sure values are within limits
      if (curSpeed < SPEED_MIN)
        curSpeed = SPEED_MIN;
      if (curSpeed > SPEED_MAX)
        curSpeed = SPEED_MAX;
      // update value in EEPROM
      stepDelay = STEP_DELAY_EQUATION;
      writeSpeedToEEPROM(curSpeed);
    }
    // send response
    printSpeedRPM();
    str1 = "";
  } // end of SET SPEED


  // --------------------------------------------------------------------

  // Command Syntax: SET TIMEOUT
  else if (str1.startsWith("TIMEOUT")) {
    str1 = str1.substring(8);  // as seconds
    str1.trim();
    if (str1 != "") {
      servoTimeout = getInt(str1);
      // make sure values are within limits
      if (servoTimeout < TIMEOUT_MIN)
        servoTimeout = TIMEOUT_MIN;
      if (servoTimeout > TIMEOUT_MAX)
        servoTimeout = TIMEOUT_MAX;
      // update value in EEPROM
      writeTimeoutToEEPROM(servoTimeout);
    }
    // send response
    printTimeout();
    str1 = "";
  } // end of SET TIMEOUT


  // --------------------------------------------------------------------

  // Command Syntax: SET DEFAULTS
  else if (str1.startsWith("DEFAULTS")) {
    writeDefaultsToEEPROM();
    Serial.print("Defaults loaded, restart the system");
  }


  // --------------------------------------------------------------------

  else if (str1 = "") {
    printSetParameters();
  }


  // --------------------------------------------------------------------

  // everything else is ignored
}



// ======================== End of Command Processing Routines =======================

//////////////////////////////////////////////////////////////////////////////////////
