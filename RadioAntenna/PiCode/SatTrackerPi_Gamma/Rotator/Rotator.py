#!/usr/bin/python
'''
Created on Dec 18, 2017

@author: blake
'''
from __future__ import division
#from __future__ import builtins
#from builtins import len

import sys
import os
import time
import atexit
import logging

# Import Local Libraries
path_runtime = os.path.dirname(__file__)
path_parent_version = os.path.abspath(os.path.join(path_runtime, os.pardir))
path_parent_platform = os.path.abspath(os.path.join(path_parent_version, os.pardir))

path_lib_gpio = os.path.join(path_parent_platform, "Adafruit_Python_GPIO/Adafruit_GPIO/SPI.py")
path_lib_stepper = os.path.join(path_parent_platform, "Adafruit-Motor-HAT-Python-Library/Adafruit_MotorHAT/Adafruit_MotorHAT_Motors.py")
path_lib_adc = os.path.join(path_parent_platform, "Adafruit_Python_MCP3008/Adafruit_MCP3008/MCP3008.py")
path_lib_orientation = os.path.join(path_parent_platform, "Adafruit_Python_BNO055/dafruit_BNO055/BNO055.py")


sys.path.insert(0, os.path.abspath(path_lib_stepper))
sys.path.insert(0, os.path.abspath(path_lib_gpio))
sys.path.insert(0, os.path.abspath(path_lib_adc))
sys.path.insert(0, os.path.abspath(path_lib_orientation))

# Import Stepper
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

from Adafruit_BNO055 import BNO055


class Rotator(object):

    
    _encoder_A = 0
    _encoder_B = 0
    _adc = 0;
    _orientation = 0
    _stepperAzimuth = 0
    _stepperElevation = 0

    _cabletension_azimuth_center = 701
    _cabletension_azimuth_min = 640
    _cabletension_azimuth_max = 745

    # Hardware SPI configuration:
    SPI_PORT   = 0
    SPI_DEVICE = 0

    _bOrientationRunning = False
    

    _azimuth_current = 0
    _elevation_current = 0
    _polarity_current = 0
    
    _azimuth_target = 0
    _elevation_target = 0    
    _polarity_target = 0   
    
    _azimuth_stepper_count = 0
    _elevation_stepper_count = 0
    _polarity_stepper_count = 0
    
    _azimuth_stepper_calibration_offset = -90
    _elevation_stepper_calibration_offset = 0
    _polarity_stepper_calibration_offset = 0

    '''
    Constructor
    '''
    def __init__(self):

        # bottom hat is default address 0x60
        # create a default object, no changes to I2C address or frequency
        self._encoder_A = Adafruit_MotorHAT(addr=0x60)
        
        # top hat has A0 jumper closed, so its address 0x61
        self._encoder_B = Adafruit_MotorHAT(addr=0x61)

        # Analog Digital Converter
        self._adc = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(self.SPI_PORT, self.SPI_DEVICE))

        #Ultimate Orientation Sensor
        self._orientation = BNO055.BNO055(serial_port='/dev/serial0', rst=24)

        if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
            logging.basicConfig(level=logging.DEBUG)

        self._stepperAzimuth = self._encoder_A.getStepper(200, 1)     # 200 steps/rev, motor port #1
        self._stepperAzimuth.setSpeed(10)                             # 10 RPM

        self._stepperElevation = self._encoder_A.getStepper(200, 2)   # 200 steps/rev, motor port #2
        self._stepperElevation.setSpeed(10)                           # 10 RPM

        self._stepperPolarity = self._encoder_B.getStepper(200, 1)   # 200 steps/rev, motor port #1
        self._stepperElevation.setSpeed(10)                           # 10 RPM

        self.start_orientation_sensor()

        print str(self._encoder_A)
        print str(self._encoder_B)

        self.recenter_azimuth()
        self.recenter_elevation()

        atexit.register(self.turnOffMotors)               


            

    def turnOffMotors(self):
        self._encoder_A.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        self._encoder_A.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
        self._encoder_A.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
        self._encoder_A.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
      
    def get_elevation(self):
        print("returning elevation of: "+ str(self._elevation_current))
        return self._elevation_current
    
    def get_azimuth(self):
        print("returning azimuth of: "+ str(self._azimuth_current))
        return self._azimuth_current
    
    def get_polarity(self):
        print("returning polarity of: "+ str(self._polarity_current))
        return self._polarity_current

    def start_orientation_sensor(self):
        
        self._isOrientationRunning = False

        if not self._isOrientationRunning:
            nRetry = 6
            nSleepTime = 2
            while ((not self._isOrientationRunning) and (nRetry>0)):
                try:
                    self._isOrientationRunning = self._orientation.begin()  #Start BNO055 Orientation Sensor
                    
                except RuntimeError as error:
                    print("BNO055 Chip Not Initialized. Will Attempt in: " + str(nSleepTime) +" seconds. Attemps Left:" +str(nRetry))
                    print(type(error))    # the exception instance
                    print(error.args)     # arguments stored in .args
                    time.sleep(nSleepTime)
                          
                    nRetry = nRetry - 1
                    nSleepTime = nSleepTime*1.5
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    raise
                          
        if (not self._isOrientationRunning):
            raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')
        
        
        # Print system status and self test result.
        status, self_test, error = self._orientation.get_system_status()
        print('System status: {0}'.format(status))
        print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
        # Print out an error if system status is in error mode.
        if status == 0x01:
            print('Orientatin System error: {0}'.format(error))
            print('See BNO055 datasheet section 4.3.59 for the meaning.')

        # Print BNO055 software revision and other diagnostic data.
        sw, bl, accel, mag, gyro = self._orientation.get_revision()
        print('Software version:   {0}'.format(sw))
        print('Bootloader version: {0}'.format(bl))
        print('Accelerometer ID:   0x{0:02X}'.format(accel))
        print('Magnetometer ID:    0x{0:02X}'.format(mag))
        print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))   




