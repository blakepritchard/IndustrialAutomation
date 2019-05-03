#!/usr/bin/python
'''
Created on Dec 18, 2017

@author: blake pritchard
'''
from __future__ import division
#from __future__ import builtins
#from builtins import len

import sys
import os
import time
import datetime
import math
import atexit
import logging
import json

# Import Local Libraries
path_runtime = os.path.dirname(__file__)
path_parent_version = os.path.abspath(os.path.join(path_runtime, os.pardir))
path_parent_platform = os.path.abspath(os.path.join(path_parent_version, os.pardir))

path_lib_gpio = os.path.join(path_parent_platform, "Adafruit_Python_GPIO/Adafruit_GPIO/SPI.py")
path_lib_stepper = os.path.join(path_parent_platform, "Adafruit-Motor-HAT-Python-Library/Adafruit_MotorHAT/Adafruit_MotorHAT_Motors.py")
path_lib_adc = os.path.join(path_parent_platform, "Adafruit_Python_MCP3008/Adafruit_MCP3008/MCP3008.py")

# Add Library Paths to Runtime Environment
sys.path.insert(0, os.path.abspath(path_lib_stepper))
sys.path.insert(0, os.path.abspath(path_lib_gpio))
sys.path.insert(0, os.path.abspath(path_lib_adc))

import RotationalAxis

# Import ADC (MCP3208) library.
from mcp3208 import MCP3208

# Import Stepper
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor

                                                                                                                                                                     
class Rotator(object):

    _verbose = 0
    _is_busy = False
    
    _encoder_A = 0
    _encoder_B = 0
    _adc = 0


    _steps_azimuth_center = 360
    _steps_azimuth_min = 0
    _steps_azimuth_max = 720

    _encoder_channel_azimuth = 0
    _encoderposition_azimuth_center = 2816
    _encoderposition_azimuth_min = 2489
    _encoderposition_azimuth_max = 3028

    _steps_elevation_center = 0
    _steps_elevation_min = 0
    _steps_elevation_max = 360

    _encoder_channel_elevation = 1
    _encoderposition_elevation_center = 1696
    _encoderposition_elevation_min = 1260
    _encoderposition_elevation_max = 1744

    _steps_polarity_center = 0
    _steps_polarity_min = 0
    _steps_polarity_max = 180

    _encoder_channel_polarity = 2
    _encoderposition_polarity_center = 3420
    _encoderposition_polarity_min = 3300
    _encoderposition_polarity_max = 3500
    

    # Hardware SPI configuration:
    SPI_PORT   = 0
    SPI_DEVICE = 0

    
    _azimuth_target = 0
    _elevation_target = 0    
    _polarity_target = 0   

    #Position in Steps
    _azimuth_stepper_count = 0
    _elevation_stepper_count = 0
    _polarity_stepper_count = 0

    _azimuth_steps_per_degree = 2
    _elevation_steps_per_degree = 4
    _polarity_steps_per_degree = 2

    _azimuth_degrees_per_step   = 1/_azimuth_steps_per_degree
    _elevation_degrees_per_step = 1/_elevation_steps_per_degree
    _polarity_degrees_per_step  = 1/_polarity_steps_per_degree

    _azimuth_requires_calibration = True
    _elevation_requires_calibration = True
    _polarity_requires_calibration = True

    '''
    Constructor
    '''
    def __init__(self):
        logging.info("Initializing SatTrackerPi Rotator")

        # bottom hat is default address 0x60
        # create a default object, no changes to I2C address or frequency
        self._encoder_A = Adafruit_MotorHAT(addr=0x60)
        
        # top hat has A0 jumper closed, so its address 0x61
        self._encoder_B = Adafruit_MotorHAT(addr=0x61)

        # Analog Digital Converter
        self._adc = MCP3208()


        if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
            logging.basicConfig(level=logging.DEBUG)

        self._stepperAzimuth = self._encoder_A.getStepper(200, 1)     # 200 steps/rev, motor port #1
        self._stepperAzimuth.setSpeed(10)                             # 10 RPM

        self._stepperElevation = self._encoder_A.getStepper(200, 2)   # 200 steps/rev, motor port #2
        self._stepperElevation.setSpeed(10)                           # 10 RPM

        self._stepperPolarity = self._encoder_B.getStepper(200, 1)   # 200 steps/rev, motor port #1
        self._stepperPolarity.setSpeed(10)                           # 10 RPM

        logging.info(str(self._encoder_A))
        logging.info(str(self._encoder_B))

        self._Azimuth = RotationalAxis.RotationalAxis("Azimuth", self._stepperAzimuth, self._azimuth_steps_per_degree, self._adc, self._encoder_channel_azimuth,
                                                        self._steps_azimuth_center, self._steps_azimuth_min, self._steps_azimuth_max, 
                                                        self._encoderposition_azimuth_center, self._encoderposition_azimuth_min, self._encoderposition_azimuth_max)

        self._Elevation = RotationalAxis.RotationalAxis("Elevation", self._stepperElevation, self._elevation_steps_per_degree, self._adc, self._encoder_channel_elevation,
                                                        self._steps_elevation_center, self._steps_elevation_min, self._steps_elevation_max, 
                                                        self._encoderposition_elevation_center, self._encoderposition_elevation_min, self._encoderposition_elevation_max)

        self._Polarity = RotationalAxis.RotationalAxis("Polarity", self._stepperPolarity, self._polarity_steps_per_degree, self._adc, self._encoder_channel_polarity,
                                                        self._steps_polarity_center, self._steps_polarity_min, self._steps_polarity_max, 
                                                        self._encoderposition_polarity_center, self._encoderposition_polarity_min, self._encoderposition_polarity_max)

        self._Elevation.reverse_movement()

        self._Azimuth.recenter()
        self._Elevation.recenter()
        self._Polarity.recenter()

        atexit.register(self.turnOffMotors)
        self._is_busy = False


    def turnOffMotors(self):
        self._encoder_A.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        self._encoder_A.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
        self._encoder_A.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
        self._encoder_A.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

        self._encoder_B.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        self._encoder_B.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
        self._encoder_B.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
        self._encoder_B.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
        self._is_busy = False

    def set_verbosity(self, verbose):
        self._verbose = verbose

    def get_verbosity(self):
        return self._verbose



