'''
Created on Dec 18, 2017

@author: blake
'''
from builtins import len

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
    
    
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
       
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
        print("setting elevation to: "+ str(elevation))
        self._elevation_current = elevation

    
    def set_azimuth(self, azimuth):
        self._azimuth_target = azimuth
        '''ToDo: Remove this Hack'''
        print("setting azimuth to: "+ str(azimuth))
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
        
    