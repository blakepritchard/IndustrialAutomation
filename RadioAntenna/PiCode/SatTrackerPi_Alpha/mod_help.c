
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


// Help Strings Declaration

String HelpLine1  = "Servo outputs: AZ pin 9,EL pin 6";
String HelpLine2  = "Commands:";
String HelpLine3  = "VE(rsion)";
String HelpLine4  = "AZ[nnn.n] (0-360)";
String HelpLine5  = "EL[nn.n]  (0-90)";
String HelpLine6  = "SA (stop AZ)";
String HelpLine7  = "SE (stop EL)";

String HelpLine8  = "HE(lp)";
String HelpLine9  = "SV (set/show values)";
String HelpLine10 = "SV AZPW|ELPW nnn nnnn (min max ms)";
String HelpLine11 = "SV SPEED nn (1-50 rpm)";
String HelpLine12 = "SV TIMEOUT nn (secs)";
String HelpLine13 = "SV DEFAULTS";
String HelpLine14 = "ECHO ON/OFF";



// Respond with the help strings organised as a help page

void printHelpInfo() {
  Serial.println(VersionString);
  Serial.println();
  Serial.println(HelpLine1);
  Serial.println();
  Serial.println(HelpLine2);
  Serial.println(HelpLine3);
  Serial.println(HelpLine4);
  Serial.println(HelpLine5);
  Serial.println(HelpLine6);
  Serial.println(HelpLine7);
  Serial.println(HelpLine8);
  Serial.println(HelpLine9);
  Serial.println(HelpLine10);
  Serial.println(HelpLine11);
  Serial.println(HelpLine12);
  Serial.println(HelpLine13);
  Serial.println(HelpLine14);
  Serial.println();
  printSetParameters();
}

// ----------------------------------------------------------------------------

//////////////////////////////////////////////////////////////////////////////////////
