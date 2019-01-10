from flask import Flask
from flask import render_template
from flask import request
import serial
import os

first_app = Flask(__name__)

@first_app.route("/")
@first_app.route("/polarity/", methods=["GET"])
def polarity_control():
 return render_template("polarity.html")

@first_app.route("/set_polarity", methods=["POST"])
def set_polarity():
 if request.method == 'POST':
  polarity_command= "PP" + request.form['newpolarity'] + "\n"
  return send_serial_command(polarity_command)
 else:
  return render_template("polarity.html")

def send_serial_command(serial_command):
 port_name=os.environ["SAT_TRACKER_WEB_OUT"]
 serial_port_website = serial.Serial(port_name, 9600, rtscts=True,dsrdtr=True, timeout=0) 
 serial_port_website.write(serial_command.encode())
 return render_template("polarity.html")

if __name__ == "__main__":
 first_app.run(host='0.0.0.0')
