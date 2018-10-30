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
        opts, args = getopt.getopt(sys.argv[1:], "vThsa:c:p:d:",
                                   [
                                       "help",
                                       "debug",
                                       "aptStatCode=",
                                       "max=",
                                       "detailTypes",
                                       "pretty",
                                       "animal=",
                                       "animalColor="
                                    ]
                                   )
    except getopt.GetoptError as err:
        # print help information and die:
        print(err)
        usage()
        sys.exit(2)

    try:
        args = sys.argv

        if len(opts) == 0 or "-h" in args or "--help" in args:
            usage()
            sys.exit

        else:
            # Setup debugging
            if "-v" in args or "--verbose" in args:
                logging.getLogger().setLevel(logging.INFO)
            elif "--debug" in args:
                logging.getLogger().setLevel(logging.DEBUG)

            logger.info("Got OPTS: " + pformat(opts))
            # Setup max records returned
            max = 1                                             # Set to None or 1 (the library defaults to 1)
            for o, a in opts:                                   # First find out if we have to set maxpages
                if o == "--max":
                    max = int(round(int(opts["max"]))//10)      # round max records to nearest 10 then devide by to to get max pages

            logger.info("Limiting records to " + str(max))

            # Setup output formatting
            pretty = False
            if "--pretty" in args:                              # How do they want the output formatted
                pretty = True
                logger.info("Setting formatting to pretty")

            for o, a in opts:
                if not a:
                    a = "{}"                                    # if user provides an empty string as an argument, make it JSONable

                if o in ("--debug", "--verbose", "-v", "--pretty", "--max"):   # skip things handled earlier
                    pass

                elif o == "-T":                                 # Test the connection to ezyvet
                    getData("-T")

                elif o == "-s":                                 # get all appointment status codes (as JSON)
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Getting ezyvet statuses.")
                    data =  e.getAptStatus()
                    printFormatted(data, pretty)

                elif o == "--aptStatCode":                      # lookup a status code by name or ID
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    code = lookupStatus(e,a)
                    if code is not None:
                        printFormatted(data, pretty)

                elif o == "-a":                                 # lookup appointments
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up appointments with filter: " + str(a))
                    data = e.getAppointment(filter = json.loads(a), maxpages=max)
                    if data is not None:
                        printFormatted(data, pretty)

                elif o == "-c":                                 # lookup consults
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up consults with filter: " + str(a))
                    data = e.getConsult(filter = json.loads(a), maxpages=max)
                    if data is not None:
                        printFormatted(data, pretty)

                elif o == "-p":                                 # lookup contacts
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up contacts with filter: " + str(a)
                    data = e.getContact(filter = json.loads(a), maxpages=max)
                    if data is not None:
                        printFormatted(data, pretty)

                elif o == "-d":                                 # lookup contact details
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up contacts detail with filter: " + str(a))
                    data = e.getContact(filter = json.loads(a), maxpages=max)
                    if data is not None:
                        printFormatted(data, pretty)

                elif o == "--detailTypes":                     # lookup contacts detail types
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up contacts detail types")
                    data = e.getContactDetailTypes()
                    if data is not None:
                        printFormatted(data, pretty)

                elif o == "--animal":                           # lookup animals
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up animal with filter " +str(a) )
                    data = e.getAnimal(filter = json.loads(a), maxpages=max)
                    if data is not None:
                        printFormatted(data, pretty)

                elif o == "--animalColor":                       # lookup animal colors
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up animal colors with filter " +str(a) )
                    data = e.getAnimal(filter = json.loads(a), maxpages=max)
                    if data is not None:
                        printFormatted(data, pretty)

                else:
                    usage()
                    msg = "Unknown option: " + pformat(o)
                    sys.exit

    except:
        logger.error("Something went wrong. Please report issies to asolomon@dovelewis.org.", exc_info=True)

def printFormatted(data, pretty):
    """
    Format output then print on screen.
    """
    if not data:
        return None
    elif pretty is True:
        pprint(data)            # Make human readable
    else:
        print(json.dumps(data)) # output JSON

def usage():
    print("\nCommandline ezyVet by Avi Solomon (asolomon@dovelewis.org) v0.2.0")
    print("USAGE: >python3 ezyvet_cli.py [OPTIONS]")
    print("\t -h or --help:     Get Help (print this help text)")
    print("\t -T                Test connection to API and exit")
    print("\t -s                Get all appointment status codes")
    print("\t -a  \"[filters | empty string]\"  Lookup appointments ")
    print("\t -c \"[filters | empty string]\"   Lookup consults ")
    print("\t -p \"[filters | empty string]\"   Lookup contacts ")
    print("\t --animal \"[filters | empty string]\"   Lookup animals ")
    print("\t --animalColor \"[filters | empty string]\"   Lookup animal colors")
    print("\t --max [int]       Maximum records returned rounded to the nearest 10.")
    print("\t --aptStatCode [id|name] Lookup appointment status code (by name or id)")
    print("\t --detailTypes get the contact detail types, like \"Mobile\" or \"email\"")
    print("\t -v:               Verbose output")
    print("\t --debug           Very verbose output")
    print("\t --pretty          Human readable output")
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