##########################################################################################
# Elevation
##########################################################################################    
    def recenter_elevation(self):
        heading, roll, pitch = self._orientation.read_euler()
        while(roll < 0):
            self._stepperElevation.step(1, Adafruit_MotorHAT.BACKWARD,  Adafruit_MotorHAT.DOUBLE)
            heading, roll, pitch = self._orientation.read_euler()
            print("Elevation: " + str(roll))
        while(roll > 0):
            self._stepperElevation.step(1, Adafruit_MotorHAT.FORWARD,  Adafruit_MotorHAT.DOUBLE)
            heading, roll, pitch = self._orientation.read_euler()
            print("Elevation: " + str(roll))




    def set_elevation(self, elevation):
        try:       
            self._elevation_target = float(elevation)
            elevation_tuple = divmod(self._elevation_target, .25)
            elevation_remainder = float(elevation_tuple[1])
            
            #round down to nearest half degree
            elevation_target = float(self._elevation_target - elevation_remainder)
            
            #round back up if remainder was closer to upper bound
            if elevation_remainder > .125:
                elevation_target += .25

            #Move Up
            if elevation_target > self._elevation_current:
                nSteps = self.calculate_elevation_steps()
                print("Elevation Target: "+str(elevation_target)+"; Moving Elevation Upward by Estimated: " + str(nSteps) + " steps.")
                
                if(self._isOrientationRunning):
                    steps_actual = 0
                    azimuth_actual, elevation_actual, polarity_actual = self._orientation.read_euler()
                    while(elevation_target > elevation_actual):
                        self._stepperElevation.step(1, Adafruit_MotorHAT.BACKWARD,  Adafruit_MotorHAT.DOUBLE)
                        azimuth_actual, elevation_actual, polarity_actual = self._orientation.read_euler()
                        print("Elevation Actual: " + str(elevation_actual))
                        steps_actual = steps_actual +1
                    print("Actual Elevation Steps: "+ str(steps_actual))
                else:
                    self._stepperElevation.step(nSteps, Adafruit_MotorHAT.BACKWARD,  Adafruit_MotorHAT.DOUBLE)


            #Move Down    
            elif elevation_target < self._elevation_current:
                nSteps = self.calculate_elevation_steps()
                print("Elevation Target: "+str(elevation_target)+"; Moving Elevation Downward by Estimated: " + str(nSteps) + "steps.")

                if(self._isOrientationRunning):
                    steps_actual = 0
                    azimuth_actual, elevation_actual, polarity_actual = self._orientation.read_euler()
                    while(elevation_target < elevation_actual):
                        self._stepperElevation.step(1, Adafruit_MotorHAT.FORWARD,  Adafruit_MotorHAT.DOUBLE)
                        azimuth_actual, elevation_actual, polarity_actual = self._orientation.read_euler()
                        print("Elevation Actual: " + str(elevation_actual))
                        steps_actual = steps_actual +1
                    print("Actual Elevation Steps: "+ str(steps_actual))

                else:
                    self._stepperElevation.step(nSteps, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.DOUBLE)
                
            else:
                print("Holding Elevation Steady at: "+ str(elevation))

            # Set Elevation Value to Be Returned to GPredict
            if(self._isOrientationRunning):
                self._elevation_current = float(elevation_actual)
            else:
                self._elevation_current = float(elevation_target)
            
        except Exception as e:
            self.handle_exception(e)

    def calculate_elevation_steps(self):
        try:
            degrees = float(self._elevation_target) - float(self._elevation_current)
            print("Elevation Degrees:" + str(degrees))
            steps = abs(4 * int(degrees))
            return steps
        except Exception as e:
            self.handle_exception(e)

