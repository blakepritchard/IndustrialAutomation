
import sys
import os

# Import Local Libraries
path_runtime = os.path.dirname(__file__)
path_parent = os.path.abspath(os.path.join(path_runtime, os.pardir))
path_lib_rotor = os.path.join(path_parent, "Rotator")
print("Rotor Lib Path:", path_lib_rotor) 

import Rotator