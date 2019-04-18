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
import MCP3208

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
    _encoderposition_azimuth_center = 2816
    _encoderposition_azimuth_min = 2489
    _encoderposition_azimuth_max = 3028

    _steps_elevation_center = 0
    _steps_elevation_min = 0
    _steps_elevation_max = 360
    _encoderposition_elevation_center = 1696
    _encoderposition_elevation_min = 1260
    _encoderposition_elevation_max = 1744

    _steps_polarity_center = 0
    _steps_polarity_min = 0
    _steps_polarity_max = 180
    _encoderposition_polarity_center = 3148 
    _encoderposition_polarity_min = 2464
    _encoderposition_polarity_max = 3424
    

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

        self._Azimuth = RotationalAxis.RotationalAxis( self._stepperAzimuth, self._azimuth_steps_per_degree, self._adc, 0,
                                        self._steps_azimuth_center, self._steps_azimuth_min, self._steps_azimuth_max, 
                                        self._encoderposition_azimuth_center, self._encoderposition_azimuth_min, self._encoderposition_azimuth_max)

        self._Elevation = RotationalAxis.RotationalAxis( self._stepperElevation, self._elevation_steps_per_degree, self._adc, 0,
                                                self._steps_elevation_center, self._steps_elevation_min, self._steps_elevation_max, 
                                                self._encoderposition_elevation_center, self._encoderposition_elevation_min, self._encoderposition_elevation_max)

        self._Polarity = RotationalAxis.RotationalAxis( self._stepperPolarity, self._polarity_steps_per_degree, self._adc, 0,
                                                self._steps_polarity_center, self._steps_polarity_min, self._steps_polarity_max, 
                                                self._encoderposition_polarity_center, self._encoderposition_polarity_min, self._encoderposition_polarity_max)
        
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



