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
        opts, args = getopt.getopt(
                        sys.argv[1:],
                        "vThdpm:",
                           [
                                "address=",
                                "animal=",
                                "animalColor=",
                                "appointment="
                                "appointmentStatus",
                                "appointmentStatusLookup=",
                                "appointmentType",
                                "assessment=",
                                "attachment=",
                                "breeds=",
                                "communication=",
                                "consult=",
                                "contact=",
                                "contactDetail=",
                                "contactDetailType",
                                "country=",
                                "diagnostic=",
                                "diagnosticResult=",
                                "diagnosticResultItem=",
                                "diagnosticRequest=",
                                "diagnosticRequestItems=",
                                "file=",
                                "integratedDiagnostic=",
                                "healthStatus=",
                                "history=",
                                "invoice=",
                                "invoiceLine=",
                                "operation=",
                                "payment=",
                                "paymentMethod=",
                                "physicalExam=",
                                "plan=",
                                "prescription=",
                                "prescriptionItems=",
                                "presentingProblem=",
                                "presentingProblemLink=",
                                "product=",
                                "productGroup=",
                                "purchaseOrder=",
                                "purchaseOrderItem=",
                                "receiveInvoice=",
                                "receiveInvoiceItem=",
                                "resource=",
                                "separation=",
                                "sex=",
                                "species=",
                                "tags=",
                                "tagCategory=",
                                "therapeutic=",
                                "systemSetting",
                                "user=",
                                "vaccination=",
                                "webHookEvents=",
                                "webHooks=",
                                "help",
                                "debug",
                                "max=",
                                "pretty",
                            ]
                           )
    except getopt.GetoptError as err:
        # print help information and die:
        print(err)
        usage()
        sys.exit(2)

    try:
        args = sys.argv

        if len(opts) == 0 or any(i for i in ["-h", "--help"] if i in args):
            usage()
            sys.exit

        else:
            # Setup debugging
            if any (i for i in ["-v", "--verbose"] if i in args):
                logging.getLogger().setLevel(logging.INFO)
            elif any (i for i in ["-d", "--debug"] if i in args):
                logging.getLogger().setLevel(logging.DEBUG)

            # Setup max records returned
            max = 1                                             # Set to None or 1 (the library defaults to 1)
            for o, a in opts:                                   # First find out if we have to set maxpages
                if o in ["--max", "-m"]:
                    max = int(round(int(a))//10)                # round max records to nearest 10 then devide by to to get max pages

            logger.info("Limiting records to " + str(max))

            # Setup output formatting
            pretty = False
            if any (i for i in ["--pretty", "-p"] if i in args):                              # How do they want the output formatted
                pretty = True
                logger.info("Setting formatting to pretty")

            for o, a in opts:
                if not a:
                    a = "{}"                                    # if user provides an empty string as an argument, make it JSONable

                # skip options allready handled
                if o in (   "--debug",
                            "--verbose",
                            "-v",
                            "--pretty",
                            "--max",
                            "-d",
                            "-p",
                            "-m"):
                    pass

                elif o == "--address":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up animal with filter " +str(a) )
                    try:
                        data = e.getAddress(filter = json.loads(a), maxpages=max)
                        printFormatted(data, pretty)
                    except json.decoder.JSONDecodeError:
                        logger.error("The filter string supplied is invalid JSON, check the filter and try again.")

                elif o == "--animal":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up animal with filter " +str(a) )
                    data = e.getAnimal(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--animalColor":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up animal color with filter " +str(a) )
                    data = e.getAnimalColor(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--appointment":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up appointments with filter: " + str(a))
                    data = e.getAppointment(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--appointmentStatus":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Getting ezyvet status.")
                    data =  e.getApptStatus()
                    printFormatted(data, pretty)

                elif o == "--apptStatusLookup":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    data = lookupApptStatus(e,a)
                    printFormatted(data, pretty)

                elif o == "--appointmentType":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Getting ezyvet appointment status.")
                    data =  e.getApptType()
                    printFormatted(data, pretty)

                elif o == "--assessment":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up assessment with filter: " + str(a))
                    data = e.getAssessment(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--attachment":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up attachments with filter: " + str(a))
                    data = e.getAttachment(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--breed":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up breeds with filter: " + str(a))
                    data = e.getBreed(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--communaction":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up communications with filter: " + str(a))
                    data = e.getCommunication(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--consult":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up consults with filter: " + str(a))
                    data = e.getConsult(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--contact":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up contacts with filter: " + str(a))
                    data = e.getContact(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--contactDetail":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up contacts details with filter: " + str(a))
                    data = e.getContactDetail(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--contactDetailType":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up contact detail types")
                    data = e.getContactDetailType()
                    printFormatted(data, pretty)

                elif o == "--country":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up countries with filter: " + str(a))
                    data = e.getCountry(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--diagnostic":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up diagnostics with filter: " + str(a))
                    data = e.getDiagnostic(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--diagnosticResult":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up diagnostic results with filter: " + str(a))
                    data = e.getDiagnosticResult(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--diagnosticResultItem":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up diagnostic results item with filter: " + str(a))
                    data = e.getDiagnosticResultItem(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--diagnosticRequest":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up diagnostic requests with filter: " + str(a))
                    data = e.getDiagnosticRequest(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--diagnosticRequestItem":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up diagnostic request items with filter: " + str(a))
                    data = e.getDiagnosticRequestItems(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--getFile":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up files with filter: " + str(a))
                    data = e.getFile(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--getIntegratedDiagnostic":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up integrated diagnostics with filter: " + str(a))
                    data = e.getintegratedDiagnostic(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--healthStatus":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up health status with filter: " + str(a))
                    data = e.getHealthStatus(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--history":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up histories with filter: " + str(a))
                    data = e.getHistory(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--invoice":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up invoices with filter: " + str(a))
                    data = e.getInvoice(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--invoiceLine":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up invoice lines with filter: " + str(a))
                    data = e.getInvoiceLine(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--operation":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up operations with filter: " + str(a))
                    data = e.getOperation(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--payment":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up payments with filter: " + str(a))
                    data = e.getPayment(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--paymentMethod":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up payment menthods with filter: " + str(a))
                    data = e.getPaymentMethod(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--physicalExam":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up physical exams with filter: " + str(a))
                    data = e.getphysicalExam(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--plan":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up plans with filter: " + str(a))
                    data = e.getPlan(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--prescription":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up prescriptions with filter: " + str(a))
                    data = e.getPrescription(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--prescriptionItems":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up prescriptions items with filter: " + str(a))
                    data = e.getPrescriptionItems(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--presentingProblem":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up presenting problems with filter: " + str(a))
                    data = e.getPresentingProblem(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--presentingProblemLink":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up presenting problem links with filter: " + str(a))
                    data = e.getPresentingProblemLink(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--product":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up products with filter: " + str(a))
                    data = e.getProduct(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--productGroup":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up product groups with filter: " + str(a))
                    data = e.getProductGroup(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--purchaseOrder":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up Purchase Orders with filter: " + str(a))
                    data = e.getPurchaseOrder(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--purchaseOrderItem":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up Purchase Order Items with filter: " + str(a))
                    data = e.getPurchaseOrderItem(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--receiveInvoice":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up Receive Invoices with filter: " + str(a))
                    data = e.getReceiveInvoice(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--receiveInvoiceItem":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up Receive Invoice Items with filter: " + str(a))
                    data = e.getReceiveInvoiceItem(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--resource":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up resources with filter: " + str(a))
                    data = e.getResource(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--separation":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up separations with filter: " + str(a))
                    data = e.getSeparation(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--sex":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up sexes with filter: " + str(a))
                    data = e.getSex(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--species":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up species with filter: " + str(a))
                    data = e.getSpecies(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--tag":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up tags with filter: " + str(a))
                    data = e.getTag(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--tagCategory":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up tag categories with filter: " + str(a))
                    data = e.getTagCategory(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--therapeutic":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up therapeutics with filter: " + str(a))
                    data = e.getTherapeutic(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--systemSetting":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up system settings")
                    data = e.getSystemSetting()
                    printFormatted(data, pretty)

                elif o == "--user":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up users with filter: " + str(a))
                    data = e.getUser(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--vaccination":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up vaccinationd with filter: " + str(a))
                    data = e.getVaccination(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--webHookEvents":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up web hook events with filter: " + str(a))
                    data = e.getWebHookEvents(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "--webHooks":
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Looking up web hooks with filter: " + str(a))
                    data = e.getWebHooks(filter = json.loads(a), maxpages=max)
                    printFormatted(data, pretty)

                elif o == "-T":                                 # Test the connection to ezyvet
                    e = ezyvet.ezyvet(SETTINGS, logger)
                    logger.info("Testing connection to ezyVet API complete.")

                else:
                    msg = "Unknown option: " + pformat(o)
                    logger.error("ERROR: " + str(msg))
                    usage()
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
    s = """
    ezyVet CLI by DoveLewis
    © 2018 DoveLewis - All Rights Reserved
    Author: Avi Solomon - 2018 (asolomon@dovelewis.org)
    Version 0.2.0

    Usage:
        python3 ezyvet_cli.py [-v|-d][-p][-m <number>] [OPTION] <filter>

    Modifiers:
        -v                                      Verbose output
        -d, --debug                             Very verbose output
        -p, --pretty                            Human readable output
        -m, --max <number>                      Set the max records returned
                                                (rounded to nearest 10)
                                                DEFAULT 1
    Options:
        -h, --help                              Get Help (print this)
        --address <filter>                      Fetch Address(es)
        --animal <filter>                       Fetch Animal(s)
        --animalcolor <filter>                  Fetch Animal Color(s)
        --appointment <filter>                  Fetch Appointment(s)
        --appointmentStatus <filter>            Fetch appointment status(es)
        --appointmentStatusLookup <id or name>  Lookup appointment status by ID or name
        --appointmentType <filter>              Fetch appointment type(s)
        --assessment <filter>                   Fetch assessment(s)
        --attachment <filter>                   Fetch attachment(s)
        --breeds <filter>                       Fetch breed(s)
        --communication <filter>                Fetch communaction(s)
        --consult <filter>                      Fetch consult(s)
        --contact <filter>                      Fetch contact(s)
        --contactDetail <filter>                Fetch contact detial(s)
        --contactDetailType <filter>            Fetch contact detail type(s)
        --country <filter>                      Fetch country
        --diagnostic <filter>                   Fetch diagnostic(s)
        --diagnosticResult <filter>             Fetch diagnostic result(s)
        --diagnosticResultItem <filter>         Fetch diagnostic result item(s)
        --diagnosticRequest <filter>            Fetch diagnostic request(s)
        --diagnosticRequestItems <filter>       Fetch diagnostic request item(s)
        --file <filter>                         Fetch file(s)
        --integratedDiagnostic <filter>         Fetch integrated diagnostic(s)
        --healthStatus <filter>                 Fetch health status
        --history <filter>                      Fetch histories
        --invoice <filter>                      Fetch invoice(s)
        --invoiceLine <filter>                  Fetch invoice items(s)
        --operation <filter>                    Fetch operation(s)
        --payment <filter>                      Fetch payment(s)
        --paymentMethod <filter>                Fetch payment method(s)
        --physicalExam <filter>                 Fetch physical exams(s)
        --plan <filter>                         Fetch plan(s)
        --prescription <filter>                 Fetch perscription(s)
        --prescriptionItems <filter>            Fetch prescription item(s)
        --presentingProblem <filter>            Fetch presenting problem(s)
        --presentingProblemLink <filter>        Fetch presenting problem link(s) to consults
        --product <filter>                      Fetch product(s)
        --productGroup <filter>                 Fetch product group(s)
        --purchaseOrder <filter>                Fetch purchase order(s)
        --purchaseOrderItem <filter>            Fetch purchase order item(s)
        --receiveInvoice <filter>               Fetch receive invoice(s)
        --receiveInvoiceItem <filter>           Fetch receive invoice item(s)
        --resource <filter>                     Fetch resource(s)
        --separation <filter>                   Fetch separation(s)
        --sex <filter>                          Fetch sex(es)
        --species <filter>                      Fetch species
        --tags <filter>                         Fetch tag(s)
        --tagCategory <filter>                  Fetch tag category
        --therapeutic <filter>                  Fetch therapeutic(s)
        --systemSetting                         Fetch system settings
        --user <filter>                         Fetch user(s)
        --vaccination <filter>                  Fetch vaccination(s)
        --webHookEvents <filter>                Fetch webhook event(s)
        --webHooks                              Fetch webhooks

    Filters:
        Flters use standard JSON formatting.:
        '{"id":22}''

        Example:
        python3 ezyvet_cli.py -p --animal '{"id":64384}'
    """

    print(s)

def lookupApptStatus(e, lookup):
    """ Given a ezyvet instance, lookup a status code or ID
        Returns: Code name, ID or None
    """
    logger.info("Looking up status: " + str(lookup))
    code = e.lookupApptStatus(lookup)
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
