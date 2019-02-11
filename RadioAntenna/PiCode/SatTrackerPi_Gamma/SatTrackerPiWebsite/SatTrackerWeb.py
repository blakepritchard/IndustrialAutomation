import os
import pwd
import sys
import logging
import socket
import json

from flask import Flask, redirect, url_for, jsonify
from flask import render_template
from flask import request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

#self.serial_lock = threading.lock

sat_tracker_app = Flask(__name__)
sat_tracker_app.config.from_object(Config)
db = SQLAlchemy(sat_tracker_app)
migrate = Migrate(sat_tracker_app, db)

from SatTrackerPiWebsite import routes, SatTrackerWebModels

sat_tracker_app.testing = True
sat_tracker_app.debug = True

sat_tracker_app.logger.setLevel(logging.DEBUG)

#sat_tracker_app.config.from_envvar("SAT_TRACKER_WEB_SERIAL_CONFIG")
#sat_tracker_app.config.from_pyfile("/home/pi/src/git/IndustrialAutomation/RadioAntenna/PiCode/SatTrackerPi_Gamma/SatTrackerPiWebsite/serial_output.config")

if __name__ == "__main__":
    sat_tracker_app.run(host='0.0.0.0')



@sat_tracker_app.route("/")
def default_page():
    return redirect("http://"+socket.gethostname()+"/sat_tracker/", code=302)

@sat_tracker_app.route("/sat_tracker/", methods=["GET"])
def sat_tracker_web():
    log_text_lines_array = open("../sat_tracker_daemon.log", "r").read().split("\n")
    log_text_lines_array = log_text_lines_array[::-1]
    return render_template("sat_tracker_web.html", **locals())

@sat_tracker_app.route("/polarity/", methods=["GET"])
def polarity_control():
    return render_template("polarity.html")



# API Calls Return JSON
@sat_tracker_app.route("/sat_tracker/api/rotator/log", methods=["GET"])
def get_rotator_log():
    try:
        log_text_lines_array = open("../sat_tracker_daemon.log", "r").read().split("\n")
        log_text_lines_array = log_text_lines_array[::-1]
        json_result = json.dumps(log_text_lines_array)
        return json_result
    
    except Exception as exception:
        return handle_web_exception(exception)


def handle_web_exception(exception):
        sat_tracker_app.logger.error("An Exception Has Occurred!")        
        sat_tracker_app.log_exception(exception)
        return(exception.message)   