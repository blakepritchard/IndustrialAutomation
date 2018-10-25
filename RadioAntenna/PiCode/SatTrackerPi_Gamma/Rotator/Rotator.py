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



class Rotator(object):

    _verbose = False
    
    _encoder_A = 0
    _encoder_B = 0
    _adc = 0;
    _orientation = 0
    _stepperAzimuth = 0
    _stepperElevation = 0

    _encoderposition_azimuth_center = 701
    _encoderposition_azimuth_min = 640
    _encoderposition_azimuth_max = 745

    _encoderposition_elevation_center = 423
    _encoderposition_elevation_min = 314
    _encoderposition_elevation_max = 435

    _encoderposition_elevation_center = 700
    _encoderposition_elevation_min = 650
    _encoderposition_elevation_max = 750
    

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

    _azimuth_degrees_per_step   = 1/self._azimuth_steps_per_degree
    _elevation_degrees_per_step = 1/self._elevation_steps_per_degree
    _polarity_degrees_per_step  = 1/self._polarity_steps_per_degree

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


        if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
            logging.basicConfig(level=logging.DEBUG)

        self._stepperAzimuth = self._encoder_A.getStepper(200, 1)     # 200 steps/rev, motor port #1
        self._stepperAzimuth.setSpeed(15)                             # 10 RPM

        self._stepperElevation = self._encoder_A.getStepper(200, 2)   # 200 steps/rev, motor port #2
        self._stepperElevation.setSpeed(15)                           # 10 RPM

        self._stepperPolarity = self._encoder_B.getStepper(200, 1)   # 200 steps/rev, motor port #1
        self._stepperElevation.setSpeed(10)                           # 10 RPM

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
        #print("returning elevation of: "+ str(self._elevation_current_degrees))
        return self._elevation_current_degrees
    
    def get_azimuth(self):
        #print("returning azimuth of: "+ str(self._azimuth_current_degrees))
        return self._azimuth_current_degrees
    
    def get_polarity(self):
        #print("returning polarity of: "+ str(self._polarity_current_degrees))
        return self._polarity_current_degrees

    def set_verbosity(self, verbose):
        self._verbose = verbose

    def get_verbosity(self):
        return self._verbose




