from flask import Flask
from flask import render_template
from flask import request
import serial
import os
import logging

logging.basicConfig(filename='sat_tracker_web.log',level=logging.DEBUG)
serial_config = open("serial_output.config")
serial_port_name = serial_config.read()

first_app = Flask(__name__)
if __name__ == "__main__":
 first_app.run(host='0.0.0.0')

@first_app.route("/")
@first_app.route("/polarity/", methods=["GET"])
def polarity_control():
 return render_template("polarity.html")

@first_app.route("/set_polarity", methods=["POST"])
def set_polarity():
    try:
        if request.method == 'POST':
            polarity_command= "PP" + request.form['newpolarity'] + "\n"
            return send_serial_command(polarity_command)
        else:
            return render_template("polarity.html")
    except Exception as exception:
        logging.warning(exception)

def send_serial_command(serial_command):
    try:
        serial_port_website = serial.Serial(serial_port_name, 9600, rtscts=True,dsrdtr=True, timeout=0) 
        serial_port_website.write(serial_command.encode())
        return render_template("polarity.html")

    except Exception as exception:
        logging.warning(exception)

 
