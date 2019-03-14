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

sat_tracker_app.testing = True
sat_tracker_app.debug = True

sat_tracker_app.logger.setLevel(logging.DEBUG)

#sat_tracker_app.config.from_envvar("SAT_TRACKER_WEB_SERIAL_CONFIG")
#sat_tracker_app.config.from_pyfile("/home/pi/src/git/IndustrialAutomation/RadioAntenna/PiCode/SatTrackerPi_Gamma/SatTrackerPiWebsite/serial_output.config")


class Rotator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rotator_name = db.Column(db.String(64), index=False, unique=True)
    rotator_commands = db.relationship("RotatorCommand", backref="Rotator", lazy=True)

    azimuth_steps = db.Column(db.Integer, index=False, unique=False)
    azimuth_degrees = db.Column(db.Float, index=False, unique=False)
    elevation_steps = db.Column(db.Integer, index=False, unique=False)
    elevation_degrees = db.Column(db.Float, index=False, unique=False)
    polarity_steps = db.Column(db.Integer, index=False, unique=False)
    polarity_degrees = db.Column(db.Float, index=False, unique=False)
    polarity_is_tracking = db.Column(db.Boolean, index=False, unique=False)
    polarity_tracking_speed = db.Column(db.Numeric, index=False, unique=False)
   
    def __repr__(self):
        return '<Rotator {}>'.format(str(self.id) + ", " + str(self.rotator_name))    

    def as_dict(self):
       return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}



class RotatorCommand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rotator_id = db.Column(db.Integer, db.ForeignKey("rotator.id"))

    issue_time = db.Column(db.DateTime, index=False, unique=False)
    execution_time = db.Column(db.DateTime, index=False, unique=False)
    command_code = db.Column(db.Integer, index=False, unique=False)
    command_value = db.Column(db.Float, index=False, unique=False)

    def __repr__(self):
        return '<RotatorCommand {}>'.format(str(self.execution_time) + ", " + str(self.command_code) + ", " + str(self.command_value) )    



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


@sat_tracker_app.route("/sat_tracker/api/rotator/status", methods=["GET"])
def get_rotator_status():
    try:
        rotator = Rotator.query.get(1)
        json_result = jsonify(rotator.as_dict())
        return json_result
    
    except Exception as exception:
        return handle_web_exception(exception)

@sat_tracker_app.route("/sat_tracker/api/rotator/status", methods=["POST"])
def set_rotator_status():
    try:
        sat_tracker_app.logger.info("a POST to set_rotator_status Has Been Recieved with data: " + request.get_data())
        str_json_post = request.get_json()
        dict_json_post = json.loads(str_json_post)     

        rotator = Rotator.query.get(dict_json_post["id"])
        sat_tracker_app.logger.debug("Found Database Record for Rotator Name:" + rotator.rotator_name )
        sat_tracker_app.logger.debug("Request Data Object:" + str(dict_json_post))
        sat_tracker_app.logger.debug("Request String Data Type:" + str(type(str_json_post))+", Dictionary Object Data Type:" + str(type(dict_json_post)) )
        
        rotator.azimuth_degrees = dict_json_post["azimuth_degrees"]
        rotator.azimuth_steps = dict_json_post["azimuth_steps"]
        rotator.elevation_degrees = dict_json_post["elevation_degrees"]
        rotator.elevation_steps = dict_json_post["elevation_steps"]
        rotator.polarity_steps = dict_json_post["polarity_steps"]
        rotator.polarity_degrees = dict_json_post["polarity_degrees"]
        if ("True" == dict_json_post["polarity_is_tracking"]):
            rotator.polarity_is_tracking = True
            rotator.polarity_tracking_speed = dict_json_post["polarity_tracking_speed"]
        else:
            rotator.polarity_is_tracking = False
            rotator.polarity_tracking_speed = 0

        db.session.commit()

        return jsonify(rotator.as_dict())
   
    except Exception as exception:
        return handle_web_exception(exception)


@sat_tracker_app.route("/sat_tracker/api/rotator/commands", methods=["GET"])
def read_rotator_status():
    try:
        commands = RotatorCommand.query.all()
        json_result = jsonify(commands.as_dict())
        return json_result
    
    except Exception as exception:
        return handle_web_exception(exception)

@sat_tracker_app.route("/sat_tracker/api/rotator/command", methods=["POST"])
def create_rotator_command():
    try:
        sat_tracker_app.logger.info("a POST to create_rotator_command Has Been Recieved with data: " + request.get_data())
        str_json_post = request.get_json()
        dict_json_post = json.loads(str_json_post)     

        sat_tracker_app.logger.debug("Request Data Object:" + str(dict_json_post))
        sat_tracker_app.logger.debug("Request String Data Type:" + str(type(str_json_post))+", Dictionary Object Data Type:" + str(type(dict_json_post)) )
        
        command = RotatorCommand()
        command.rotator_id = dict_json_post["rotator_id"]
        command.issue_time = dict_json_post["issue_time"]
        command.execution_time = dict_json_post["execution_time"]
        command.command_code = dict_json_post["command_code"]
        command.command_value = dict_json_post["command_value"]

        db.session.commit()

        return jsonify(command.as_dict())
   
    except Exception as exception:
        return handle_web_exception(exception)




################################################################################################################
# Exception Handling
def handle_web_exception(exception):
        sat_tracker_app.logger.error("An Exception Has Occurred!")        
        sat_tracker_app.log_exception(exception)
        return(exception.message)   