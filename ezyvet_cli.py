#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2018 - DoveLewis
# Author: Avi Solomon (asolomon@dovelewis.org)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from settings import *    # This file contains login credentials do not track with git
from ezyvet import ezyvet
from pprint import pprint,pformat
import logging
import sys
import getopt
import json

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def main():
    ''' Main function to parce commandline options
    '''
    try:
        opts, args = getopt.getopt(sys.argv[1:], "vThsa:c:p:d:", ["help", "debug", "aptStatCode=", "max=", "detailTypes"])
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

            # First find out if we have to set maxpages
            max = None
            for o, a in opts:
                if o == "--max":
                    max = int(round(int(a))//10)      # round max records to nearest 10 then devide by to to get max pages
                    logger.info("Limiting records to " + str(max))

            for o, a in opts:
                if o == "-v":                                   # Turn on Verbose
                    logging.getLogger().setLevel(logging.INFO)

                elif o == "--debug":                            # Turn on debugging output
                    logging.getLogger().setLevel(logging.DEBUG)

                elif o in ("-h", "--help"):                     # Print CLI usage
                    usage()
                    sys.exit

                elif o == "-T":                                 # Test the connection to ezyvet
                    e = ezyvet.ezyvet(SETTINGS, logger)

                elif o == "-s":                                 # get all appointment status codes (as JSON)
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Getting ezyvet statuses.")
                    statuses =  e.getAptStatus()
                    if statuses is None:
                        print("Could not retrieve statuses.")
                    else:
                        pprint(statuses)

                elif o == "--aptStatCode":                      # lookup a status code by name or ID
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    code = lookupStatus(e,a)
                    if code is not None:
                        print(code)

                elif o == "-a":                                 # lookup appointments
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up appointments with filter: " + str(a))
                    if max is None:
                        max = 1
                    if not a:
                        a = "{}"

                    logger.info("Limiting records to " + str(max))
                    data = e.getAppointment(filter = json.loads(a), maxpages=max)
                    if data is not None:
                        pprint(data)

                elif o == "--max":                              # check if max is set alone
                    logger.info("Max records option set to " + str(a))
                    if len(opts) == 1:
                        print("The option --max should be specified with a query like -a, but not alone.")

                elif o == "-c":                                 # lookup consults
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up consults with filter: " + str(a))
                    if max is None:
                        max = 1
                    if not a:
                        a = "{}"

                    data = e.getConsult(filter = json.loads(a), maxpages=max)
                    if data is not None:
                        pprint(data)

                elif o == "-p":                                 # lookup contacts
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up contacts with filter: " + str(a))
                    if max is None:
                        max = 1
                    if not a:
                        a = "{}"

                    data = e.getContact(filter = json.loads(a), maxpages=max)
                    if data is not None:
                        pprint(data)

                elif o == "-d":                                 # lookup contact details
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up contacts detail with filter: " + str(a))
                    if max is None:
                        max = 1
                    if not a:
                        a = "{}"

                    data = e.getContact(filter = json.loads(a), maxpages=max)
                    if data is not None:
                        pprint(data)

                elif o == "--detailTypes":                     # lookup contacts detail types
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up contacts detail types")
                    data = e.getContactDetailTypes()
                    if data is not None:
                        pprint(data)

                else:
                    usage()
                    msg = "Unhandled option: " + pformat(o)
                    assert False, msg
    except:
        logger.error("Something went wrong, bye.", exc_info=True)

def usage():
    print("\nCommandline ezyVet by Avi Solomon (asolomon@dovelewis.org) v0.1.1")
    print("USAGE: >python3 ezyvet_cli.py [OPTIONS]")
    print("\t -h or --help: Get Help (print this help text)")
    print("\t -T Test connection to API and exit")
    print("\t -s Get all appointment status codes")
    print("\t -a \"[filters as json or empty string]\" Lookup appointments ")
    print("\t -c \"[filters as json or empty string]\" Lookup consults ")
    print("\t -p \"[filters as json or empty string]\" Lookup contacts ")
    print("\t --max [int] Maximum records returned. Will be rounded to the nearest multiple of 10, default 10.")
    print("\t --aptStatCode [id|name] Lookup appointment status code (by name or id)")
    print("\t -v: Verbose output")
    print("\t --debug: Very verbose output")
    print("")

def lookupStatus(e, lookup):
    """ Given a ezyvet instance, lookup a status code or ID
        Returns: Code name, ID or None
    """
    logger.info("Looking up status: " + str(lookup))
    code = e.getAptStatusCode(lookup)
    if code is None:
        logger.error("Could not find appointment status with ID = " + str(a))
    else:
        return(code)


def round( n ):
    """ return n rounded to the number to nearest 10
    """
    logger.debug("Rounding " + str(n))
    if n < 10:
        logger.debug("Less than 10 returning 10 ")
        return 10

    a = (n // 10) * 10  # Smaller multiple
    b = a + 10 # Larger multiple
    logger.debug("Round val a = " + str(a) + " val b = " + str(b))
    return (b if n - a > b - n else a) # Return of closest of two

if __name__ == "__main__":
    main()
