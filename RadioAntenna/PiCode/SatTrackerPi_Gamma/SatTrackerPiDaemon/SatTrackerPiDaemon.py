#!/usr/local/bin/python2.7
# encoding: utf-8
'''
SatTrackerPiDaemon.SatTrackerPiDaemon -- shortdesc

SatTrackerPiDaemon.SatTrackerPiDaemon is a description

It defines classes_and_methods

@author:     Blake Pritchard

@copyright:  2017 Blake Pritchard. All rights reserved.

@license:    license

@contact:    user_email
@deffield    updated: Updated
'''


import sys
import os
import serial

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

# Import Local Libraries
path_runtime = os.path.dirname(__file__)
path_parent = os.path.abspath(os.path.join(path_runtime, os.pardir))
path_lib_rotor = os.path.join(path_parent, "Rotator")


sys.path.insert(0, os.path.abspath(path_parent))
sys.path.insert(0, os.path.abspath(path_lib_rotor))
print(sys.path)

import Rotator
device_rotator = Rotator.Rotator()


#Init Variables
__all__ = []
__version__ = 0.1
__date__ = '2017-12-18'
__updated__ = '2017-12-18'

DEBUG = 1
TESTRUN = 0
PROFILE = 0


class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg
    
    
#################################################################
# Main
#################################################################
def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Blake Pritchard on %s.
  Copyright 2017 Blake Pritchard. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument("-p", "--port", dest="serial port device", type=string, help="set serial port [default: %(default)s]")
        parser.add_argument("-s", "--speed", dest="serial port speed", type=int, help="set serial port speed [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)       
         

        # Process arguments
        args = parser.parse_args()
        verbose = args.verbose
        serial_port_dev = args.port
        serial_port_speed = int(args.speed)
        
        if verbose > 0: print("Verbose mode on")       
        if(''==serial_port_dev): serial_port_dev = '/dev/pts/4'
        if(''==serial_port_speed): serial_port_speed = 9600
        
        ser = serial.Serial(serial_port_dev, 9600, rtscts=True,dsrdtr=True)
        bytes_carraigereturn = bytes("\r", "UTF8")
        bytes_linefeed = bytes("\n", "UTF8")    

        command = ""
        
        while True:
            byte_next = ser.read()
            char_next = byte_next.decode("utf-8")
            if byte_next:
                
                if ((byte_next == bytes_carraigereturn) or (byte_next == bytes_linefeed)):
                    print(command)
                    device_rotator.execute_easycomm2_command(command)
                    command = ""  
                elif '!'==char_next:
                    print('.')             
                else:
                    command += char_next
                    
                char_next = ''
                byte_next = 0
                    
    
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    
    except serial.SerialException as e:
        print(e.msg)
        raise       # XXX handle instead of re-raise?

    except Exception as e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
        sys.argv.append("-v")
        sys.argv.append("-r")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'SatTrackerPiDaemon.SatTrackerPiDaemon_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())