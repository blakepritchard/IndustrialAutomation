from flask import Flask, redirect
from flask import render_template
from flask import request
import serial
import os
import pwd
import sys
import logging
import socket

sat_tracker_app = Flask(__name__)

sat_tracker_app.testing = True
sat_tracker_app.debug = True

sat_tracker_app.logger.setLevel(logging.DEBUG)

#sat_tracker_app.config.from_envvar("SAT_TRACKER_WEB_SERIAL_CONFIG")
sat_tracker_app.config.from_pyfile("/home/pi/src/git/IndustrialAutomation/RadioAntenna/PiCode/SatTrackerPi_Gamma/SatTrackerPiWebsite/serial_output.config")

if __name__ == "__main__":
    sat_tracker_app.run(host='0.0.0.0')



@sat_tracker_app.route("/")
def default_page():
    return redirect("http://"+socket.gethostname()+"/sat_tracker/", code=302)

@sat_tracker_app.route("/sat_tracker/", methods=["GET"])
def sat_tracker_web():
    send_serial_command("AZ")
    azimuth_current = get_serial_response()

    send_serial_command("EL")
    elevation_current = get_serial_response()

    send_serial_command("PO")
    polarity_current = get_serial_response()

    return render_template("sat_tracker_web.html", **locals())

@sat_tracker_app.route("/polarity/", methods=["GET"])
def polarity_control():
    return render_template("polarity.html")

@sat_tracker_app.route("/sat_tracker/set_azimuth", methods=["POST"])
@sat_tracker_app.route("/azimuth/set_azimuth", methods=["POST"])
def set_azimuth():
    try:
        sat_tracker_app.logger.debug("a POST to set_azimuth Has Been Recieved")
        if request.method == 'POST':
            polarity_command= "AZ" + request.form['azimuth_new'] + "\n"
            return send_serial_command(polarity_command)
        else:
            return redirect("http://"+socket.gethostname()+"/sat_tracker/", code=302)
    except Exception as exception:
        sat_tracker_app.logger.error("An Exception Has Occurred!")        
        sat_tracker_app.log_exception(exception)
        return(exception.message)


@sat_tracker_app.route("/sat_tracker/set_elevation", methods=["POST"])
@sat_tracker_app.route("/elevation/set_elevation", methods=["POST"])
def set_elevation():
    try:
        sat_tracker_app.logger.debug("a POST to set_elevation Has Been Recieved")
        if request.method == 'POST':
            polarity_command= "EL" + request.form['elevation_new'] + "\n"
            return send_serial_command(polarity_command)
        else:
            return redirect("http://"+socket.gethostname()+"/sat_tracker/", code=302)
    except Exception as exception:
        sat_tracker_app.logger.error("An Exception Has Occurred!")        
        sat_tracker_app.log_exception(exception)
        return(exception.message)


@sat_tracker_app.route("/sat_tracker/set_polarity", methods=["POST"])
@sat_tracker_app.route("/polarity/set_polarity", methods=["POST"])
def set_polarity():
    try:
        sat_tracker_app.logger.debug("a POST to set_polarity Has Been Recieved")
        if request.method == 'POST':
            polarity_command= "PP" + request.form['polarity_new'] + "\n"
            return send_serial_command(polarity_command)
        else:
            return render_template("polarity.html")
    except Exception as exception:
        sat_tracker_app.logger.error("An Exception Has Occurred!")        
        sat_tracker_app.log_exception(exception)
        return(exception.message)



def send_serial_command(serial_command):
    try:
        serial_port_name = sat_tracker_app.config['SERIAL_PORT_NAME']
        print("User: " + str(pwd.getpwuid(os.getuid()).pw_name) + " is about to Send Serial Command to: "+ str(serial_port_name) )
        serial_port = serial.Serial(str(serial_port_name), 9600, rtscts=True,dsrdtr=True, timeout=0) 
        serial_port.write(serial_command.encode())
        serial_port.close()
        return redirect("http://"+socket.gethostname()+"/polarity", code=302)

    except Exception as exception:
        sat_tracker_app.logger.error("An Exception Has Occurred!")
        sat_tracker_app.log_exception(exception)
        return(exception.message)

# Read website port
def get_serial_response():
    try:
        serial_port_name = sat_tracker_app.config['SERIAL_PORT_NAME']
        serial_port = serial.Serial(str(serial_port_name), 9600, rtscts=True,dsrdtr=True, timeout=5) 

        bytes_carraigereturn = bytes("\r")
        bytes_linefeed = bytes("\n")    

        characters_recieved = ""
        continue_reading=True
        while continue_reading:
            byte_next = serial_port.read()
            char_next = byte_next.decode("utf-8")

            if byte_next:
                    
                if ((byte_next == bytes_carraigereturn) or (byte_next == bytes_linefeed)):
                    continue_reading=False
                else:
                    characters_recieved += char_next         
                char_next = ''
                byte_next = 0

        serial_port.close()
        return characters_recieved

    
    except serial.SerialException as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.critical(exc_type, fname, exc_tb.tb_lineno)
        logging.critical(e)
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
        return redirect("http://"+socket.gethostname()+"/polarity", code=302)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.critical(exc_type, fname, exc_tb.tb_lineno)
        logging.critical(e)
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
        return redirect("http://"+socket.gethostname()+"/polarity", code=302)

