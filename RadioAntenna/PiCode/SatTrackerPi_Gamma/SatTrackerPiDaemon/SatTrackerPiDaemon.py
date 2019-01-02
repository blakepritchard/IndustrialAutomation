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
# print(sys.path)

import Rotator
device_rotator = Rotator.Rotator()


#Init Variables
__all__ = []
__version__ = 0.1
__date__ = '2018-12-28'
__updated__ = '2018-12-28'

DEBUG = 0
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
        parser.add_argument("-l", "--loglevel", dest="loglevel", help="set loglevel level [default: %(default)s]")
        parser.add_argument("-r", "--rotctl", dest="rotctl", help="set rotctl-gpredict serial port [default: %(default)s]")
        parser.add_argument("-w", "--website", dest="website", help="set website serial port [default: %(default)s]")
        parser.add_argument("-s", "--speed", dest="speed", type=int, help="set serial port speed [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)       

        print("Processing Arguments")

        # Process arguments
        args = parser.parse_args()
        verbose = args.loglevel
        name_port_rotctl = args.rotctl
        name_port_website = args.website
        
        speed_serial = args.speed



        #set rotator verbosity
        device_rotator.set_verbosity(verbose)
        
        if verbose > 0: 
                print("Verbose mode on Log Level: "+str(verbose))       
        if(''==name_port_rotctl): 
            name_port_rotctl = '/dev/ttyUSB1'
        print("RotCtl Port: " + name_port_rotctl)

        """if(''==serial_port_speed): 
                serial_port_speed = 9600
        print("Using Speed: " + serial_port_speed)
        """
        print("Opening serial port for rotctl.")
        serial_port_rotctl = serial.Serial(name_port_rotctl, 9600, rtscts=True,dsrdtr=True, inter_byte_timeout=200)

        print("WebSite Port: " + name_port_website)
        print("Opening serial port for website.")
        serial_port_website = serial.Serial(name_port_website, 9600, rtscts=True,dsrdtr=True, inter_byte_timeout=200)

        print("Port Open. Setting Constants.")
        bytes_carraigereturn = bytes("\r")
        bytes_linefeed = bytes("\n")    

        print("Reading Serial Port Loop")
        
        command_rotctl = ""
        command_website = ""
        print_newline = False
        while True:

            # Read rotctl port
            byte_next_rotctl = serial_port_rotctl.read()
            char_next_rotctl = byte_next_rotctl.decode("utf-8")

            if verbose > 0: print('-')
            if byte_next_rotctl:
                
                if ((byte_next_rotctl == bytes_carraigereturn) or (byte_next_rotctl == bytes_linefeed)):
                    if verbose > 0: print(command_rotctl)
                    rotator_response = device_rotator.execute_easycomm2_command(command_rotctl)
                    # serial_port_rotctl.write(rotator_response)
                    command_rotctl = ""  
                elif '!'==char_next_rotctl:
                    print('!'),
                    print_newline = True 
                else:
                    command_rotctl += char_next_rotctl
                    print(char_next_rotctl)
                    if print_newline:
                        print','
                        print_newline = False
                    
                char_next_rotctl = ''
                byte_next_rotctl = 0

            # Read website port
            byte_next_website = serial_port_website.read()
            char_next_website = byte_next_website.decode("utf-8")

            if verbose > 0: print('-')
            if byte_next_website:
                
                if ((byte_next_website == bytes_carraigereturn) or (byte_next_website == bytes_linefeed)):
                    if verbose > 0: print(command_website)
                    website_response = device_rotator.execute_website_command(command_website)
                    serial_port_website.write(website_response)
                    command_website = ""  
                elif '!'==char_next_website:
                    print('!'),
                    print_newline = True 
                else:
                    command_website += char_next_website
                    if print_newline:
                        print','
                        print_newline = False
                    
                char_next_website = ''
                byte_next_website = 0
        
            if verbose > 4: print('.')

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    
    except serial.SerialException as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
        
        if DEBUG or TESTRUN:
            raise(e)
        
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
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
