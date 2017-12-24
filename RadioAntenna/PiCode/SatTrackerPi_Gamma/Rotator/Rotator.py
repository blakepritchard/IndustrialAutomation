'''
Created on Dec 18, 2017

@author: blake
'''
from __future__ import division
from __future__ import builtins
import sys
import os
import time
from builtins import len



# Import Local Libraries
path_runtime = os.path.dirname(__file__)
path_parent_version = os.path.abspath(os.path.join(path_runtime, os.pardir))
path_parent_platform = os.path.abspath(os.path.join(path_parent_version, os.pardir))
path_lib_servo = os.path.join(path_parent_platform, "Adafruit_Python_PCA9685/Adafruit_PCA9685/PCA9685.py")
sys.path.insert(0, os.path.abspath(path_lib_servo))
# Import the PCA9685 module.
import Adafruit_PCA9685



class Rotator(object):

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

        # Initialise the PCA9685 using the default address (0x40).
        _pwm = Adafruit_PCA9685.PCA9685()
        # Set frequency to 50hz, good for servos.
        _pwm.set_pwm_freq(50)
        
        #Reset Servos to Center with a 1500us pulse
        _pwm.set_pwm(0, 0, self._servo_center)
        time.sleep(1)
        _pwm.set_pwm(1, 0, self._servo_center)
        time.sleep(1)

       
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
        self._elevation_target = elevation
        '''ToDo: Remove this Hack'''
        
        pulse_width = int(self._servo_center + ((self._servo_max - self._servo_center) * (float(elevation)/90.0)))
        print("setting elevation to: "+ str(elevation)+" with a pulse width of: "+ pulse_width)
        self._pwm.set_pwm(1, 0, pulse_width)
        self._elevation_current = elevation

    
    def set_azimuth(self, azimuth):
        self._azimuth_target = azimuth
        '''ToDo: Remove this Hack'''
        
        pulse_width = int(self._servo_center + ((self._servo_max - self._servo_center) * (float(azimuth)/180.0)))
        print("setting elevation to: "+ str(azimuth)+" with a pulse width of: "+ pulse_width)
        self._pwm.set_pwm(0, 0, pulse_width)
        self._azimuth_current = azimuth

    
    def set_polarity(self, polarity):
        self._polarity_target = polarity
        '''ToDo: Remove this Hack'''
        print("setting polarity to: "+ str(polarity))
        self._polarity_current = polarity
        
    
    def stop_azimuth(self):
        print("AZ Stop")
        
    def stop_elevation(self):
        print("EL Stop")
        
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
        
          
    def execute_easycomm2_command(self, rotator_commands):  
        
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
                
                if      "AZ" == command_operation: self.set_azimuth(command_parameters)
                elif    "EL" == command_operation: self.set_elevation(command_parameters)       
    
            hash_results[rotator_command] = result;

        return hash_results       
        
    