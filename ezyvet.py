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

import requests
from bs4 import BeautifulSoup
import json
from pprint import pprint,pformat
import re
import logging
import sys
from ezhelpers import writeJson, readJson

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

    fetchToken()
        Get a new token if we don't have one or if it is invalid

    getAptStatus()
        Get all available appointment statuses as an array

    getAptStatusCode(name, id)
        Given a name return the appointment status ID or None
        Given an ID, return the status name or None

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
        try:
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
        except:
            self.logger.error("ERROR: init Failed", exc_info=True)
            return None

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
            self.logger.error("ERROR: Initconnection Failed", exc_info=True)
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
            self.logger.error("ERROR: Token var does not have a token in it.", exc_info=True)
            sys.exit(0)
        except NameError:
            self.logger.error("ERROR: Token did not work.", exc_info=True)
            return None
        except:
            self.logger.error("ERROR: Token did not work or something else went wrong.", exc_info=True)
            return None

    def fetchToken(self):
        """ Get a fresh access token from the API, this must be done every 14 days"""
        try:
            # TODO: add scope to settings file
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

    def getAptStatus(self):
        """ Return an array of appointment statuses
            or None for failure.
        """
        try:
            self.logger.debug("Token: " + self.token["access_token"])
            headers = {
                "authorization": "Bearer " + self.token["access_token"],
                'Cache-Control': "no-cache"
            }

            r = requests.request("GET", self.url + "/appointmentstatus", headers=headers)
            self.logger.debug("Get appoint status response: " + str(r.content))
            if r.status_code != 200:
                self.logger.error("Unable to retreive appointment statuses, received " + r.content)
                return None
            status_data = json.loads(r.text)
            self.logger.debug("Got status data " + r.text)
            if "meta" not in status_data or "items" not in status_data:
                self.logger.error("Error: meta or items not in status data.")
                return None

            statuses = []
            for s in status_data["items"]:
                statuses.append(s)
            pages = int(status_data["meta"]["items_page_total"])
            i = 1

            while pages > i:
                i += 1
                r = requests.request("GET", self.url + "/appointmentstatus?page="+str(i), headers=headers)
                if r.status_code != 200:
                    self.logger.error("ERROR: Unable to retreive appointment statuses, received " + str(r.status_code))
                new_data = json.loads(r.text)
                self.logger.debug("Got status data " + r.text)
                if "meta" not in status_data or "items" not in status_data:
                    self.logger.error("Error: meta or items not in status data.")
                    return None
                for s in new_data["items"]:
                    statuses.append(s)

            return statuses

        except TypeError:
            self.logger.error("ERROR: Something went wrong", exc_info=True)
            sys.exit(0)

        except:
            self.logger.error("ERROR: something else went wrong.", exc_info=True)
            return None

    def getAptStatusCode(self, name=None, id=None):
        """ Given a name return the ID or None of the appointment status
            Given a ID return the name or None
        """
        try:
            codes = self.getAptStatus()
            self.logger.debug("Got codes: " + pformat(codes))
            if codes is None:
                self.logger.error("ERROR: Could not retreive list of appointment status.")
                return None
            if name is not None:
                self.logger.info("Looking up " + str(name) + " in appointment statuses.")
                for s in codes:
                    self.logger.debug("Examining status " + s["appointmentstatus"]["name"] + " [" + str(s["appointmentstatus"]["id"] +"]"))
                    if s["appointmentstatus"]["name"] == name:
                        return s["appointmentstatus"]["id"]
                return None
            elif id is not None:
                self.logger.info("Looking up " + str(id) + " in appointment statuses.")
                for s in codes:
                    self.logger.debug("Examining status " + s["appointmentstatus"]["name"] + " [" + str(s["appointmentstatus"]["id"] +"]"))
                    if int(s["appointmentstatus"]["id"]) == id:
                        return s["appointmentstatus"]["name"]
                return None
            else:
                self.logger.error("You must suppily a name or id of code to lookup")
                return None

        except:
            self.logger.error("ERROR: getAptStatusCode - something went wrong.", exc_info=True)
            return None
