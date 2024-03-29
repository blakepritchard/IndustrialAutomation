#!/usr/bin/python
'''
Created on Apr 14, 2021

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


#Adafruit Libraries for ADC
import busio
import digitalio
import board
from rpi_lcd import LCD

import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# Import Stepper
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit

# Import Local Class Libraries (RotaionalAxis)
path_runtime = os.path.dirname(__file__)
path_parent_version = os.path.abspath(os.path.join(path_runtime, os.pardir))
path_parent_platform = os.path.abspath(os.path.join(path_parent_version, os.pardir))
import RotationalAxis

                                                                                                                                                                     
class Rotator(object):

    _verbose = 0
    _is_busy = False
    
    _stepper_controller_A = 0
    _encoder_B = 0
    _adc = 0

    _steps_polarity_center = 0
    _steps_polarity_min = 0
    _steps_polarity_max = 10800

    _encoder_channel_polarity = 0
    _encoderposition_polarity_center = 28865
    _encoderposition_polarity_min = 26700
    _encoderposition_polarity_max = 36000
    
    # Hardware SPI configuration:
    SPI_PORT   = 0
    SPI_DEVICE = 0

    
    # Target
    _polarity_target = 0   

    #Position in Steps
    _polarity_stepper_count = 0
    _polarity_steps_per_degree = 30
    _polarity_degrees_per_step  = 1/_polarity_steps_per_degree
    _polarity_requires_calibration = True

    '''
    Constructor
    '''
    def __init__(self, logLevel):
        logging.basicConfig(filename='~/tuner_pi_rotator.log', filemode='w', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        logging.info("Initializing TunerPi Rotator")

        # Initialize LCD Display
        lcd = LCD()
        lcd.clear()
        lcd.text("TunerPi, Rev.1 ", 1)
        lcd.text("Copyright 2022", 2)
        lcd.text("Blake Pritchard", 3)
        lcd.text("www.blakesbots.com", 4)

        # create a default object, no changes to I2C address or frequency
        logging.info("Initializing Motor Hat A at I2C address: 0x6F")
        self._stepper_controller_A = MotorKit(i2c=board.I2C())


        # Analog To Digital Converter
        logging.info("Initializing ADC Hat on SPI bus")
        # create the spi bus
        spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        # create the cs (chip select)
        cs = digitalio.DigitalInOut(board.D22)
        # create the mcp object
        self._adc = MCP.MCP3008(spi, cs)
                                                             

        if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
            logging.basicConfig(level=logging.DEBUG)

        self._stepperPolarity = self._stepper_controller_A.stepper1  # motor port #1
        # self._stepperPolarity.setSpeed(10)                           # 10 RPM
                                
        logging.info(str(self._stepper_controller_A))
        self._Polarity = RotationalAxis.RotationalAxis("Polarity", self._stepperPolarity, self._polarity_steps_per_degree, self._adc,
                                                        self._steps_polarity_center, self._steps_polarity_min, self._steps_polarity_max, 
                                                        self._encoderposition_polarity_center, self._encoderposition_polarity_min, self._encoderposition_polarity_max)

        self._Polarity.recenter()

        atexit.register(self.turnOffMotors)
        self._is_busy = False

    def turnOffMotors(self):
        self._stepper_controller_A.stepper1.release()
        self._stepper_controller_A.stepper2.release()

    def set_verbosity(self, verbose):
        self._verbose = verbose

    def get_verbosity(self):
        return self._verbose



##########################################################################################
#    Protocol
##########################################################################################    
    def get_version_text(self):
        return "TunerPi - Version 1.0"
    
    def get_help_text(self):       
        return "Help Text Goes Here..."
    
    def get_unsupported_command_text(self):
        msg_text = "Unsupported Command..."
        logging.info(msg_text)
        return msg_text    

    def get_rotator_status(self):
        status_dict = {}
        status_dict["polarity_degrees"] = self._Polarity.get_degrees()
        status_dict["polarity_steps"] = self._Polarity.get_stepper_count()
        
        json_result = json.dumps(status_dict)
        logging.debug("Rotator Status: " + json_result)
        return json_result

    def execute_website_command(self, rotator_commands):  
        try:
            array_commands = rotator_commands.split(" ")               
            for rotator_command in array_commands: 
                logging.debug("Command: " + rotator_command)
                result = ""
                  
                #Stop  
                if("STOP" == rotator_command): 
                        self._Polarity.stop()
                        logging.debug("Received Stop Polarity Command")
                        lcd.clear()
                        lcd.text("Stop", 1)  
                            
                # Website uses short commands to Get values from the Rotator
                elif len(rotator_command) == 2:
                    if  "RS" == rotator_command:
                       result = str(self.get_rotator_status()) 
                       logging.debug("Received Rotator Status Request, Result: " + str(result)) 

                    elif "PO" == rotator_command: 
                        result_deg = str(self._Polarity.get_degrees())
                        result_steps = str(self._Polarity.get_stepper_count())
                        logging.debug("Received Polarity Request, Degrees: " + result_deg + ", Steps: " + result_steps)
                        lcd.clear()
                        lcd.text("Steps: " + str(result_steps), 1)
                        lcd.text("Degrees: " + str(result_deg), 2)

                    elif "SP" == rotator_command: 
                        self._Polarity.stop()
                        logging.debug("Received Stop Polarity Command")
                    elif "VE" == rotator_command: result = self.get_version_text()
                    elif "HE" == rotator_command: result = self.get_help_text()
                    
                # WebSite uses longer commands to Set values on the Rotator        
                elif len(rotator_command) > 2:
                    command_operation = rotator_command[:2]
                    command_parameters = rotator_command[2:]

                    if not self._is_busy:     
                        if "PO" == command_operation:
                            logging.info("Received Polarity Position Command: " + str(command_parameters))
                            result = self._Polarity.set_position(command_parameters)
                            logging.info("Returning Polarity Position: " + str(result))
                            lcd.clear()
                            lcd.text(str(result), 1)         
                    else:
                        result = "Busy"
                        logging.warning("Rotor is Busy Moving, Ignoring Command: " + str(rotator_command))
                        lcd.text("Busy, Ignoring: " +str(rotator_command), 1) 
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
        lcd.clear()
        lcd.text(e, 1)
        return 2
