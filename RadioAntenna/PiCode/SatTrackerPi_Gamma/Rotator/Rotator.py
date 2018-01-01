'''
Created on Dec 18, 2017

@author: blake
'''
from __future__ import division
#from __future__ import builtins


import sys
import os
import time

#from builtins import len



# Import Local Libraries
path_runtime = os.path.dirname(__file__)
path_parent_version = os.path.abspath(os.path.join(path_runtime, os.pardir))
path_parent_platform = os.path.abspath(os.path.join(path_parent_version, os.pardir))
path_lib_servo = os.path.join(path_parent_platform, "Adafruit_Python_PCA9685/Adafruit_PCA9685/PCA9685.py")
path_lib_stepper = os.path.join(path_parent_platform, "Adafruit-Motor-HAT-Python-Library/Adafruit_MotorHAT/Adafruit_MotorHAT_Motors.py")

sys.path.insert(0, os.path.abspath(path_lib_servo))
sys.path.insert(0, os.path.abspath(path_lib_stepper))

# Import the PCA9685 module.
import Adafruit_PCA9685


#!/usr/bin/python
#import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_Stepper
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor

import time
import atexit

# create a default object, no changes to I2C address or frequency
mh = Adafruit_MotorHAT()


class Rotator(object):

    _pwm = Adafruit_PCA9685.PCA9685()

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


    # Configure min and max servo pulse lengths
    _servo_min = 150  # Min pulse length out of 4096
    _servo_max = 600  # Max pulse length out of 4096
    _servo_center = 325
            
    
    '''
    classdocs
    '''

    '''
    Constructor
    '''
    def __init__(self):

        """
        # Initialise the PCA9685 using the default address (0x40).

        # Set frequency to 50hz, good for servos.
        self._pwm.set_pwm_freq(50)
        
        #Reset Servos to Center with a 1500us pulse
        self._pwm.set_pwm(0, 0, self._servo_center)
        time.sleep(1)
        self._pwm.set_pwm(1, 0, self._servo_center)
        time.sleep(1)
        """
        
        atexit.register(turnOffMotors)

        myStepper = mh.getStepper(200, 1)  # 200 steps/rev, motor port #1
        myStepper.setSpeed(30)             # 30 RPM
                

       
    def get_elevation(self):
        print("returning elevation of: "+ str(self._elevation_current))
        return self._elevation_current
    
    def get_azimuth(self):
        print("returning azimuth of: "+ str(self._azimuth_current))
        return self._azimuth_current
    
    def get_polarity(self):
        print("returning polarity of: "+ str(self._polarity_current))
        return self._polarity_current
    
    
    def set_elevation(self, elevation):
        try:       
            self._elevation_target = elevation
            '''ToDo: Remove this Hack'''
            
            pulse_width = int((self._servo_center + ((self._servo_max - self._servo_center) * (float(elevation)/90.0))) /2 )
            print("setting elevation to: "+ str(elevation)+" with a pulse width of: "+ str(pulse_width))
            self._pwm.set_pwm(1, 0, pulse_width)
            self._elevation_current = enumerate
            
        except Exception as e:
            self.handle_exception(e)
    
    def set_azimuth(self, azimuth):
        try:
            self._azimuth_target = azimuth
            '''ToDo: Remove this Hack'''
            
            pulse_width = int((self._servo_center + ((self._servo_max - self._servo_center) * (float(azimuth)/180.0))) /2 )
            print("setting elevation to: "+ str(azimuth)+" with a pulse width of: "+ str(pulse_width))
            self._pwm.set_pwm(0, 0, pulse_width)
            self._azimuth_current = azimuth

        except Exception as e:
            self.handle_exception(e)
    
    def set_polarity(self, polarity):
        self._polarity_target = polarity
        '''ToDo: Remove this Hack'''
        print("setting polarity to: "+ str(polarity))
        self._polarity_current = polarity
        
    
    def stop_azimuth(self):
        try:
            self._pwm.set_pwm(0, 0, self._servo_center)        
            print("AZ Stop")
        except Exception as e:
            self.handle_exception(e)        
        
    def stop_elevation(self):
        try:
            self._pwm.set_pwm(1, 0, self._servo_center)        
            print("EL Stop")
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
    
    
    # Helper function to make setting a servo pulse width simpler.
    def set_servo_pulse(self, channel, pulse):
        pulse_length = 1000000    # 1,000,000 us per second
        pulse_length //= 60       # 60 Hz
        print('{0}us per period'.format(pulse_length))
        pulse_length //= 4096     # 12 bits of resolution
        print('{0}us per bit'.format(pulse_length))
        pulse *= 1000
        pulse //= pulse_length
        self.pwm.set_pwm(channel, 0, pulse)
        
        
    def turnOffMotors():
        mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
        mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
        mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
    

        
          
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
            
            sys.stderr.write(program_name + ": " + repr(e) + "\n")
            return 2