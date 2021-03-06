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

#################################################################################################################################################################
# Worker Class to Execute Commands From Website
#################################################################################################################################################################
class SatTrackerPiWebClient:

    def __init__(self,  verbose, config_file_serial, speed_serial, url_webserver, interval):
        logging.info("Initializing Web Client Object.")
        self.rotator_id = 1
        self.verbose = verbose
        self.config_file_serial = config_file_serial
        self.url_webserver = url_webserver
        self.speed_serial = int(speed_serial)
        self.interval = float(interval)


        self.polarity_is_tracking = False
        self.polarity_tracking_speed = float(0.0)
        self.polarity_degrees_to_move = float(0.0)
        self.polarity_degrees_current = float(0.0)        

        self.polarity_steps_per_degree = int(2)
        self.polarity_degrees_per_step = float(0.5)

        self.serial_port_name = "/dev/pts/999"
        with open(self.config_file_serial, 'r') as f:
            config_dict = json.load(f)
            self.serial_port_name = config_dict['SERIAL_PORT_NAME']
        
        logging.info("Serial Port Output Set to: " + str(self.serial_port_name))

        self._timer     = None
        self.is_running = False
        self.start_time = time.time()
       

    def __del__(self):
        logging.info("Destructing Web Client, Stopping Client Loop")
        #self.scheduler.cancel(self.client_loop_event)
        
        
    def start_client_loop(self):
        try:
            logging.info("Initializing Timer With Interval: "+str(self.interval))
            self.scheduler = sched.scheduler(time.time, time.sleep)

            # sync up with system clock
            loop_start_interval = float(self.interval - (time.time() % self.interval))
            self.client_loop_event = self.scheduler.enter(loop_start_interval, 1, self._execute_client_loop, ())
            logging.info("Starting Client Loop With Interval: "+str(self.interval))
            self.scheduler.run()
        except Exception as exception:
            return self.handle_exception(exception)

    def _execute_client_loop(self):
        try:
            logging.debug("Starting Client Loop Interval." )
            self.start_time = time.time()

            logging.debug("Posting Rotator Status" )
            self.post_rotator_status()

            logging.debug("Executing Client Commands" )
            self.execute_client_commands()

            logging.debug("Executing Polarity Tracking" )
            if(self.polarity_is_tracking):
                self.execute_polarity_tracking()

            logging.info("Calculating Time" )
            current_time = time.time()
            run_time = current_time - self.start_time
            interval_next = float(self.interval - (run_time % self.interval ))
            start_time_next = float(time.time()+ interval_next)
            logging.debug("Start Time: "+str(self.start_time)+", Run Time:" + str(run_time)+ "End Time: "+ str(current_time))
            logging.debug("Interval Until Next Start Time:"+ str(interval_next) +", Next Start Time: "+ str(start_time_next))
            self.scheduler.enter(interval_next, 1, self._execute_client_loop, ())
        except Exception as exception:
            return self.handle_exception(exception)

    def execute_client_commands(self):
        try:
            url = self.url_webserver + "/sat_tracker/api/rotator/commands"
            r = requests.get(url)
            list_of_commands = r.json()
            sorted_list_of_commands = sorted(list_of_commands, key = lambda command: (command['issue_time']))

            results = [self.execute_client_command(command) for command in sorted_list_of_commands]

        except Exception as exception:
            return self.handle_exception(exception)

    def execute_client_command(self, command):
        logging.info("Execute Tracking Command Id: " + command['id'] + ", Code: " + command['command_code'] + ", Value: " +command['command_value'])
        try:
            if "PT" == command['command_code']:
                self.start_polarity_tracking(command)
                self.delete_client_command(command)
            elif "SP" == command['command_code']:
                self.stop_polarity_tracking(command)
                self.delete_client_command(command)
            elif "PO" == command['command_code']:
                self.set_polarity_json(command)
                self.delete_client_command(command)
            elif "AZ" == command['command_code']:
                self.set_azimuth_json(command)
                self.delete_client_command(command)
            elif "EL" == command['command_code']:
                self.set_elevation_json(command)
                self.delete_client_command(command)

        except Exception as exception:
            return self.handle_exception(exception)

    def delete_client_command(self, command):
        try:
            url = self.url_webserver + "/sat_tracker/api/rotator/command/"+str(command['id'])
            r = requests.delete(url)
            logging.info("Delete Issued for Tracking Command Id: " + command['id'])
        except Exception as exception:
            return self.handle_exception(exception)

    
    def start_polarity_tracking(self, command):
        try:
            self.polarity_is_tracking = True
            self.polarity_tracking_speed = float(command['command_value'])
            logging.info("Start Polarity Tracking Command Issued at: " + command['issue_time'])
        except Exception as exception:
            return self.handle_exception(exception)

    def stop_polarity_tracking(self, command):
        try:
            self.polarity_is_tracking = False
            self.polarity_tracking_speed = float(0.0)
            logging.info("Stop Polarity Tracking Command Issued at: " + command['issue_time'])

        except Exception as exception:
            return self.handle_exception(exception)

    def execute_polarity_tracking(self):
        try:
            # tracking speed in degrees per second multiplied by number of seconds per client loop interval
            logging.debug("TypeOf Speed: " + str(type(self.polarity_tracking_speed))+ ", TypeOf Interval: " + str(type(self.interval)) + ", Degrees Per Step: " + str(self.polarity_degrees_per_step))
            self.polarity_degrees_to_move += (float(self.polarity_tracking_speed) * float(self.interval))

            if(0 != self.polarity_degrees_to_move):
                # set next polarity to a value equal to steps
                steps, degrees_remainder = divmod(self.polarity_degrees_to_move, self.polarity_degrees_per_step )
                polarity_degrees_move_rounded = steps * self.polarity_degrees_per_step
                polarity_degrees_position_next = self.polarity_degrees_current + polarity_degrees_move_rounded

                self.execute_serial_command("PO"+ str(polarity_degrees_position_next)+"\n")
                
                # carry over remainder to next iteration of the client loop 
                self.polarity_degrees_to_move = degrees_remainder

        except Exception as exception:
            return self.handle_exception(exception)


    def post_rotator_status(self):
        try:
            return_val = ""
            logging.debug("getting rotator status")
            rotator_serial_response = self.get_rotator_status()
            if(rotator_serial_response != "Busy"):
                dict_json_post = json.loads(rotator_serial_response)
                dict_json_post["id"] = self.rotator_id
                dict_json_post["polarity_is_tracking"] = self.polarity_is_tracking
                dict_json_post["polarity_tracking_speed"] = self.polarity_tracking_speed
                str_json_post = json.dumps(dict_json_post)

                self.polarity_degrees_current = dict_json_post["polarity_degrees"]

                if(not isinstance(rotator_serial_response, Exception)):
                    logging.debug("Posting Rotator Status: "+str(str_json_post))
                    url = self.url_webserver + "/sat_tracker/api/rotator/status"
                    r = requests.post(url, json=str_json_post)
                    logging.debug("Post Response Text: "+str(r.text))
                else:
                    logging.error("Post_Rotator_Status recieved and will re-raise the exception: "+str(rotator_serial_response))
                    raise(rotator_serial_response)
                return_val = r.text
            else:
                logging.warning("Rotator Is Busy. Not Ready to Post Rotator Status.")

            return return_val

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
            logging.info("a set_polarity_json command has been recieved with data: " + polarity_json['command_value'])

            float_polarity_next = polarity_json['command_value']
 
            polarity_command= "PO" +  str(float_polarity_next)
            polarity_current = self.execute_serial_command(polarity_command, None)
            self.polarity_degrees_current = polarity_current
            json_result = {"polarity_degrees": polarity_current}
            return json.dumps(json_result)

        except Exception as exception:
            return self.handle_exception(exception)



    def set_elevation_json(self, elevation_json):
        try:
            json_result = ""
            logging.info("a set_elevation_json command has been recieved with data: " + elevation_json['command_value'])
            float_elevation_next = elevation_json['command_value']

            elevation_command= "EL" + str(float_elevation_next)
            logging.debug("a set_elevation Command Is Being Sent to the Serial Port: " + elevation_command)

            elevation_current = self.execute_serial_command(elevation_command, None)
            json_result = {"elevation_degrees": elevation_current}
            return json_result

        except Exception as exception:
            return self.handle_exception(exception)


    #@sat_tracker_app.route("/sat_tracker/set_azimuth", methods=["GET","POST"])
    #@sat_tracker_app.route("/azimuth/set_azimuth", methods=["POST"])
    def set_azimuth_json(self, azimuth_json):
        try:
            json_result = ""
            logging.info("a set_azimuth_json command is being sent with data: " + azimuth_json['command_value'])
            float_azimuth_next = azimuth_json['command_value']
            
            azimuth_command= "AZ" + str(float_azimuth_next) 
            logging.debug("a set_azimuth Command Is Being Sent to the Serial Port: " + azimuth_command)

            azimuth_current = self.execute_serial_command(azimuth_command)
            json_result = {"azimuth_degrees": azimuth_current}
            return json_result

        except Exception as exception:
            return self.handle_exception(exception)


    # Send Serial Command, Get Serial Response
    def execute_serial_command(self, serial_command, serial_timeout=0):

        try:
            #self.serial_lock.acquire()
            serial_response = ""
            serial_port = serial.Serial(str(self.serial_port_name), self.speed_serial, rtscts=True,dsrdtr=True, timeout=serial_timeout) 
            logging.debug("User: " + str(pwd.getpwuid(os.getuid()).pw_name) + " is about to Send Serial Command: "+str(serial_command)+" to: "+ str(self.serial_port_name) )

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
                logging.debug("User: " + str(pwd.getpwuid(os.getuid()).pw_name) + " Received Serial Response: "+str(serial_response)+" to: "+ str(self.serial_port_name) )

            #Close Port, Return Result
            serial_port.close()
            return serial_response

        except serial.SerialException as e:
            logging.error("A Serial Exception Has Occurred!")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            #logging.error(exc_type, fname, exc_tb.tb_lineno)
            logging.exception(e)
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            return e.args[0]

        except Exception as e:
            logging.error("A General Exception Has Occurred!")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            #logging.error(exc_type, fname, exc_tb.tb_lineno)
            logging.exception(e)
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            return e.args[0]


    def wait_until_rotator_ready(self, serial_timeout=0):

        try:
            #self.serial_lock.acquire()
            serial_response = ""
            serial_port = serial.Serial(str(self.serial_port_name), self.speed_serial, rtscts=True,dsrdtr=True, timeout=serial_timeout) 
            logging.info("User: " + str(pwd.getpwuid(os.getuid()).pw_name) + " is waiting until Rotator is Ready, Listening to Port: "+ str(self.serial_port_name) )

            # Send Command
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
            logging.info("User: " + str(pwd.getpwuid(os.getuid()).pw_name) + " Received Serial Response: "+str(serial_response)+" from Port: "+ str(self.serial_port_name) + ", at time: " + str(time.time()))

            #Close Port, Return Result
            serial_port.close()
            return serial_response

        except serial.SerialException as e:
            logging.error("A Serial Exception Has Occurred While Waiting!")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            #logging.error(exc_type, fname, exc_tb.tb_lineno)
            logging.exception(e)
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            return e.args[0]

        except Exception as e:
            logging.error("A General Exception Has Occurred While Waiting!")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            #logging.error(exc_type, fname, exc_tb.tb_lineno)
            logging.exception(e)
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            return e.args[0]


    def handle_exception(self, ex):
            logging.error("An Exception Has Occurred!")        
            logging.exception(ex)
            return(ex)  

#####################################################################################################################################


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
    # serial_config_filename = ("/home/pi/src/git/IndustrialAutomation/RadioAntenna/PiCode/SatTrackerPi_Gamma/SatTrackerPiWebClient/webclient_serial.config")

    # Process arguments
    args = parser.parse_args()
    logging.basicConfig(filename='sat_tracker_pi_web_client.log', filemode='w', level=int(args.loglevel), format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.info("Verbose mode on Log Level: "+str(args.loglevel))
    
    sat_tracker_webclient = SatTrackerPiWebClient(args.loglevel, args.rotator, args.speed, args.webserver, args.interval)

    logging.info("Web Client Object Initialized at" + str(sat_tracker_webclient.start_time)+", Beginning to Wait for Rotator Ready")
    sat_tracker_webclient.wait_until_rotator_ready()

    logging.info("Starting Web Client Loop")
    sat_tracker_webclient.start_client_loop()

    logging.info("Exiting Main")
    return 0

if __name__ == "__main__":
    r = main()
    logging.info("Exiting with Return Code: "+str(r))
    sys.exit(r)