##########################################################################################
#    Azimuth
##########################################################################################
    def get_orientation_azimuth(self):
        azimuth_actual, elevation_actual, polarity_actual = self._orientation.read_euler()

        #this is a hack because I mounted the chip sideways
        print "Azimuth Raw: " + str(azimuth_actual) + "Azimuth Offset: " + str(self._azimuth_stepper_calibration_offset)
        azimuth_actual = azimuth_actual + self._azimuth_stepper_calibration_offset
        
        if azimuth_actual <0:
            azimuth_actual = 360 + azimuth_actual
        print "Azimuth Adusted: " + str(azimuth_actual)
        return azimuth_actual

    
    def recenter_azimuth(self):
        try:
            print("Recentering Azimuth")
            cabletension_current = self._adc.read_adc(0)

            print("Cable Tension = " + str(cabletension_current))

            nSteps = 0;
            while ((cabletension_current < self._cabletension_azimuth_center)
                and (cabletension_current < self._cabletension_azimuth_max)
                and (cabletension_current > self._cabletension_azimuth_min)):
                    nSteps+=1
                    self._stepperAzimuth.step(1, Adafruit_MotorHAT.FORWARD,  Adafruit_MotorHAT.DOUBLE)
                    cabletension_current = self._adc.read_adc(0)           

            
            while ((cabletension_current > self._cabletension_azimuth_center)
                and (cabletension_current < self._cabletension_azimuth_max)
                and (cabletension_current > self._cabletension_azimuth_min)):
                    nSteps-=1
                    self._stepperAzimuth.step(1, Adafruit_MotorHAT.BACKWARD,  Adafruit_MotorHAT.DOUBLE)
                    cabletension_current = self._adc.read_adc(0)

            print("Steps: " + str(nSteps))
                  
            self._azimuth_current = self.get_orientation_azimuth()   

        except Exception as e:
            self.handle_exception(e)

            
    def estimate_cable_tension_azimuth(self, target_azimuth, is_clockwise):
        cabletension_current = self._adc.read_adc(0)
        azimuth_actual = self.get_orientation_azimuth()

        target_is_safe = True
        degrees_travel = 0
        estimated_tension = 0
        tension_ratio = 180 / (self._cabletension_azimuth_max - self._cabletension_azimuth_min)

        if (is_clockwise):
            degrees_travel = target_azimuth - azimuth_actual
            if degrees_travel < 0:
                degrees_travel = 360 + degrees_travel
            estimated_tension_change = degrees_travel * tension_ratio
            estimated_tension_total = cabletension_current + estimated_tension_change
            print "Predicted CableTension Value: {estimated_tension}"
            if estimated_tension > self._cabletension_azimuth_max:
                target_is_safe = False
                print "Exceeds Maximum Value of {self._cabletension_azimuth_max}"
        else:
            degrees_travel = azimuth_actual - target_azimuth
            if degrees_travel < 0:
                degrees_travel = 360 + degrees_travel
            estimated_tension_change = degrees_travel * tension_ratio
            estimated_tension_total = cabletension_current - estimated_tension_change
            print "Predicted CableTension Value: {estimated_tension}"
            if estimated_tension < self._cabletension_azimuth_min:
                target_is_safe = False
                print "Exceeds Mainimum Value of {self._cabletension_azimuth_min}"

        return (target_is_safe, degrees_travel, estimated_tension)

    def calculate_azimuth_steps(self, degrees_travel):
        try:
            steps = abs(2 * int(degrees_travel))
            return steps            
        except Exception as e:
            self.handle_exception(e)

    def motor_direction_driver_const(self, is_clockwise):
        if True == is_clockwise:
            return Adafruit_MotorHAT.FORWARD
        else:
            return Adafruit_MotorHAT.BACKWARD
        

    def set_azimuth(self, azimuth):
        try:

            if(self._isOrientationRunning):
                #Find Nearest Half Degree Increment
                self._azimuth_target = float(azimuth)
                azimuth_tuple = divmod(self._azimuth_target, .5)
                azimuth_remainder = float(azimuth_tuple[1])
                
                #round down to nearest half degree
                azimuth_target_rounded = float(self._azimuth_target - azimuth_remainder)
                
                #round back up if remainder was closer to upper bound
                if azimuth_remainder > .25:
                    azimuth_target_rounded += .5

                #determine Motor Direction
                is_clockwise = True;
                if azimuth_target_rounded < self._azimuth_current:
                    is_clockwise = False;

                # check cable tension
                target_azimuth_is_safe, degrees_travel, estimated_tension = self.estimate_cable_tension_azimuth(azimuth_target_rounded, is_clockwise)
                if False == target_azimuth_is_safe:
                    print "Default Direction is Estimated to Exceed Cable Tension. Reversing Direction"
                    is_clockwise = not is_clockwise
                 
                #Move Stepper
                if azimuth_target_rounded != self._azimuth_current:
                    cabletension_current = self._adc.read_adc(0)
                    nSteps = self.calculate_azimuth_steps(degrees_travel)
                    print("Azimuth Target: " + str(azimuth_target_rounded) + "; Moving Azimuth  by Estimated: " + str(nSteps) + "steps.")


                    #Use Magnetic Compass on BNO055
                    steps_actual = 0
                    azimuth_actual = self.get_orientation_azimuth()

                    keep_moving = True
                    while(keep_moving):

                        if ((cabletension_current > _cabletension_azimuth_min) and (cabletension_current < self._cabletension_azimuth_max)):
                            motor_direction = self.motor_direction_driver_const(is_clockwise)
                            self._stepperAzimuth.step(1, motor_direction,  Adafruit_MotorHAT.DOUBLE)
                            azimuth_actual = self.get_orientation_azimuth()
                            cabletension_current = self._adc.read_adc(0)
                            print("Azimuth Actual: " + str(azimuth_actual) + ", CableTension: " + str(cabletension_current) + ", Direction: " + str(motor_direction))
                            steps_actual = steps_actual +1
                        else:
                            print "Target Cable Tension Maxed Out In Current Direction, Re-centering and Reversing Direction to unwind cable"
                            recenter_azimuth()
                            is_clockwise = not is_clockwise

                        # Update Object
                        self._azimuth_current = azimuth_actual
                        azimuth_current_rounded, azimuth_current_remainder = divmod(azimuth_actual, .5)
                        if azimuth_current_remainder > .25:
                            azimuth_current_rounded += .5

                        # Keep Moving ?
                        if azimuth_current_rounded  ==  azimuth_target_rounded:
                            print "Stopping Rotation at : " + str(azimuth_current_rounded)
                            keep_moving = False

                    print("Actual Azimuth Steps Forward: "+ str(steps_actual))


                else:
                    print("Holding Azimuth Steady at: "+ str(azimuth))

                # Set Azimuth Value to Be Returned to GPredict
                if(self._isOrientationRunning):
                    self._azimuth_current = float(azimuth_actual)
                else:
                    self._azimuth_current = float(azimuth_target)

            else:
                print "Orientation Sensor Not Running"

        except Exception as e:
            self.handle_exception(e)


                

    def stop_azimuth(self):
        try: 
            print("AZ Stop")
            self._encoder_A.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        except Exception as e:
            self.handle_exception(e)  


            
    
    def set_polarity(self, polarity):
        self._polarity_target = polarity
        '''ToDo: Remove this Hack'''
        print("setting polarity to: "+ str(polarity))
        self._polarity_current = polarity
        
    
      
        
    def stop_elevation(self):
        try:        
            print("EL Stop")
            self._encoder_A.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
            self._encoder_A.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
        except Exception as e:
            self.handle_exception(e)
            
    def get_version_text(self):
        return "SatTrackerPi - Version 1.0"
    
    def get_help_text(self):       
        return "Help Text Goes Here..."
    
    def get_unsupported_command_text(self):
        msg_text = "Unsupported Command..."
        print(msg_text)
        return msg_text
        
          
    def execute_easycomm2_command(self, rotator_commands):  

        try:
            array_commands = rotator_commands.split(" ")
            hash_results = {}
                
            for rotator_command in array_commands: 
                print("Command: " + rotator_command)
                result = ""
                    
                # EasyCommII uses short commands to Get values from the Rotator
                if len(rotator_command) == 2:
                    if      "AZ" == rotator_command: result = self.get_azimuth()
                    elif    "EL" == rotator_command: result = self.get_elevation()
                    elif    "SA" == rotator_command: result = self.stop_azimuth()
                    elif    "SE" == rotator_command: result = self.stop_elevation()
                    elif    "VE" == rotator_command: result = self.get_version_text()
                    elif    "HE" == rotator_command: result = self.get_help_text()
                    
                    # EasyCommII uses longer commands to Set values on the Rotator        
                elif len(rotator_command) > 2:
                    command_operation = rotator_command[:2]
                    command_parameters = rotator_command[2:]
                        
                    if "AZ" == command_operation:
                        print("Recieved Azimuth Command: " + str(command_parameters))
                        self.set_azimuth(command_parameters)
                    elif "EL" == command_operation:
                        print("Recieved Elevation Command: " + str(command_parameters))      
                        self.set_elevation(command_parameters)       

            return 0       
        
        except Exception as e:
            self.handle_exception(e)


    def handle_exception(self, e):
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            
            sys.stderr.write("Rotator.py: " + repr(e) + "\n")
            return 2
