from flask import Flask, redirect
from flask import render_template
from flask import request
import serial
import os
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
    return redirect("http://"+socket.gethostname()+"/polarity", code=302)

@sat_tracker_app.route("/polarity/", methods=["GET"])
def polarity_control():
    return render_template("polarity.html")

@sat_tracker_app.route("/polarity/set_polarity", methods=["POST"])
def set_polarity():
    try:
        sat_tracker_app.logger.debug("a POST to set_polarity Has Been Recieved")
        if request.method == 'POST':
            polarity_command= "PP" + request.form['newpolarity'] + "\n"
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
        print("User: " + os.environ.get('USER')+ " is about to Send Serial Command to: "+ str(serial_port_name) )
        serial_port_website = serial.Serial(str(serial_port_name), 9600, rtscts=True,dsrdtr=True, timeout=0) 
        serial_port_website.write(serial_command.encode())
        return redirect("http://"+socket.gethostname()+"/polarity", code=302)

    except Exception as exception:
        sat_tracker_app.logger.error("An Exception Has Occurred!")
        sat_tracker_app.log_exception(exception)
        return(exception.message)
