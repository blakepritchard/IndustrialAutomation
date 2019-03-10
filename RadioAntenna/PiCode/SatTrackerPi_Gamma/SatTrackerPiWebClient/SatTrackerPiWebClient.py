import os
import sys
import pwd

import serial
import logging
import json
import requests 
import argparse

import sched
import time

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

def main(argv=None):
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    parser = ArgumentParser(description="SatTrackerPi Web Client", formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("-l", "--loglevel", dest="loglevel", help="set loglevel level [default: %(default)s]")
    parser.add_argument("-r", "--rotator", dest="rotator", help="config file with serial port name for output[default: %(default)s]")
    parser.add_argument("-s", "--speed", dest="speed", type=int, help="set serial port speed [default: %(default)s]")
    parser.add_argument("-w", "--webserver", dest="webserver", help="set SatTrackerWebsite webserver URL [default: %(default)s]")
    parser.add_argument("-i", "--interval", dest="interval", help="set Interval between Status Updates")
    serial_config_filename = ("/home/pi/src/git/IndustrialAutomation/RadioAntenna/PiCode/SatTrackerPi_Gamma/SatTrackerPiDaemon/webclient_serial.config")

    # Process arguments
    args = parser.parse_args()
    logging.basicConfig(filename='sat_tracker_webclient.log', filemode='w', level=int(args.loglevel), format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.info("Verbose mode on Log Level: "+str(args.loglevel))

    sat_tracker_webclient = SatTrackerPiWebClient(args.loglevel, args.rotator, args.speed, args.webserver, args.interval)
    sat_tracker_webclient.start_client_loop()

if __name__ == "__main__":
    sys.exit(main())



class SatTrackerPiWebClient:

    def __init__(self,  verbose, config_file_serial, speed_serial, url_webserver, interval):
        self.verbose = verbose
        self.config_file_serial = config_file_serial
        self.url_webserver = url_webserver
        self.speed_serial = speed_serial
        self.interval = interval
        self.start_time = time.time()
        self.scheduler = sched.scheduler(time.time, time.sleep)

        with open(self.config_file_serial, 'r') as f:
            config_dict = json.load(f)
        self.serial_port_name = config_dict['SERIAL_PORT_NAME']


    
    def start_client_loop(self):
        try:
            logging.info("Starting Client Loop With Interval: "+str(self.interval))
            self.scheduler.enter(self.interval, 1, self._execute_client_loop(), ())
            self.scheduler.run()
        except Exception as exception:
            return self.handle_exception(exception)

    def _execute_client_loop(self):
        try:
            self.start_time = time.time()
            self.post_rotator_status()
            current_time = time.time()
            interval_next = self.interval- (( current_time - self.start_time) % self.interval )
            self.scheduler.enter(interval_next, 1, self._execute_client_loop(), ())
        except Exception as exception:
            return self.handle_exception(exception)

    def post_rotator_status(self):
        try:
            data = self.get_rotator_status()
            logging.info("Posting Rotator Status: "+str(data))
            r = requests.post(url = self.url_webserver + "/sat_tracker/api/rotator/status", data = data)
            logging.info("Post Response Text: "+str(r.text))        
            return r.text
        except Exception as exception:
            return self.handle_exception(exception)       


    def get_rotator_status(self):
        try:
            json_result = self.execute_serial_command("RS", None)
            logging.debug("Rotator Status: " + json_result)
            return json_result
        
        except Exception as exception:
            return self.handle_exception(exception)


    def set_polarity_json(self, polarity_json):
        try:
            json_result = ""
            logging.info("a set_polarity_json command is being sent with data: " + polarity_json)

            float_polarity_next = polarity_json['polarity_new']
 
            polarity_command= "PP" +  str(float_polarity_next)
            polarity_current = self.execute_serial_command(polarity_command, None)
            json_result = {"polarity_degrees": polarity_current}
            return json.dumps(json_result)

        except Exception as exception:
            return self.handle_exception(exception)



    def set_elevation(self, elevation_new):
        try:
            logging.debug("a set_elevation Command Is Being Sent")

            polarity_command= "EL" + elevation_new 
            result = self.execute_serial_command(polarity_command)
            return result

        except Exception as exception:
            return self.handle_exception(exception)


    #@sat_tracker_app.route("/sat_tracker/set_azimuth", methods=["GET","POST"])
    #@sat_tracker_app.route("/azimuth/set_azimuth", methods=["POST"])
    def set_azimuth(self, azimuth_new):
        try:
            logging.debug("a set_azimuth Command Is Being Sent")

            polarity_command= "AZ" + azimuth_new 
            result = self.execute_serial_command(polarity_command)

            return result

        except Exception as exception:
            return self.handle_exception(exception)






    # Send Serial Command, Get Serial Response
    def execute_serial_command(self, serial_command, serial_timeout=0):

        try:
            #self.serial_lock.acquire()
            serial_response = ""
            serial_port = serial.Serial(str(self.serial_port_name), self.speed_serial, rtscts=True,dsrdtr=True, timeout=serial_timeout) 
            logging.info("User: " + str(pwd.getpwuid(os.getuid()).pw_name) + " is about to Send Serial Command: "+str(serial_command)+" to: "+ str(self.serial_port_name) )

            # Send Command
            serial_command += "\n"
            serial_port.write(serial_command.encode())

            # If TimeOut Is 0 Then Return Immediately, Otherwise Wait For a Response to Arrive On the Serial Port
            if(0 == serial_timeout):
                serial_response = 0
            else:
                bytes_carraigereturn = bytes("\r")
                bytes_linefeed = bytes("\n")  
                characters_recieved = ""
                continue_reading=True
                while continue_reading:
                    byte_next = serial_port.read()
                    char_next = byte_next.decode("utf-8")

                    # Continue Reading Bytes From the Serial Port Until We Find a NewLine Charater ("\n") LineFeed (LF) 0x0A
                    if byte_next:
                        if ((byte_next == bytes_linefeed) or (byte_next == bytes_carraigereturn)):
                            continue_reading=False
                        else:
                            characters_recieved += char_next         
                        char_next = ''
                        byte_next = 0
                serial_response = characters_recieved
                logging.info("User: " + str(pwd.getpwuid(os.getuid()).pw_name) + " Received Serial Response: "+str(serial_response)+" to: "+ str(self.serial_port_name) )

            #Close Port, Return Result
            serial_port.close()
            return serial_response

        except serial.SerialException as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.error(exc_type, fname, exc_tb.tb_lineno)
            logging.exception(e)
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            return e.args[0]

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.error(exc_type, fname, exc_tb.tb_lineno)
            logging.exception(e)
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            return e.args[0]


    def handle_exception(self, ex):
            logging.error("An Exception Has Occurred!")        
            logging.exception(ex)
            return(ex)  