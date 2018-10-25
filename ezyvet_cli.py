#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Copyright (C) 2018 - DoveLewis
    Author: Avi Solomon (asolomon@dovelewis.org)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from settings import *    # This file contains login credentials do not track with git
from ezyvet import ezyvet
from pprint import pprint,pformat
import logging
import sys
import getopt

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def main():
    ''' Main function to parce commandline options
    '''
    try:
        opts, args = getopt.getopt(sys.argv[1:], "vThsa:", ["help", "debug"])
    except getopt.GetoptError as err:
        # print help information and die:
        print(err)
        usage()
        sys.exit(2)

    try:
        if len(opts) == 0 or "-h" in opts:
            usage()
            sys.exit(0)

        else:
            mode = None

            for o, a in opts:
                if o == "-v":                                   # Turn on Verbose
                    logging.getLogger().setLevel(logging.INFO)

                elif o == "--debug":                            # Turn on debugging output
                    logging.getLogger().setLevel(logging.DEBUG)

                elif o in ("-h", "--help"):                     # Print CLI usage
                    usage()
                    sys.exit

                elif o == "-T":
                    # Test the connection
                    ezy = ezyvet(SETTINGS, logger)

                elif o == "-s":
                    e = ezyvet(SETTINGS, logger)
                    logger.info("Getting ezyvet statuses.")
                    statuses =  e.getAptStats()
                    if statuses is None:
                        print("Could not retrieve statuses.")
                    else:
                        pprint(statuses)
                elif o == "-a":
                    e = ezyvet(SETTINGS, logger)
                    try:    # let's see if it is a name or ID lookup
                        id = int(a)
                        code = e.getAptStatusCode(id=id)
                        if code is None:
                            logger.error("Could not find appointment status with ID = " + str(a))
                        else:
                            print(code)
                    except ValueError:
                        # Lookup by name not ID
                        code = e.getAptStatusCode(name=a)
                        if code is None:
                            logger.error("Could not find appointment status with name = " + str(a))
                        else:
                            print(code)

                else:
                    usage()
                    msg = "Unhandled option: " + pformat(o)
                    assert False, msg
    except:
        logger.error("Something went wrong, bye.", exc_info=True)

def usage():
    print("\nCommandline ezyVet by Avi Solomon (asolomon@dovelewis.org) v0.1")
    print("USAGE: >python3 ezyvet_cli.py [OPTIONS]")
    print("\t -h or --help: Get Help (print this help text)")
    print("\t -T Test connection to API and exit")
    print("\t -s Get all appointment status codes")
    print("\t -s [id or name] Lookup appointment status code (by name or id)")
    print("\t -v: Verbose output")
    print("\t --debug: Very verbose output")
    print("")

if __name__ == "__main__":
    main()
