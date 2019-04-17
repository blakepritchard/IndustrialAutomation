import os
import sys
import time
import logging

# Import ADC (MCP3208) library.
from mcp3208 import MCP3208

# Import Stepper
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor


class RotationalAxis(object):

    _is_busy = False
    _adc = 0
    _stepper = 0

    _encoderposition_center = 0
    _encoderposition_min = 0
    _encoderposition_max = 0

    _steppercount_center = 0
    _steppercount_min = 0
    _steppercount_max = 0

    _target_degrees = 0
    _stepper_count = 0
    _steps_per_degree = 2
    _degrees_per_step   = 1/_steps_per_degree
    _requires_calibration = True

    def __init__(self, stepper, adc, center, min, max):
        self._stepper = stepper
        self._adc = adc
        self._adc_channel = 0
        self._encoderposition_center = 0
        self._encoderposition_min = 0
        self._encoderposition_max = 0

    def __del__(self):
        # body of destructor
        self._stepper = 0    

    def handle_exception(self, e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.critical(exc_type, fname, exc_tb.tb_lineno)
        logging.critical(e)
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
        
        sys.stderr.write("Rotator.py: " + repr(e) + "\n")
        return 2    

    def get_degrees(self):
        return float((self.get_stepper_count() / self._steps_per_degree))

    def get_stepper_count(self):
        return self._stepper_count
    
    def set_stepper_count(self, stepper_count):
        self._stepper_count = stepper_count
    
   #Re-Center
    def recenter(self):
        try:
            logging.info("Recentering To Encoder Value: "+ str(self._encoderposition_center))
            encoderposition_current = self._adc.read(self._adc_channel)
            encoderposition_previous = encoderposition_current
            logging.info("Current Encoder Value = " + str(encoderposition_current))
            nSteps = 0

            # set default direction forward
            direction_required = Adafruit_MotorHAT.FORWARD
            stepper_incriment = 1
            
            # then check to see if we need to go backward
            if (encoderposition_current < self._encoderposition_center):
                direction_required = Adafruit_MotorHAT.BACKWARD
                stepper_incriment = -1

            self._is_busy = True
            while ((encoderposition_current != self._encoderposition_center) and 
                    (encoderposition_current < self._encoderposition_max) and
                    (encoderposition_current > self._encoderposition_min)):
                    nSteps+=stepper_incriment
                    self._stepper.step(1, direction_required, Adafruit_MotorHAT.DOUBLE)
                    encoderposition_previous = encoderposition_current
                    encoderposition_current = self._adc.read(self._adc_channel)           
                    #check it see if the encoder value is bouncing, if so then re-read encoder
                    if( abs(encoderposition_current - encoderposition_previous) > 2 ):
                        logging.warning("Received Unexpected Encoder with Previous Value: "+str(encoderposition_previous)+"; New Outlier Value: "+str(encoderposition_current)+"; sleeping 1 second")
                        time.sleep(1)
                        encoderposition_current = self._adc.read(self._adc_channel)
                        encoderposition_previous = encoderposition_current
                        logging.warning("Re-Reading Encoder with New Value "+str(encoderposition_current))
                    logging.info("Steps: " + str(nSteps) + ", "+str(encoderposition_current))
            
            self._is_busy = False
            logging.info("Total Steps: " + str(nSteps))
                  
            self.set_stepper_count(0)
            self._requires_calibration = False
            logging.info("Current  Reading: "+str(self.get_degrees())+", Now Centered on Tripod with Encoder Position = " + str(self._adc.read(0)))
            return self.get_degrees()

        except Exception as e:
            self.handle_exception(e)
            return e



    # Set  Position Based On Stepper Count
    def set_position(self, _target):
        try:       
            if(self._requires_calibration == True):
                self.recenter()
    
            steps_required, self.target = self.calculate_steps(_target)

            logging.debug("Position Target: "+ str(self.target) +"; degrees per setp: " + str(self._degrees_per_step) ) 

            _current_degrees = self.get_degrees()
            if _target == _current_degrees:
                logging.info("Holding  Steady at: "+ str(_target))
            else:
                
                encoder_position_current = self._adc.read(self._adc_channel)

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

                logging.info(" Target: "+str(_target)+",  Current: "+str(_current_degrees))
                logging.info(" Stepper Count: "+str(self.get_stepper_count())+", Moving  "+str(direction_label)+" by Estimated: " + str(steps_required) + " steps.")

                #execute rotation    
                self._is_busy = True               
                for steps_taken in range(abs(steps_required)):         
                    
                    # Step Motor
                    self._stepper.step(1, direction_required, Adafruit_MotorHAT.DOUBLE)

                    # Set  Value to Be Returned to GPredict                    
                    self.set_stepper_count(self.get_stepper_count() + stepper_incriment)
                    encoderposition_current = self._adc.read(self._adc_channel)
                    
                    logging.debug("Interim  Stepper Count:"+str(self.get_stepper_count())+"; Interim  Degrees: " + str(self.get_degrees()) + " EncoderValue: "+ str(encoderposition_current))

                    # Check Limits
                    if ((encoderposition_current > self._encoderposition_max) or (encoderposition_current < self._encoderposition_min)):
                        logging.warning(" Exceeded "+str(limit_label)+" Encoder Value at: " + str(encoderposition_current)+ "; Re-Centering .")
                        self.recenter()
                        break

            self._is_busy = False
            logging.info("New  Stepper Count: "+str(self.get_stepper_count())+"; New  Degrees: " + str(self.get_degrees()) + " EncoderValue: "+ str(encoderposition_current))
            return self.get_degrees()
            
        except Exception as e:
            self.handle_exception(e)
            return e

    def calculate_steps(self, _target):
        try:
            steps = int(0)
            _remainder = 0.0

            self._target = float(_target)
            _tuple = divmod(self._target, self._degrees_per_step)
            _remainder = float(_tuple[1])
            
            #round down to nearest half degree
            _target = float(self._target - _remainder)
            
            #round back up if remainder was closer to upper bound
            if _remainder > (self._degrees_per_step / 2):
                _target += self._degrees_per_step


            degrees = float(_target) - float(self.get_degrees())
            steps = int(self._steps_per_degree * degrees)
            logging.debug("Steps Per Degree: "+ str(self._steps_per_degree) +"; Degrees: "+str(degrees)+"; Steps: " + str(steps)+ "; Remainder: "+ str(_remainder)) 
            
            return steps, _target

        except Exception as e:
            self.handle_exception(e)

    def stop(self):
        try:        
            logging.info(" Stop")
            self._stepper.run(Adafruit_MotorHAT.RELEASE)           
            self._requires_calibration = True
        except Exception as e:
            self.handle_exception(e)
    
    