"""
##########################################################################################
# Elevation - Inclination
##########################################################################################    
    def get_elevation_degrees(self):
        return float((self.get_elevation_stepper_count() / self._elevation_steps_per_degree))

    def get_elevation_stepper_count(self):
        return self._elevation_stepper_count
    
    def set_elevation_stepper_count(self, stepper_count):
        self._elevation_stepper_count = stepper_count
    


    def recenter_elevation(self):
        try:
            logging.info("Recentering Elevation at Value: " + str(self._encoderposition_elevation_center))
            encoderposition_elevation_current = self._adc.read(1)
            logging.info("Elevation Encoder Reading = " + str(encoderposition_elevation_current))

            nSteps = 0
            self._is_busy = True
            while ((encoderposition_elevation_current < self._encoderposition_elevation_center)
                and (encoderposition_elevation_current < self._encoderposition_elevation_max)
                and (encoderposition_elevation_current > self._encoderposition_elevation_min)):
                    nSteps+=1
                    self._stepperElevation.step(1, Adafruit_MotorHAT.FORWARD,  Adafruit_MotorHAT.DOUBLE)
                    encoderposition_elevation_current = self._adc.read(1)           

            
            while ((encoderposition_elevation_current > self._encoderposition_elevation_center)
                and (encoderposition_elevation_current < self._encoderposition_elevation_max)
                and (encoderposition_elevation_current > self._encoderposition_elevation_min)):
                    nSteps-=1
                    self._stepperElevation.step(1, Adafruit_MotorHAT.BACKWARD,  Adafruit_MotorHAT.DOUBLE)
                    encoderposition_elevation_current = self._adc.read(1)

            self._is_busy = False
            logging.info("Steps: " + str(nSteps))
                  

            self.set_elevation_stepper_count(0)
            encoderposition_elevation_current = self._adc.read(1)
            self._elevation_requires_calibration = False
            logging.info("Current Elevation Reading:"+str(self.get_elevation_degrees())+", Now Centered on Tripod with Cable Tension = " + str(encoderposition_elevation_current))
            return self.get_elevation_degrees()

        except Exception as e:
            self.handle_exception(e)
            return e

    def set_elevation(self, elevation):
        try:
            if(self._elevation_requires_calibration == True):
                self.recenter_elevation()       

            elevation_current_degrees = self.get_elevation_degrees()
            steps_required, self._elevation_target = self.calculate_elevation_steps(float(elevation))

            self._is_busy = True
            
            #Move Up
            if self._elevation_target > elevation_current_degrees:
                logging.info("Elevation Target: "+str(self._elevation_target)+", Elevation Current:"+str(elevation_current_degrees)+"; Moving Elevation Upward by Estimated: " + str(steps_required) + " steps.")
                self._stepperElevation.step(abs(steps_required), Adafruit_MotorHAT.BACKWARD,  Adafruit_MotorHAT.DOUBLE)

            #Move Down    
            elif self._elevation_target < elevation_current_degrees:
                logging.info("Elevation Target: "+str(self._elevation_target)+", Elevation Current:"+str(elevation_current_degrees)+"; Moving Elevation Downward by Estimated: " + str(steps_required) + " steps.")
                self._stepperElevation.step(abs(steps_required), Adafruit_MotorHAT.FORWARD,  Adafruit_MotorHAT.DOUBLE)

            else:
                logging.info("Holding Elevation Steady at: "+ str(elevation))

            # Set Elevation Value to Be Returned to GPredict
            self._is_busy = False
            self.set_elevation_stepper_count(self.get_elevation_stepper_count() + steps_required)
        
            return self.get_elevation_degrees()
            
        except Exception as e:
            self.handle_exception(e)
            return e


    def calculate_elevation_steps(self, elevation):
        try:

            elevation_tuple = divmod(elevation, self._elevation_degrees_per_step)
            elevation_remainder = float(elevation_tuple[1])
            
            #round down to nearest half degree
            elevation_target = float(elevation - elevation_remainder)
            
            #round back up if remainder was closer to upper bound
            if elevation_remainder > (self._elevation_degrees_per_step / 2):
                elevation_target += self._elevation_degrees_per_step

            degrees = float(elevation_target) - float(self.get_elevation_degrees())
            steps = int(self._elevation_steps_per_degree * degrees)
            
            return steps, elevation_target
        
        except Exception as e:
            self.handle_exception(e)

    def stop_elevation(self):
        try:        
            logging.info("EL Stop")
            self._encoder_A.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
            self._encoder_A.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
            self._elevation_requires_calibration = True
            return True
        except Exception as e:
            self.handle_exception(e)
            


##########################################################################################
#    Azimuth - Heading
##########################################################################################
    def get_azimuth_stepper_count(self):
        return self._azimuth_stepper_count
    
    def set_azimuth_stepper_count(self, stepper_count):
        self._azimuth_stepper_count = stepper_count

    # Calculate Azimuth in Degrees
    def get_azimuth_degrees(self):
        azimuth_current = float(self.get_azimuth_stepper_count() / self._azimuth_steps_per_degree)
        if azimuth_current < 0: 
            azimuth_current += 360
        return azimuth_current


    #Re-Center
    def recenter_azimuth(self):
        try:
            logging.info("Recentering Azimuth To Encoder Value: "+ str(self._encoderposition_azimuth_center))
            encoderposition_azimuth_current = self._adc.read(0)
            encoderposition_azimuth_previous = encoderposition_azimuth_current
            logging.info("Cable Tension Start = " + str(encoderposition_azimuth_current))

            nSteps = 0

            self._is_busy = True
            while (encoderposition_azimuth_current < self._encoderposition_azimuth_center):
                    nSteps+=1
                    self._stepperAzimuth.step(1, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.DOUBLE)
                    encoderposition_azimuth_previous = encoderposition_azimuth_current
                    encoderposition_azimuth_current = self._adc.read(0)           
                    #check it see if the encoder value is bouncing, if so then re-read encoder
                    if( abs(encoderposition_azimuth_current - encoderposition_azimuth_previous) > 2 ):
                        logging.warning("Received Unexpected Encoder with Previous Value: "+str(encoderposition_azimuth_previous)+"; New Outlier Value: "+str(encoderposition_azimuth_current)+"; sleeping 1 second")
                        time.sleep(1)
                        encoderposition_azimuth_current = self._adc.read(0)
                        encoderposition_azimuth_previous = encoderposition_azimuth_current
                        logging.warning("Re-Reading Encoder with New Value "+str(encoderposition_azimuth_current))
                    logging.info("Steps: " + str(nSteps) + ", "+str(encoderposition_azimuth_current))
            
            while (encoderposition_azimuth_current > self._encoderposition_azimuth_center):
                    nSteps-=1
                    self._stepperAzimuth.step(1, Adafruit_MotorHAT.BACKWARD,Adafruit_MotorHAT.DOUBLE)
                    encoderposition_azimuth_current = self._adc.read(0)
                    #check it see if the encoder value is bouncing, if so then re-read encoder
                    if( abs(encoderposition_azimuth_current - encoderposition_azimuth_previous) > 2 ):
                        logging.warning("Received Unexpected Encoder with Previous Value: "+str(encoderposition_azimuth_current)+"; New Outlier Value: "+str(encoderposition_azimuth_current)+"; sleeping 1 second")
                        time.sleep(1)
                        encoderposition_azimuth_current = self._adc.read(0)
                        encoderposition_azimuth_previous = encoderposition_azimuth_current
                        logging.warning("Re-Reading Encoder with New Value"+str(encoderposition_azimuth_previous))                    
                    logging.info("Steps: " + str(nSteps) + ", "+str(encoderposition_azimuth_current))

            self._is_busy = False
            logging.info("Total Steps: " + str(nSteps))
                  
            self.set_azimuth_stepper_count(0)
            self._azimuth_requires_calibration = False
            logging.info("Current Azimuth Reading: "+str(self.get_azimuth_degrees())+", Now Centered on Tripod with Encoder Position = " + str(self._adc.read(0)))
            return self.get_azimuth_degrees()

        except Exception as e:
            self.handle_exception(e)
            return e


    #Plan Horizontal Motion Based on encoder limits
    def plan_azimuth_movement(self, target_azimuth):
        
        # Initial Plan is to travel shortest route
        shortest_route_is_safe = True

        # Set Up Loca; Variables        
        degrees_travel = 0
        azimuth_actual = self.get_azimuth_degrees()

        #Start by setting motor direction to shortest linear route
        move_is_clockwise = True
        if target_azimuth < self.get_azimuth_degrees():
            move_is_clockwise = False

        # Measure Rotation in Degrees
        if (move_is_clockwise):
            degrees_travel = target_azimuth - azimuth_actual
        else:
            degrees_travel = azimuth_actual - target_azimuth

        # Check for shortest Circular Route
        # Is it shorter to go the other way around ?
        if degrees_travel > 180:
            move_is_clockwise = not move_is_clockwise
            degrees_travel = 360 - degrees_travel

        # Check Cable Tension
        # Is it physically safe to spin any farther in that direction?                
        if (move_is_clockwise):
            logging.info("Path from: "+str(azimuth_actual)+" to: "+str(target_azimuth)+" is: "+str(degrees_travel)+" Degrees Clockwise")
        else:
            logging.info("Path: from: "+str(azimuth_actual)+" to: "+str(target_azimuth)+" is: "+str(degrees_travel)+" Degrees Counter-Clockwise")


        #calculate the number of steps required by the Stepper Motor
        steps_planned = self.calculate_azimuth_steps(degrees_travel)
        return (steps_planned, move_is_clockwise, degrees_travel)



    def calculate_azimuth_steps(self, degrees_travel):
        try:
            steps, remainder = divmod(degrees_travel, (self._azimuth_degrees_per_step))
            return steps            
        except Exception as e:
            self.handle_exception(e)

    def motor_direction_driver_const(self, is_clockwise):
        if True == is_clockwise:
            return Adafruit_MotorHAT.FORWARD
        else:
            return Adafruit_MotorHAT.BACKWARD

    def round_azimuth_value(self, azimuth):
        #round down to nearest half degree
        azimuth_div, azimuth_remainder = divmod(azimuth, self._azimuth_degrees_per_step)
        azimuth_rounded = float(azimuth - azimuth_remainder)
        #round back up if remainder was closer to upper bound
        if azimuth_remainder > (self._azimuth_degrees_per_step / 2):
            azimuth_rounded += self._azimuth_degrees_per_step
        return azimuth_rounded   



    ##########################################
    # Execute Azimuth 
    def set_azimuth(self, azimuth):
        try:
            if(self._azimuth_requires_calibration == True):
                self.recenter_azimuth()

            #Find Nearest Half Degree Increment
            self._azimuth_target = float(azimuth)
            azimuth_target_rounded = self.round_azimuth_value(self._azimuth_target)
            
            if azimuth_target_rounded != self.get_azimuth_degrees():

                # Plan Movement
                steps_planned, is_clockwise, degrees_travel = self.plan_azimuth_movement(azimuth_target_rounded)
                logging.info("Azimuth Target: " + str(azimuth_target_rounded) + "; Moving Azimuth by: " + str(degrees_travel) + " Degrees, with: " + str(steps_planned) + " Steps.")

                # Scope Variables
                steps_actual = 0
                encoderposition_azimuth_current = self._adc.read(0)

                self._is_busy = True
                keep_moving = True
                while(keep_moving):

                    #Check Encoder Limits Before Moving
                    if ((encoderposition_azimuth_current > self._encoderposition_azimuth_min) and (encoderposition_azimuth_current < self._encoderposition_azimuth_max)):

                        #Move Stepper
                        motor_direction = self.motor_direction_driver_const(is_clockwise)
                        self._stepperAzimuth.step(1, motor_direction,  Adafruit_MotorHAT.DOUBLE)

                        # Increment Counters
                        steps_actual = 1 + steps_actual 
                        encoderposition_azimuth_current = self._adc.read(0)

                    # If Azimuth Travel Has Exceeded Limits, Reverse Direction, Recenter, then Stop Moving
                    else:
                        logging.info("Target Cable Tension Maxed Out In Current Direction at: "+str(encoderposition_azimuth_current)+" Re-centering to unwind cable")
                        self.recenter_azimuth()
                        encoderposition_azimuth_current = self._adc.read(0)
                        keep_moving = False

                    # Update Object
                    if(True == is_clockwise):
                        self.set_azimuth_stepper_count(self.get_azimuth_stepper_count() + 1)
                    else:
                        self.set_azimuth_stepper_count(self.get_azimuth_stepper_count() - 1)
                        
                    # Keep Moving ?
                    if (steps_actual >= steps_planned):
                        logging.info("Stopping Rotation at : " + str(steps_actual) + " Steps.")
                        keep_moving = False

                self._is_busy = False
                logging.info("Actual Azimuth Steps: "+ str(steps_actual) + ", Encoder Position: " + str(encoderposition_azimuth_current) + ", Direction: " + str(motor_direction))
                logging.info("Azimuth Stepper Count: " + str(self.get_azimuth_stepper_count()) + ", Azimuth Current Degrees: " + str(self.get_azimuth_degrees()))

            else:
                logging.info("Holding Azimuth Steady at: "+ str(azimuth))
            
            return self.get_azimuth_degrees()

        except Exception as e:
            self.handle_exception(e)
            return e

    def stop_azimuth(self):
        try: 
            logging.info("AZ Stop")
            self._encoder_A.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
            self._encoder_A.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
            self._azimuth_requires_calibration = True
            return True
    
        except Exception as e:
            self.handle_exception(e) 
            return e 


##########################################################################################
#    Polarity - Radio Signal Rotation
##########################################################################################
    def get_polarity_degrees(self):
        return float((self.get_polarity_stepper_count() / self._polarity_steps_per_degree))

    def get_polarity_stepper_count(self):
        return self._polarity_stepper_count
    
    def set_polarity_stepper_count(self, stepper_count):
        self._polarity_stepper_count = stepper_count
    

    # Find Centerline Based on Analog Encoder
    def recenter_polarity(self):
        try:
            logging.info("Recentering Polarity at Value: " + str(self._encoderposition_polarity_center))
            encoderposition_polarity_current = self._adc.read(2)
            logging.info("Polarity Encoder Reading = " + str(encoderposition_polarity_current))

            nSteps = 0
            self._is_busy = True
            while ((encoderposition_polarity_current < self._encoderposition_polarity_center)
                and (encoderposition_polarity_current < self._encoderposition_polarity_max)
                and (encoderposition_polarity_current > self._encoderposition_polarity_min)):
                    nSteps+=1
                    self._stepperPolarity.step(1, Adafruit_MotorHAT.FORWARD,  Adafruit_MotorHAT.DOUBLE)
                    encoderposition_polarity_current = self._adc.read(2)           

            
            while ((encoderposition_polarity_current > self._encoderposition_polarity_center)
                and (encoderposition_polarity_current < self._encoderposition_polarity_max)
                and (encoderposition_polarity_current > self._encoderposition_polarity_min)):
                    nSteps-=1
                    self._stepperPolarity.step(1, Adafruit_MotorHAT.BACKWARD,  Adafruit_MotorHAT.DOUBLE)
                    encoderposition_polarity_current = self._adc.read(2)

            self._is_busy = False
            logging.info("Steps: " + str(nSteps))
                  

            self.set_polarity_stepper_count(0)
            encoderposition_polarity_current = self._adc.read(2)
            self._polarity_requires_calibration = False
            logging.info("Current polarity Reading:"+str(self.get_polarity_degrees())+", Now Centered on Tripod with Cable Tension = " + str(encoderposition_polarity_current))
            return self.get_polarity_degrees()

        except Exception as e:
            self.handle_exception(e)
            return e


    # Set Polarity Position Based On Stepper Count
    def set_polarity(self, polarity_target):
        try:       
            if(self._polarity_requires_calibration == True):
                self.recenter_polarity()
    
            steps_required, self._polarity_target = self.calculate_polarity_steps(polarity_target)

            logging.debug("Polarity Target: "+ str(self._polarity_target) +"; degrees per setp: " + str(self._polarity_degrees_per_step) ) 

            polarity_current_degrees = self.get_polarity_degrees()
            if polarity_target == polarity_current_degrees:
                logging.info("Holding polarity Steady at: "+ str(polarity_target))
            else:
                
                encoderposition_polarity_current = self._adc.read(2)

                # set default direction forward
                direction_required = Adafruit_MotorHAT.FORWARD
                direction_label = "Clockwise"
                limit_label = "Maximum"
                stepper_incriment = 1
                
                # then check to see if we need to go backward
                if steps_required < 0:
                    direction_required = Adafruit_MotorHAT.BACKWARD
                    direction_label = "CounterClockwise"
                    limit_label = "Minimum"
                    stepper_incriment = -1

                logging.info("Polarity Target: "+str(polarity_target)+", Polarity Current: "+str(polarity_current_degrees))
                logging.info("Polarity Stepper Count: "+str(self.get_polarity_stepper_count())+", Moving polarity "+str(direction_label)+" by Estimated: " + str(steps_required) + " steps.")

                #execute rotation    
                self._is_busy = True               
                for steps_taken in range(abs(steps_required)):         
                    
                    # Step Motor
                    self._stepperPolarity.step(1, direction_required, Adafruit_MotorHAT.DOUBLE)

                    # Set Polarity Value to Be Returned to GPredict                    
                    self.set_polarity_stepper_count(self.get_polarity_stepper_count() + stepper_incriment)
                    encoderposition_polarity_current = self._adc.read(2)
                    if self._verbose > 3 :
                        logging.debug("Interim Polarity Stepper Count:"+str(self.get_polarity_stepper_count())+"; Interim Polarity Degrees: " + str(self.get_polarity_degrees()) + " EncoderValue: "+ str(encoderposition_polarity_current))

                    # Check Limits
                    if ((encoderposition_polarity_current > self._encoderposition_polarity_max) or (encoderposition_polarity_current < self._encoderposition_polarity_min)):
                        logging.warning("Polarity Exceeded "+str(limit_label)+" Encoder Value at: " + str(encoderposition_polarity_current)+ "; Re-Centering Polarity.")
                        self.recenter_polarity()
                        break

            self._is_busy = False
            logging.info("New Polarity Stepper Count: "+str(self.get_polarity_stepper_count())+"; New Polarity Degrees: " + str(self.get_polarity_degrees()) + " EncoderValue: "+ str(encoderposition_polarity_current))
            return self.get_polarity_degrees()
            
        except Exception as e:
            self.handle_exception(e)
            return e

    def calculate_polarity_steps(self, polarity_target):
        try:
            steps = int(0)
            polarity_remainder = 0.0

            self._polarity_target = float(polarity_target)
            polarity_tuple = divmod(self._polarity_target, self._polarity_degrees_per_step)
            polarity_remainder = float(polarity_tuple[1])
            
            #round down to nearest half degree
            polarity_target = float(self._polarity_target - polarity_remainder)
            
            #round back up if remainder was closer to upper bound
            if polarity_remainder > (self._polarity_degrees_per_step / 2):
                polarity_target += self._polarity_degrees_per_step


            degrees = float(polarity_target) - float(self.get_polarity_degrees())
            steps = int(self._polarity_steps_per_degree * degrees)
            logging.debug("Steps Per Degree: "+ str(self._polarity_steps_per_degree) +"; Degrees: "+str(degrees)+"; Steps: " + str(steps)+ "; Remainder: "+ str(polarity_remainder)) 
            
            return steps, polarity_target

        except Exception as e:
            self.handle_exception(e)

    def stop_polarity(self):
        try:        
            logging.info("Polarity Stop")
            self._encoder_B.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
            self._encoder_B.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
            self._polarity_requires_calibration = True
        except Exception as e:
            self.handle_exception(e)
            
"""