##########################################################################################
# Elevation
##########################################################################################    
    def get_elevation_degrees(self):
        return float((self.get_elevation_stepper_count() / self._elevation_steps_per_degree))

    def get_elevation_stepper_count(self):
        return self._elevation_stepper_count
    
    def set_elevation_stepper_count(self, stepper_count):
        self._elevation_stepper_count = stepper_count
    


    def recenter_elevation(self):
        try:
            print("Recentering elevation")
            encoderposition_elevation_current = self._adc.read_adc(1)
            print("Cable Tension = " + str(encoderposition_elevation_current))

            nSteps = 0;
            while ((encoderposition_elevation_current < self._encoderposition_elevation_center)
                and (encoderposition_elevation_current < self._encoderposition_elevation_max)
                and (encoderposition_elevation_current > self._encoderposition_elevation_min)):
                    nSteps+=1
                    self._stepperElevation.step(1, Adafruit_MotorHAT.FORWARD,  Adafruit_MotorHAT.DOUBLE)
                    encoderposition_elevation_current = self._adc.read_adc(1)           

            
            while ((encoderposition_elevation_current > self._encoderposition_elevation_center)
                and (encoderposition_elevation_current < self._encoderposition_elevation_max)
                and (encoderposition_elevation_current > self._encoderposition_elevation_min)):
                    nSteps-=1
                    self._stepperElevation.step(1, Adafruit_MotorHAT.BACKWARD,  Adafruit_MotorHAT.DOUBLE)
                    encoderposition_elevation_current = self._adc.read_adc(1)

            print("Steps: " + str(nSteps))
                  

            self.set_elevation_stepper_count(0)
            encoderposition_elevation_current = self._adc.read_adc(1)
            print("Current Elevation Reading:"+str(self.get_elevation_degrees())+", Now Centered on Tripod with Cable Tension = " + str(encoderposition_elevation_current))
            
        except Exception as e:
            self.handle_exception(e)

    def set_elevation(self, elevation):
        try:       
            self._elevation_target = float(elevation)
            elevation_tuple = divmod(self._elevation_target, self._elevation_degrees_per_step)
            elevation_remainder = float(elevation_tuple[1])
            
            #round down to nearest half degree
            elevation_target = float(self._elevation_target - elevation_remainder)
            
            #round back up if remainder was closer to upper bound
            if elevation_remainder > (self._elevation_degrees_per_step / 2):
                elevation_target += self._elevation_degrees_per_step

            elevation_current_degrees = self.get_elevation_degrees()
            steps_required = self.calculate_elevation_steps(elevation_target)

            #Move Up
            if elevation_target > elevation_current_degrees:
                print("Elevation Target: "+str(elevation_target)+", Elevation Current:"+str(elevation_current_degrees)+"; Moving Elevation Upward by Estimated: " + str(steps_required) + " steps.")
                self._stepperElevation.step(abs(steps_required), Adafruit_MotorHAT.BACKWARD,  Adafruit_MotorHAT.DOUBLE)

            #Move Down    
            elif elevation_target < elevation_current_degrees:
                print("Elevation Target: "+str(elevation_target)+", Elevation Current:"+str(elevation_current_degrees)+"; Moving Elevation Downward by Estimated: " + str(steps_required) + " steps.")
                self._stepperElevation.step(abs(steps_required), Adafruit_MotorHAT.FORWARD,  Adafruit_MotorHAT.DOUBLE)

            else:
                print("Holding Elevation Steady at: "+ str(elevation))

            # Set Elevation Value to Be Returned to GPredict
            self.set_elevation_stepper_count(self.get_elevation_stepper_count() + steps_required)

            
        except Exception as e:
            self.handle_exception(e)

    def calculate_elevation_steps(self, elevation_target):
        try:
            degrees = float(elevation_target) - float(self.get_elevation_degrees())
            steps = self._elevation_steps_per_degree * int(degrees)
            return steps
        except Exception as e:
            self.handle_exception(e)

    def stop_elevation(self):
        try:        
            print("EL Stop")
            self._encoder_A.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
            self._encoder_A.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
        except Exception as e:
            self.handle_exception(e)
            


