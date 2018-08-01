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

# Import Local Libraries
path_runtime = os.path.dirname(__file__)
path_parent_version = os.path.abspath(os.path.join(path_runtime, os.pardir))
path_parent_platform = os.path.abspath(os.path.join(path_parent_version, os.pardir))

path_lib_gpio = os.path.join(path_parent_platform, "Adafruit_Python_GPIO/Adafruit_GPIO/SPI.py")
path_lib_stepper = os.path.join(path_parent_platform, "Adafruit-Motor-HAT-Python-Library/Adafruit_MotorHAT/Adafruit_MotorHAT_Motors.py")
path_lib_adc = os.path.join(path_parent_platform, "Adafruit_Python_MCP3008/Adafruit_MCP3008/MCP3008.py")


sys.path.insert(0, os.path.abspath(path_lib_stepper))
sys.path.insert(0, os.path.abspath(path_lib_gpio))
sys.path.insert(0, os.path.abspath(path_lib_adc))

# Import Stepper
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008


class Rotator(object):

    # create a default object, no changes to I2C address or frequency
    _encoder_A = 0
    _stepperAzimuth = 0
    _stepperElevation = 0

    _cabletension_azimuth_center = 701
    _cabletension_azimuth_min = 640
    _cabletension_azimuth_max = 745

    # Hardware SPI configuration:
    SPI_PORT   = 0
    SPI_DEVICE = 0
    _adc = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

    # this line was for the hobby servo motors
    # _pwm = Adafruit_PCA9685.PCA9685()

    _azimuth_current = 0
    _elevation_current = 0
    _polarity_current = 0
    
    _azimuth_target = 0
    _elevation_target = 0    
    _polarity_target = 0   
    
    _azimuth_stepper_count = 0
    _elevation_stepper_count = 0
    _polarity_stepper_count = 0
    
    _azimuth_stepper_calibration_offset = 0
    _elevation_stepper_calibration_offset = 0
    _polarity_stepper_calibration_offset = 0

    '''
    Constructor
    '''
    def __init__(self):

        # bottom hat is default address 0x60
        self._encoder_A = Adafruit_MotorHAT(addr=0x60)
        
        # top hat has A0 jumper closed, so its address 0x61
        self._encoder_B = Adafruit_MotorHAT(addr=0x61)

        self._stepperAzimuth = self._encoder_A.getStepper(200, 1)     # 200 steps/rev, motor port #1
        self._stepperAzimuth.setSpeed(10)                             # 10 RPM

        self._stepperElevation = self._encoder_A.getStepper(200, 2)   # 200 steps/rev, motor port #2
        self._stepperElevation.setSpeed(10)                           # 10 RPM

        self._stepperPolarity = self._encoder_B.getStepper(200, 1)   # 200 steps/rev, motor port #1
        self._stepperElevation.setSpeed(10)                           # 10 RPM

        print str(self._encoder_A)
        print str(self._encoder_B)

        self.recenter_azimuth();

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

    def recenter_azimuth(self):
        try:
            cabletension_current = mcp.read_adc(1)

             while (cabletension_current < _cabletension_azimuth_center) and (cabletension_current < _cabletension_azimuth_max) and (cabletension_current > _cabletension_azimuth_min):
                self._stepperAzimuth.step(1, Adafruit_MotorHAT.FORWARD,  Adafruit_MotorHAT.DOUBLE)
                cabletension_current = mcp.read_adc(1)           
 
            while (cabletension_current > _cabletension_azimuth_center) and (cabletension_current < _cabletension_azimuth_max) and (cabletension_current > _cabletension_azimuth_min):
                self._stepperAzimuth.step(1, Adafruit_MotorHAT.BACKWARD,  Adafruit_MotorHAT.DOUBLE)
                cabletension_current = mcp.read_adc(1)

                self._azimuth_current = 0    

        except Exception as e:
            self.handle_exception(e)

    
    def set_elevation(self, elevation):
        try:       
            self._elevation_target = float(elevation)
            
            elevation_remainder = divmod(self._elevation_target, .25)
            
            #round down to nearest half degree
            elevation_increment = self._elevation_target - elevation_remainder
            
            #round back up if remainder was closer to upper bound
            if elevation_remainder > .125:
                elevation_increment += .25

            if self._elevation_target < self._elevation_current:
                nSteps = self.calculate_elevation_steps()
                print("Moving Elevation Upward by: " + str(nSteps) + "steps.")
                self._stepperElevation.step(nSteps, Adafruit_MotorHAT.BACKWARD,  Adafruit_MotorHAT.DOUBLE)

                
            elif self._elevation_target > self._elevation_current:
                nSteps = self.calculate_elevation_steps()
                print("Moving ElevationAzimuth Downward by: " + str(nSteps) + "steps.")
                self._stepperElevation.step(nSteps, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.DOUBLE)
                
            else:
                print("Holding Elevation Steady at: "+ str(elevation))
                      
            self._elevation_current = float(elevation_increment)
            
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

    
    def set_azimuth(self, azimuth):
        try:
            #Find Nearest Half Degree Increment
            self._azimuth_target = float(azimuth)
            azimuth_remainder = divmod(self._azimuth_target, .5)
            
            #round down to nearest half degree
            azimuth_increment = self._azimuth_target - azimuth_remainder
            
            #round back up if remainder was closer to upper bound
            if azimuth_remainder > .25:
                azimuth_increment += .5
             
 
            if self.azimuth_increment > self._azimuth_current:
                cabletension_current = mcp.read_adc(1)
                if cabletension < _cabletension_azimuth_max:
                    nSteps = self.calculate_azimuth_steps()
                    print("Moving Azimuth Forward by: " + str(nSteps) + "steps.")
                    self._stepperAzimuth.step(nSteps, Adafruit_MotorHAT.FORWARD,  Adafruit_MotorHAT.DOUBLE)
                else:
                    recenter_azimuth()
                
            elif self.azimuth_increment < self._azimuth_current:
                if cabletension > _cabletension_azimuth_min:
                    nSteps = self.calculate_azimuth_steps()
                    print("Moving Azimuth Backward by: " + str(nSteps) + "steps.")
                    self._stepperAzimuth.step(nSteps, Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.DOUBLE)
                else:
                    recenter_azimuth()
            else:
                print("Holding Azimuth Steady at: "+ str(azimuth))

            self._azimuth_current = float(azimuth_increment)

        except Exception as e:
            self.handle_exception(e)


    def calculate_azimuth_steps(self):
        try:
            degrees = float(self._azimuth_target) - float(self._azimuth_current)
            steps = abs(2 * int(degrees))
            return steps            
        except Exception as e:
            self.handle_exception(e)
            
    
    def set_polarity(self, polarity):
        self._polarity_target = polarity
        '''ToDo: Remove this Hack'''
        print("setting polarity to: "+ str(polarity))
        self._polarity_current = polarity
        
    
    def stop_azimuth(self):
        try: 
            print("AZ Stop")
            self._encoder_A.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        except Exception as e:
            self.handle_exception(e)        
        
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
                        
                    if      "AZ" == command_operation:
                                print("Recieved Azimuth Command: " + str(command_parameters))
                                self.set_azimuth(command_parameters)
                    elif    "EL" == command_operation:
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
