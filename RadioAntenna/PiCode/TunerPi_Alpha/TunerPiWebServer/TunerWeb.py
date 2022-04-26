# from flask import Flask
# app = Flask(__name__)

# @app.route("/")
# def hello():
#     return "Hello World!"

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

from TunerWebModels import Rotator
from TunerWebModels import RotatorCommand
from TunerWebModels import db

tuner_web_app = Flask(__name__)
tuner_web_app.config.from_object(Config)

db.init_app(tuner_web_app)
#db = SQLAlchemy(tuner_web_app)

migrate = Migrate(tuner_web_app, db)

tuner_web_app.testing = True
tuner_web_app.debug = True
tuner_web_app.logger.setLevel(logging.DEBUG)

# #if __name__ == "__main__":
# #    tuner_web_app.run(host='0.0.0.0')

@tuner_web_app.route("/")
def hello():
    return "Hello World Again!"

# @tuner_web_app.route("/")
# def default_page():
#     return redirect("http://"+socket.gethostname()+"/tuner/", code=302)

@tuner_web_app.route("/tuner/", methods=["GET"])
def tuner_web():
    # log_text_lines_array = open("../tuner_pi_daemon.log", "r").read().split("\n")
    # log_text_lines_array = log_text_lines_array[::-1]
    return render_template("tuner_web.html", **locals())
    return "Hello Tuner "

@tuner_web_app.route("/polarity/", methods=["GET"])
def polarity_control():
    return render_template("polarity.html")



# API Calls Return JSON
@tuner_web_app.route("/tuner/api/rotator/log", methods=["GET"])
def get_rotator_log():
    try:
        log_text_lines_array = open("../tuner_pi_daemon.log", "r").read().split("\n")
        log_text_lines_array = log_text_lines_array[::-1]
        json_result = json.dumps(log_text_lines_array)
        return json_result
    
    except Exception as exception:
        return handle_web_exception(exception)


@tuner_web_app.route("/tuner/api/rotator/status", methods=["GET"])
def get_rotator_status():
    try:
        rotator = Rotator.query.get(1)

        if(rotator is None):
            tuner_web_app.logger.info("Rotator Database Record Not Found. Creating New Rotator Object.")
            rotator =  create_rotator()            
        else:
            tuner_web_app.logger.debug("Found Database Record for Rotator Name:" + rotator.rotator_name)

        json_result = jsonify(rotator.as_dict())
        return json_result
    
    except Exception as exception:
        return handle_web_exception(exception)

@tuner_web_app.route("/tuner/api/rotator/status", methods=["POST"])
def set_rotator_status():
    try:
        tuner_web_app.logger.info("a POST to set_rotator_status Has Been Recieved with data: " + request.get_data())
        str_json_post = request.get_json()
        dict_json_post = json.loads(str_json_post)     

        rotator = Rotator.query.get(dict_json_post["id"])

        if(rotator is None):
            tuner_web_app.logger.info("Rotator Database Record Not Found. Creating New Rotator Object.")
            rotator =  create_rotator()
        else:
            tuner_web_app.logger.debug("Found Database Record for Rotator Name:" + rotator.rotator_name )
            tuner_web_app.logger.debug("Request Data Object:" + str(dict_json_post))
            tuner_web_app.logger.debug("Request String Data Type:" + str(type(str_json_post))+", Dictionary Object Data Type:" + str(type(dict_json_post)) )

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

def create_rotator():
    tuner_web_app.logger.info("Instantiating New Rotator Object With Default Values.")
    rotator = Rotator()
    db.session.add(rotator)
    db.session.commit()
    return rotator

@tuner_web_app.route("/tuner/api/rotator/commands", methods=["GET"])
def read_rotator_commands():
    try:
        tuner_web_app.logger.info("a GET request has been received to read_rotator_commands")
        list_of_commands = RotatorCommand.query.all()
        list_of_dictionaries = [command.as_dict() for command in list_of_commands]
        json_result = jsonify(list_of_dictionaries)
        return json_result
    
    except Exception as exception:
        return handle_web_exception(exception)

@tuner_web_app.route("/tuner/api/rotator/command", methods=["POST"])
def create_rotator_command():
    try:
        tuner_web_app.logger.info("a POST to create_rotator_command Has Been Recieved with data: " + request.get_data() + "... get_json returned Type:"+ str(type(request.get_json())))  
        dict_json_post = request.get_json()

        tuner_web_app.logger.debug("Request Data Object:" + str(dict_json_post))
        tuner_web_app.logger.debug(" Dictionary Object Data Type:" + str(type(dict_json_post)) )
 
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

@tuner_web_app.route("/tuner/api/rotator/command/<int:id>", methods=["DELETE"])
def delete_rotator_command(id):
    try:
        tuner_web_app.logger.info("a Delete request has been received to delete_rotator_command")
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
        tuner_web_app.logger.error("An Exception Has Occurred!")        
        tuner_web_app.log_exception(exception)
        return(exception.message)   