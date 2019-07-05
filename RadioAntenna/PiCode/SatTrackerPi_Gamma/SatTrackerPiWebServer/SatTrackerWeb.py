import os
import pwd
import sys
import logging
import socket
import json
import datetime

from flask import Flask, redirect, url_for, jsonify
from flask import render_template
from flask import request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from SatTrackerWebModels import Rotator
from SatTrackerWebModels import RotatorCommand
from SatTrackerWebModels import db

sat_tracker_app = Flask(__name__)
sat_tracker_app.config.from_object(Config)

db.init_app(sat_tracker_app)
SatTrackerWebModels.create_model()

#db = SQLAlchemy(sat_tracker_app)
#migrate = Migrate(sat_tracker_app, db)

sat_tracker_app.testing = True
sat_tracker_app.debug = True
sat_tracker_app.logger.setLevel(logging.DEBUG)


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
def read_rotator_commands():
    try:
        sat_tracker_app.logger.info("a GET request has been received to read_rotator_commands")
        list_of_commands = RotatorCommand.query.all()
        list_of_dictionaries = [command.as_dict() for command in list_of_commands]
        json_result = jsonify(list_of_dictionaries)
        return json_result
    
    except Exception as exception:
        return handle_web_exception(exception)

@sat_tracker_app.route("/sat_tracker/api/rotator/command", methods=["POST"])
def create_rotator_command():
    try:
        sat_tracker_app.logger.info("a POST to create_rotator_command Has Been Recieved with data: " + request.get_data() + "... get_json returned Type:"+ str(type(request.get_json())))  
        dict_json_post = request.get_json()

        sat_tracker_app.logger.debug("Request Data Object:" + str(dict_json_post))
        sat_tracker_app.logger.debug(" Dictionary Object Data Type:" + str(type(dict_json_post)) )
 
        command = RotatorCommand()
        command.rotator_id = dict_json_post["rotator_id"]
        command.issue_time = datetime.datetime.now()
        #command.execution_time = dict_json_post["execution_time"]
        command.command_code = dict_json_post["command_code"]
        command.command_value = dict_json_post["command_value"]

        db.session.add(command)
        db.session.commit()

        return jsonify(command.as_dict())
   
    except Exception as exception:
        return handle_web_exception(exception)

@sat_tracker_app.route("/sat_tracker/api/rotator/command/<int:id>", methods=["DELETE"])
def delete_rotator_command(id):
    try:
        sat_tracker_app.logger.info("a Delete request has been received to delete_rotator_command")
        command = RotatorCommand.query.get(id)
        db.session.delete(command)
        db.session.commit()

        resp = jsonify(success=True)
        resp.status_code = 200
        return resp

    except Exception as exception:
        return handle_web_exception(exception)


################################################################################################################
# Exception Handling
def handle_web_exception(exception):
        sat_tracker_app.logger.error("An Exception Has Occurred!")        
        sat_tracker_app.log_exception(exception)
        return(exception.message)   