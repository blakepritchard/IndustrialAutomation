from flask import Flask
from flask import render_template
from flask import request
import serial
import os


sat_tracker_app = Flask(__name__)
if __name__ == "__main__":
 sat_tracker_app.run(host='0.0.0.0')

@sat_tracker_app.route("/")
@sat_tracker_app.route("/polarity/", methods=["GET"])
def polarity_control():
 return render_template("polarity.html")

@sat_tracker_app.route("/set_polarity", methods=["POST"])
def set_polarity():
    try:
        if request.method == 'POST':
            polarity_command= "PP" + request.form['newpolarity'] + "\n"
            return send_serial_command(polarity_command)
        else:
            return render_template("polarity.html")
    except Exception as exception:
        sat_tracker_app.log_exception(exception)

def send_serial_command(serial_command):
    try:
        serial_port_website = serial.Serial("/dev/pts/0", 9600, rtscts=True,dsrdtr=True, timeout=0) 
        serial_port_website.write(serial_command.encode())
        return render_template("polarity.html")

    except Exception as exception:
        sat_tracker_app.log_exception(exception)
