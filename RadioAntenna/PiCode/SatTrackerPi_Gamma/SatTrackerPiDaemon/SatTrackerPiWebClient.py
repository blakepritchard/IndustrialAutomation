import sys
import serial
import logging

def main(argv=None):
    serial_config_filename = ("/home/pi/src/git/IndustrialAutomation/RadioAntenna/PiCode/SatTrackerPi_Gamma/SatTrackerPiDaemon/webclient_serial.config")

if __name__ == "__main__":
    sys.exit(main())


def get_rotator_status():
    azimuth_current = execute_serial_command("AZ", None)
    elevation_current = execute_serial_command("EL", None)
    polarity_current = execute_serial_command("PO", None)

#c@sat_tracker_app.route("/sat_tracker/api/rotator/status", methods=["GET"])
def get_rotator_status():
    try:
        json_result = execute_serial_command("RS", None)
        logging.debug("Rotator Status: " + json_result)
        return json_result
    
    except Exception as exception:
        return handle_web_exception(exception)

#@sat_tracker_app.route("/sat_tracker/api/rotator/polarity", methods=["POST"])
def set_polarity_json():
    try:
        json_result = ""
        sat_tracker_app.logger.info("a POST to set_polarity_json Has Been Recieved with data: " + request.get_data())
        obj_polarity_next = request.get_json(force=True)
        float_polarity_next = obj_polarity_next['polarity_new']
        if request.method == 'POST':
            polarity_command= "PP" +  str(float_polarity_next)
            polarity_current = execute_serial_command(polarity_command, None)
            json_result = {"polarity_degrees": polarity_current}
        return json.dumps(json_result)

    except Exception as exception:
        return handle_web_exception(exception)


#@sat_tracker_app.route("/sat_tracker/set_elevation", methods=["GET","POST"])
#@sat_tracker_app.route("/elevation/set_elevation", methods=["POST"])
def set_elevation():
    try:
        sat_tracker_app.logger.debug("a POST to set_elevation Has Been Recieved")
        if request.method == 'POST':
            polarity_command= "EL" + request.form['elevation_new'] 
            execute_serial_command(polarity_command)
        return redirect("http://"+socket.gethostname()+"/sat_tracker/", code=302)

    except Exception as exception:
        return handle_web_exception(exception)


#@sat_tracker_app.route("/sat_tracker/set_azimuth", methods=["GET","POST"])
#@sat_tracker_app.route("/azimuth/set_azimuth", methods=["POST"])
def set_azimuth():
    try:
        sat_tracker_app.logger.debug("a POST to set_azimuth Has Been Recieved")
        if request.method == 'POST':
            polarity_command= "AZ" + request.form['azimuth_new'] 
            execute_serial_command(polarity_command)
        return redirect("http://"+socket.gethostname()+"/sat_tracker/", code=302)

    except Exception as exception:
        return handle_web_exception(exception)






# Send Serial Command, Get Serial Response
def execute_serial_command(serial_command, serial_timeout=0):

    try:
        #self.serial_lock.acquire()
        serial_response = ""
        serial_port_name = sat_tracker_app.config['SERIAL_PORT_NAME']
        serial_port = serial.Serial(str(serial_port_name), 9600, rtscts=True,dsrdtr=True, timeout=serial_timeout) 
        sat_tracker_app.logger.info("User: " + str(pwd.getpwuid(os.getuid()).pw_name) + " is about to Send Serial Command: "+str(serial_command)+" to: "+ str(serial_port_name) )

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
            sat_tracker_app.logger.info("User: " + str(pwd.getpwuid(os.getuid()).pw_name) + " Received Serial Response: "+str(serial_response)+" to: "+ str(serial_port_name) )

        #Close Port, Return Result
        serial_port.close()
        return serial_response

    except serial.SerialException as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sat_tracker_app.logger.error(exc_type, fname, exc_tb.tb_lineno)
        sat_tracker_app.log_exception(e)
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
        return redirect("http://"+socket.gethostname()+"/polarity", code=302)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        sat_tracker_app.logger.error(exc_type, fname, exc_tb.tb_lineno)
        sat_tracker_app.log_exception(e)
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
        return redirect("http://"+socket.gethostname()+"/polarity", code=302)
    
    finally:
        #serial_lock.release()