##########################################################################################
#    Protocol
##########################################################################################    
    def get_version_text(self):
        return "SatTrackerPi - Version 1.0"
    
    def get_help_text(self):       
        return "Help Text Goes Here..."
    
    def get_unsupported_command_text(self):
        msg_text = "Unsupported Command..."
        logging.info(msg_text)
        return msg_text    

    def get_rotator_status(self):
        status_dict = {}
        status_dict["azimuth_degrees"] = self._Azimuth.get_degrees()
        status_dict["azimuth_steps"] = self._Azimuth.get_stepper_count()
        status_dict["elevation_degrees"] = self._Elevation.get_degrees()
        status_dict["elevation_steps"] = self._Elevation.get_stepper_count()
        status_dict["polarity_degrees"] = self._Polarity.get_degrees()
        status_dict["polarity_steps"] = self._Polarity.get_stepper_count()
        
        json_result = json.dumps(status_dict)
        logging.debug("Rotator Status: " + json_result)
        return json_result

    def execute_easycomm2_command(self, rotator_commands):  

        try:
            array_commands = rotator_commands.split(" ")
                
            for rotator_command in array_commands: 
                #logging.debug("Command: " + rotator_command)
                result = ""
                    
                # EasyCommII uses short commands to Get values from the Rotator
                if len(rotator_command) == 2:
                    if      "AZ" == rotator_command: result = str(self._Azimuth.get_degrees())
                    elif    "EL" == rotator_command: result = str(self._Elevation.get_degrees())
                    elif    "SA" == rotator_command: self._Azimuth.stop()
                    elif    "SE" == rotator_command: self._Elevation.stop()
                    elif    "VE" == rotator_command: result = self.get_version_text()
                    elif    "HE" == rotator_command: result = self.get_help_text()
                    
                # EasyCommII uses longer commands to Set values on the Rotator        
                elif len(rotator_command) > 2:
                    command_operation = rotator_command[:2]
                    command_parameters = rotator_command[2:]

                    if not self._is_busy:    
                        if "AZ" == command_operation:
                            logging.info("Recieved Azimuth Command: " + str(command_parameters))
                            self._Azimuth.set_position(command_parameters)
                        elif "EL" == command_operation:
                            logging.info("Recieved Elevation Command: " + str(command_parameters))      
                            self._Elevation.set_position(command_parameters)       
                    else:
                        logging.info("Rotor is Busy Moving, Ignoring Command: " + str(command_parameters))
            return result       
        
        except Exception as e:
            self.handle_exception(e)


    def execute_website_command(self, rotator_commands):  
        try:
            array_commands = rotator_commands.split(" ")               
            for rotator_command in array_commands: 
                logging.debug("Command: " + rotator_command)
                result = ""
                    
                # Website uses short commands to Get values from the Rotator
                if len(rotator_command) == 2:
                    if  "RS" == rotator_command:
                       result = str(self.get_rotator_status()) 
                       logging.debug("Received Rotator Status Request, Result: " + str(result)) 
                    elif    "AZ" == rotator_command: 
                        result = str(self._Azimuth.get_degrees())
                        logging.debug("Received Azimuth Request, Result: " + str(result))
                    elif    "EL" == rotator_command: 
                        result = str(self._Elevation.get_degrees())
                        logging.debug("Received Elevation Request, Result: " + str(result))
                    elif    "PO" == rotator_command: 
                        result = str(self._Polarity.get_degrees())
                        logging.debug("Received Polarity Request, Result: " + str(result))
                    elif    "SA" == rotator_command: 
                        self._Azimuth.stop()
                        logging.debug("Received Stop Azimuth Command")
                    elif    "SE" == rotator_command: 
                        self._Elevation.stop()
                        logging.debug("Received Stop Elevation Command")
                    elif    "SP" == rotator_command: 
                        self._Polarity.stop()
                        logging.debug("Received Stop Polarity Command")
                    elif    "VE" == rotator_command: result = self.get_version_text()
                    elif    "HE" == rotator_command: result = self.get_help_text()
                    
                # WebSite uses longer commands to Set values on the Rotator        
                elif len(rotator_command) > 2:
                    command_operation = rotator_command[:2]
                    command_parameters = rotator_command[2:]

                    if not self._is_busy:
                        if "AZ" == command_operation:
                            logging.info("Received Azimuth Command: " + str(command_parameters))
                            result = self._Azimuth.set_position(command_parameters)
                        elif "EL" == command_operation:
                            logging.info("Received Elevation Command: " + str(command_parameters))      
                            result = self._Elevation.set_position(command_parameters)       
                        elif "PO" == command_operation:
                            logging.info("Received Polarity Position Command: " + str(command_parameters))
                            result = self._Polarity.set_position(command_parameters)
                            logging.info("Returning Polarity Position: " + str(result))         
                    else:
                        result = "Busy"
                        logging.warning("Rotor is Busy Moving, Ignoring Command: " + str(rotator_command))
            return result       
        
        except Exception as e:
            self.handle_exception(e)


    def handle_exception(self, e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.critical(exc_type, fname, exc_tb.tb_lineno)
        logging.critical(e)
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
        
        sys.stderr.write("Rotator.py: " + repr(e) + "\n")
        return 2