##########################################################################################
#    Azimuth
##########################################################################################
    def get_azimuth_stepper_count(self):
        return self._azimuth_stepper_count
    
    def set_azimuth_stepper_count(self, stepper_count):
        self._azimuth_stepper_count = stepper_count

    # Calculate Azimuth in Degrees
    def get_azimuth_degrees(self):
        return float(self.get_azimuth_stepper_count() / self._azimuth_steps_per_degree)


    #Re-Center
    def recenter_azimuth(self):
        try:
            print("Recentering Azimuth")
            encoderposition_azimuth_current = self._adc.read_adc(0)
            print("Cable Tension = " + str(encoderposition_azimuth_current))

            nSteps = 0;
            while ((encoderposition_azimuth_current < self._encoderposition_azimuth_center)
                and (encoderposition_azimuth_current < self._encoderposition_azimuth_max)
                and (encoderposition_azimuth_current > self._encoderposition_azimuth_min)):
                    nSteps+=1
                    self._stepperAzimuth.step(1, Adafruit_MotorHAT.FORWARD,  Adafruit_MotorHAT.DOUBLE)
                    encoderposition_azimuth_current = self._adc.read_adc(0)           

            
            while ((encoderposition_azimuth_current > self._encoderposition_azimuth_center)
                and (encoderposition_azimuth_current < self._encoderposition_azimuth_max)
                and (encoderposition_azimuth_current > self._encoderposition_azimuth_min)):
                    nSteps-=1
                    self._stepperAzimuth.step(1, Adafruit_MotorHAT.BACKWARD,  Adafruit_MotorHAT.DOUBLE)
                    encoderposition_azimuth_current = self._adc.read_adc(0)

            print("Steps: " + str(nSteps))
                  
            self.set_azimuth_stepper_count(0)
            print("Current Azimuth Reading:"+str(self.get_azimuth_degreess)+", Now Centered on Tripod with Cable Tension = " + str(self._adc.read_adc(0)))
            
        except Exception as e:
            self.handle_exception(e)


    #Plan Horizontal Motion Based on encoder limits
    def plan_azimuth_movement(self, target_azimuth):
        
        # Initial Plan is to travel shortest route
        shortest_route_is_safe = True

        # Set Up Loca; Variables        
        degrees_travel = 0
        estimated_tension = 0
        tension_ratio = (self._encoderposition_azimuth_max - self._encoderposition_azimuth_min) / 360

        degrees_travel_simple = 0
        degrees_travel_alternate = 0
        degrees_travel_shortest = 0
        degrees_travel_recommended = 0;     
        
        #Use Encoder on MCP3008
        encoderposition_azimuth_current = self._adc.read_adc(0)
        azimuth_actual = self.get_azimuth_degrees()

        #Start by setting motor direction to shortest linear route
        move_is_clockwise = True;
        if target_azimuth < self.get_azimuth_degrees():
            move_is_clockwise = False;

        # Check for shortest Circular Route
        # Is it shorter to go the other way around ?
        if (move_is_clockwise):
            degrees_travel_simple = target_azimuth - azimuth_actual
        else:
            degrees_travel_simple = azimuth_actual - target_azimuth

        degrees_travel_alternate = 360 - degrees_travel_simple               
        if degrees_travel_alternate < degrees_travel_simple:
            move_is_clockwise = not move_is_clockwise
            degrees_travel_shortest = degrees_travel_alternate
        else:
            degrees_travel_shortest = degrees_travel_simple

        # Check Cable Tension
        # Is it physically safe to spin any farther in that direction?                
        estimated_tension_change = degrees_travel_shortest * tension_ratio
        if (move_is_clockwise):
            print "Shortest Path from: "+str(azimuth_actual)+" to: "+str(target_azimuth)+" is: "+str(degrees_travel_shortest)+" Degrees Clockwise, Tension Ratio:" + str(tension_ratio) + " Per Degree"
        else:
            print "Shortest Path: from: "+str(azimuth_actual)+" to: "+str(target_azimuth)+" is: "+str(degrees_travel_shortest)+" Degrees Counter-Clockwise, Tension Ratio:" + str(tension_ratio)+ " Per Degree"

        if (move_is_clockwise):
            estimated_tension_total = encoderposition_azimuth_current + estimated_tension_change
            print "Predicted encoderposition Value: " + str(estimated_tension_total)
            if estimated_tension_total > self._encoderposition_azimuth_max:
                shortest_route_is_safe = False
                print "Estiamte: "+str(estimated_tension_total)+ " Exceeds Maximum Value of " + str(self._encoderposition_azimuth_max) + ", Azimuth will track the long way around."
        else:
            estimated_tension_total = encoderposition_azimuth_current - estimated_tension_change
            print "Predicted encoderposition Value: " + str(estimated_tension_total)
            if estimated_tension_total < self._encoderposition_azimuth_min:
                shortest_route_is_safe = False
                print "Estimate: "+str(estimated_tension_total)+ " Is Below Minimum Value of " + str(self._encoderposition_azimuth_min) + ", Azimuth will track the long way around."

        if shortest_route_is_safe:
            degrees_travel_recommended = degrees_travel_shortest
        else:
            move_is_clockwise = not move_is_clockwise
            degrees_travel_recommended = 360 - degrees_travel_shortest
            

        #calculate the number of steps required by the Stepper Motor
        steps_planned = self.calculate_azimuth_steps(degrees_travel_recommended)
        return (steps_planned, move_is_clockwise, degrees_travel_recommended, estimated_tension)



    def calculate_azimuth_steps(self, degrees_travel):
        try:
            steps, remainder = divmod(degrees_travel, (1/self._azimuth_degrees_per_step))
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

            #Find Nearest Half Degree Increment
            self._azimuth_target = float(azimuth)
            azimuth_target_rounded = self.round_azimuth_value(self._azimuth_target)
            
            if azimuth_target_rounded != self.get_azimuth_degrees():

                # Plan Movement
                steps_planned, is_clockwise, degrees_travel, estimated_tension = self.plan_azimuth_movement(azimuth_target_rounded)
                print("Azimuth Target: " + str(azimuth_target_rounded) + "; Moving Azimuth by Estimated: " + str(degrees_travel) + " Degrees, with" + str(steps_planned) + " Steps.")

                # Scope Variables
                steps_actual = 0
                encoderposition_azimuth_current = self._adc.read_adc(0)
                
                keep_moving = True
                while(keep_moving):

                    #Check Encoder Limits Before Moving
                    if ((encoderposition_azimuth_current > self._encoderposition_azimuth_min) and (encoderposition_azimuth_current < self._encoderposition_azimuth_max)):

                        #Move Stepper
                        motor_direction = self.motor_direction_driver_const(is_clockwise)
                        self._stepperAzimuth.step(1, motor_direction,  Adafruit_MotorHAT.DOUBLE)

                        # Increment Counters
                        steps_actual = 1 + steps_actual 
                        azimuth_current_rounded = self.get_rounded_azimuth()
                        encoderposition_azimuth_current = self._adc.read_adc(0)

                    # If Azimuth Travel Has Exceeded Limits, Reverse Direction, Recenter, then Stop Moving
                    else:
                        print "Target Cable Tension Maxed Out In Current Direction at: "+str(encoderposition_azimuth_current)+" Despite Predictions, Re-centering and Reversing Direction to unwind cable"
                        self.recenter_azimuth()
                        encoderposition_azimuth_current = self._adc.read_adc(0)
                        is_clockwise = not is_clockwise
                        keep_moving = False

                    # Update Object
                    if(true == is_clockwise):
                        self.set_azimuth_stepper_count(self.get_azimuth_stepper_count() + 1)
                    else:
                        self.set_azimuth_stepper_count(self.get_azimuth_stepper_count() - 1)
                        
                    # Keep Moving ?
                    if (steps_actual >= steps_planned):
                        print "Stopping Rotation at : " + str(steps_actual) + " Steps."
                        keep_moving = False

                print("Actual Azimuth Steps: "+ str(steps_actual) + ", Encoderposition: " + str(encoderposition_azimuth_current) + ", Direction: " + str(motor_direction))
                print("Azimuth Target Rounded: " + str(azimuth_target_rounded) + ", Azimuth Current Rounded: " + str(azimuth_current_rounded))


            else:
                print("Holding Azimuth Steady at: "+ str(azimuth))


        except Exception as e:
            self.handle_exception(e)

    def stop_azimuth(self):
        try: 
            print("AZ Stop")
            self._encoder_A.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        except Exception as e:
            self.handle_exception(e)  

##########################################################################################
#    Polarity
##########################################################################################
    def set_polarity(self, polarity):
        self._polarity_target = polarity
        '''ToDo: Remove this Hack'''
        print("setting polarity to: "+ str(polarity))
        self._polarity_current_degrees = polarity
        

##########################################################################################
#    Protocol
##########################################################################################    
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
                #print("Command: " + rotator_command)
                result = ""
                    
                # EasyCommII uses short commands to Get values from the Rotator
                if len(rotator_command) == 2:
                    if      "AZ" == rotator_command: result = str(self.get_azimuth_degrees())
                    elif    "EL" == rotator_command: result = str(self.get_elevation_degrees())
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
