#python

from SatTrackerWebModels import db
from SatTrackerWebModels import Rotator
from SatTrackerWebModels import RotatorCommand
db.create_all()
rotator = Rotator()
rotator.rotator_name="SatTrackerPi"
rotator.azimuth_steps=0
rotator.azimuth_degrees=0
rotator.elevation_steps = 0
rotator.elevation_degrees=0
rotator.polarity_steps=0
rotator.polarity_degrees=0
rotator.polarity_is_tracking=False
rotator.polarity_tracking_speed=0
db.session.add(rotator)
db.session.commit()
db.session.close()
#exit()
