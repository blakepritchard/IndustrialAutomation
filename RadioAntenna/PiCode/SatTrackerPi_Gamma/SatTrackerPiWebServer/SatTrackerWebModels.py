from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
    polarity_degrees_to_move = 0

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
    
    def as_dict(self):
       return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

