#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json
from pprint import pprint,pformat
import re
import logging
import sys

class ezyvet:
    """
    Common base class for all ezyvet sessions

    ...

    Attributes
    ----------
    settings : static settings
        Data from the settings file
    logger : the logger session
        It makes more consistant logs to pass a logger session to the class
    sandbox : Bool, optional
        Are we going to use the sandbox or production API

    Methods
    -------
    initConnection()
        Connect to the ezyVet API, get token if you don't have one.

    testToken()
        If we have a stored token, test it.
    """

    def __init__(self, settings, logger, sandbox=False):
        """
        Parameters
        ----------
        settings : static settings
            Data from the settings file
        logger : the logger session
            It makes more consistant logs to pass a logger session to the class
        sandbox : Bool, optional
            Are we going to use the sandbox or production API
        """
        self.logger = logger or logging.getLogger(__name__)
        self.settings = settings
        if sandbox is False:
            self.url = settings["PROD_URL"]
            self.partner_id = self.settings['PARTNER_ID'],
            self.client_id = self.settings['CLIENT_ID'],
            self.client_secret = self.settings['CLIENT_SECRET'],
        else:
            self.url = settings["SAND_URL"]
            self.partner_id = self.settings['PARTNER_ID'],
            self.client_id = self.settings['CLIENT_ID_SAND'],
            self.client_secret = self.settings['CLIENT_SECRET_SAND'],
        self.initConnection()

    def initConnection(self):
        try:
            self.s = requests.session()
            for attempt in range(1):
                try:
                    self.logger.info("INFO: Reading stored access token.")
                    self.token = readJson("token.json")         # lets see if we have a stored token
                    if self.token is None:
                        self.logger.info("INFO: No stored token, fetching new one.")
                        self.token = self.fetchToken()

                    self.logger.info("INFO: Testing token.")
                    if self.testToken() is not 200:                # Lets test the Token
                        self.logger.info("INFO: Test Failed, refreshing token.")
                        self.token = self.fetchToken()
                        self.logger.info("INFO: Re-testing token.")
                        if self.testToken() is not 200:
                            self.logger.error("ERROR: Refreshing token did not work, quiting.")
                            sys.exit(2)

                    self.logger.info("Init Complete.")

                except requests.exceptions.ReadTimeout:
                    self.logger.error("ERROR: initConnection(self): exceptions.ReadTimeout, trying re-init.", exc_info=True)
                    time.sleep(60)
                    continue
                break

        except:
            self.logger.error("ERROR: init Failed", exc_info=True)
            return None

    def testToken(self):
        """ Test the token stored in self.token
            Returns a status code
        """
        if self.token is None or 'access_token' not in self.token:
            self.logger("Token sent for testing was missing")
            return None
        try:
            self.logger.debug("Token: " + self.token["access_token"])
            headers = {
                "authorization": "Bearer " + self.token["access_token"],
                'Cache-Control': "no-cache"
            }
            # Get some trivial data to test the token id=1 is the address of
            # ezyVet in Auckland
            r = requests.request("GET", self.url + "/address?id=1", headers=headers)
            self.logger.debug("Token testing response: " + str(r.content))
            return r.status_code

        except TypeError:
            self.logger.info("ERROR: Token var does not have a token in it.", exc_info=True)
            sys.exit(0)
        except NameError:
            self.logger.info("INFO: Token did not work.", exc_info=True)
            return None
        except:
            self.logger.info("INFO: Token did not work or something else went wrong.", exc_info=True)
            return None

    def fetchToken(self):
        """ Get a fresh access token from the API, this must be done every 14 days"""
        try:
            payload = {
                "partner_id": self.partner_id,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
                "scope":"read-address,read-animal,read-animalcolour,read-appointment,read-appointmentstatus,read-appointmenttype,read-assessment,read-attachment,read-breed,read-consult,read-contact,read-contactdetail,read-contactdetailtype,read-country,read-diagnostic,read-diagnosticrequest,read-diagnosticresult,read-diagnosticresultitem,read-healthstatus,read-history,read-integrateddiagnostic,read-invoice,read-invoiceline,read-operation,read-payment,read-paymentallocation,read-paymentmethod,read-physicalexam,read-plan,read-prescription,read-prescriptionitem,read-presentingproblem,read-presentingproblemlink,read-product,read-productgroup,read-purchaseorder,read-purchaseorderitem,read-receiveinvoice,read-receiveinvoiceitem,read-resource,read-separation,read-sex,read-species,read-systemsetting,read-tag,read-tagcategory,read-therapeutic,read-user,read-vaccination"
            }

            headers = {
                'Content-Type': "application/x-www-form-urlencoded",
                'cache-control': "no-cache"
            }
            url = self.url + "/oauth/access_token"
            self.logger.info("API URL: " + url)
            r = requests.request("POST", url, data=payload, headers=headers)
            self.logger.info(r.text)
            response = r.json()
            if "access_token" not in response:
                self.logger.error("ERROR: We got a message not an access token")
                self.logger.error(pformat(token))
                writeJson(response, "err.json")
                sys.exit(2)
            writeJson(response, "token.json")
            self.logger.info("Got access token: " + response["access_token"])
            return response

        except requests.exceptions.ConnectionError:
            self.logger.error("ERROR: fetchToken - Connection error", exc_info=True)
            return None
        except requests.exceptions.Timeout:
            self.logger.error("ERROR: fetchToken - Timeout updating...", exc_info=True)
            return None
        except:
            self.logger.error("fetchToken Failed", exc_info=True)
            return None

def writeJson(data, filename):
    """Given a filename (path) write json to file. """
    try:
        with open(filename, 'w') as outfile:
            json.dump(data, outfile)
    except:
        self.logger.error("Write JSON Failed", exc_info=True)

def readJson(filename):
    """ Given a filename, read file as json"""
    try:
        with open(filename) as f:
            data = json.load(f)
        return data
    except:
        return None
