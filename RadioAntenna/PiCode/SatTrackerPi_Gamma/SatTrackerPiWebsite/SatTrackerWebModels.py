from SatTackerPiWeb import db

class Rotator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ratator_name = db.Column(db.String(64), index=True, unique=True)
    rotator_commands = db.relationship("RotatorCommand", backref="Rotator", lazy=True)

    azimuth_steps = db.Column(db.Integer, index=False, unique=False)
    azimuth_degrees = db.Column(db.Float, index=False, unique=False)
    elevation_steps = db.Column(db.Integer, index=False, unique=False)
    elevation_degrees = db.Column(db.Float, index=False, unique=False)
    polarity_steps = db.Column(db.Integer, index=False, unique=False)
    polarity_degrees = db.Column(db.Float, index=False, unique=False)
    polarity_is_tracking = db.Column(db.Boolean, index=False, unique=False)
    polarity_tracking_speed = db.Column(db.Boolean, index=False, unique=False)
   
    def __repr__(self):
        return '<Rotator {}>'.format(self.id + ", " + self.ratator_name)    



class RotatorCommand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rotator_id = db.Column(db.Integer, db.ForeignKey("rotator.id"))

    issue_time = db.Column(db.DateTime, index=False, unique=False)
    execution_time = db.Column(db.DateTime, index=False, unique=False)
    command_code = db.Column(db.Integer, index=False, unique=False)
    command_value = db.Column(db.Float, index=False, unique=False)

    def __repr__(self):
        return '<RotatorCommand {}>'.format(self.execution_time + ", " + self.command_code + ", " + self.command_value )    