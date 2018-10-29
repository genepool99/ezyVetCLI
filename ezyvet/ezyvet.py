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

import requests
from bs4 import BeautifulSoup
import json
from pprint import pprint,pformat
import re
import logging
import sys
import os
from urllib.parse import urlencode
from ezyvet.ezhelpers import writeJson, readJson


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

    getAppointment(self, filters=None, maxpages=1)
        Get an array of appointments optionally filtered. Pages contain up to 10 records.

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
            self.scope = ','.join(settings['SCOPE'])    # make the list into a comma seperated string
            self.logger.debug("Scope: " + str(self.scope))
            self.home_dir = str(self.settings['HOME_DIR'])
            if self.home_dir[-1:] is not "/" or self.home_dir[-1:] is not "\\":
                if '\\' in self.home_dir:
                    self.home_dir = self.home_dir + '\\'     # for windows users
                else:
                    self.home_dir = self.home_dir + '/'
            self.logger.info("Using working directory: " + self.home_dir)

            if self.partner_id == '' or self.client_id == '' or self.client_secret == '' or self.scope == '':
                self.logger.error("The settings file is incomplete. Make sure the partner id, client id, secret and scope are filled in.")
                sys.exit(2)

            self.initConnection()
        except:
            self.logger.error("ERROR: init Failed", exc_info=True)

    def initConnection(self):
        try:
            self.s = requests.session()
            for attempt in range(1):                             # number to make repeated attempts to init
                try:
                    self.logger.info("Reading stored access token.")
                    self.token = readJson(self.home_dir + "token.json")         # lets see if we have a stored token
                    if self.token is None:
                        self.logger.info("No stored token, fetching new one.")
                        self.token = self.fetchToken()

                    self.logger.info("Testing token.")
                    if self.testToken() is not 200:                # Lets test the Token
                        self.logger.info("Test Failed, refreshing token.")
                        self.token = self.fetchToken()
                        self.logger.info("Re-testing token.")
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

    def testToken(self):
        """ Test the token stored in self.token
            Returns a status code
        """
        if self.token is None or 'access_token' not in self.token:
            self.logger.info("Token sent for testing was missing")
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
        except:
            self.logger.error("ERROR: Token did not work or something else went wrong.", exc_info=True)

    def fetchToken(self):
        """ Get a fresh access token from the API"""
        try:
            payload = {
                "partner_id": self.partner_id,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
                "scope":self.scope
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
                self.logger.error(pformat(response))
                writeJson(response, self.home_dir + "err.json")
                self.logger.info("Wrote error to " + self.home_dir + "err.json")
                sys.exit(2)

            writeJson(response, self.home_dir + "token.json")
            self.logger.info("Got access token: " + response["access_token"])
            self.logger.info("Wrote token to " + self.home_dir + "err.json")
            return response

        except requests.exceptions.ConnectionError:
            self.logger.error("ERROR: fetchToken - Connection error", exc_info=True)
        except requests.exceptions.Timeout:
            self.logger.error("ERROR: fetchToken - Timeout updating...", exc_info=True)
        except:
            self.logger.error("fetchToken Failed", exc_info=True)

    def getData(self, url, filter=None, maxpages=1):
        """ Helper function to get data from all pages and return it
            to the caller as JSON. This helps prevent duplicate core
            get functions. This function is somewhat specific to how the
            ezyVet API functions, so it is kept in the core class. This functions
            strips out any of the meta data, so if you want that don't use this.
            Arguments:
                url = The endpoint ex. '/appointment'
                filter = None or a dictonary for query parameters
                maxpages = max number of records to return (page=10 records, default 1)
            Returns JSON data or None
        """
        try:
            self.logger.debug("Base url: " + str(url))
            if filter is not None:
                self.logger.info("Got filter: " + pformat(filter))
                qs = urlencode(filter)
                self.logger.info("Adding querystring to URL: " + qs)
                url += "?" + str(qs)
            self.logger.debug("url with query: " + str(url))

            headers = {
                "authorization": "Bearer " + self.token["access_token"],
                'Cache-Control': "no-cache"
            }

            ''' The while below is a little weird. Because we don't know how many pages
                of data we will get until we make our first call to the endpoint.
                To deal with it, we have a loop that determins at the end if it
                should break.
            '''
            i = 1               # current page counter
            pages = 0           # total pages
            items = []          # array of items we will return
            while True:
                if i > 1:       # this is not our first page
                    if '?' in url:
                        url += str('&page=' + str(i))
                    else:
                        url += str('?page=' + str(i))

                r = requests.request("GET", self.url + str(url), headers=headers)
                self.logger.debug("GetData Response: " + str(r.content))
                if r.status_code != 200:
                    self.logger.error("ERROR: getData - Unable to retreive data, received " + r.content)
                    return None

                data = json.loads(r.text)
                self.logger.debug("Got data " + r.text)

                if "meta" not in data or "items" not in data:
                    self.logger.error("ERROR: getData - meta or items not in data.")
                    return None

                for d in data["items"]:
                    items.append(d)

                pages = int(data["meta"]["items_page_total"])
                if pages <= 1 or i == pages or i==maxpages:            # if it is the last or only page break the loop
                    break
                i += 1

            return items

        except:
            self.logger.error("ERROR: getData - something went wrong.", exc_info=True)

    def getAptStatus(self):
        """ Return an array of appointment statuses
            or None for failure.
        """
        try:
            return self.getData("/appointmentstatus")

        except:
            self.logger.error("ERROR: something else went wrong.", exc_info=True)

    def getAptStatusCode(self, lookup):
        """ Given a name return the ID or None of the appointment status
            Given a ID return the name or None
        """

        try:
            if lookup is None:
                self.logger.error("You must suppily a name or id of code to look it up.")
            name = id = None
            try:
                id = int(lookup)                 # let's see if it is a name or ID lookup by testing id
                self.logger.debug("Looking up status code: " + str(lookup))
                id = lookup
            except ValueError:                  # Lookup by name not ID
                self.logger.info("Looking up status string: " + str(lookup))
                name = lookup

            codes = self.getAptStatus()         # get a fresh list of codes TODO: This coud be chached
            if codes is None:
                self.logger.error("ERROR: Could not retreive list of appointment status types.")
                return None
            self.logger.debug("Got codes: " + pformat(codes))

            for s in codes:
                self.logger.debug("Examining status " + s["appointmentstatus"]["name"] + " [" + str(s["appointmentstatus"]["id"] +"]"))
                if name is not None:
                    value = s["appointmentstatus"]["name"]
                    key = name
                    rvalue = s["appointmentstatus"]["id"]
                else:
                    value = s["appointmentstatus"]["id"]
                    key = id
                    rvalue = s["appointmentstatus"]["name"]
                if key == value:
                    return rvalue

        except:
            self.logger.error("ERROR: getAptStatusCode - something went wrong.", exc_info=True)

    def getAppointment(self, filter=None, maxpages=1):
        """ Get appointments given various filters.
            Arguments:
                filter: a dictonary of filters. Here is a example:
                filters = {
                    'id': 23,
                    'active': True,
                    'created_at': 1498690800,
                    ...
                }
            Returns: an array of appointments
        """
        try:
            # Build the query string
            url = "/appointment"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data

        except:
            self.logger.error("ERROR: getAppointment - something went wrong.", exc_info=True)

    def getCommunication(self, filter=None, maxpages=1):
        """Get communications given various filters.
            Arguments:
                filter: a dictonary of filters.
                maxpages: limits the total number of records returned (1 page = 10 records)

            Returns: an array of communications

            Note: This function requires the read-communication scope which is
            not currently available to me, so I cannot test.
        """
        try:
            # Build the query string
            url = "/communication"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data

        except:
            self.logger.error("ERROR: getCommunications - something went wrong.", exc_info=True)

    def getConsult(self, filter=None, maxpages=1):
        """Get consult data given various filters.
            Arguments:
                filter: a dictonary of filters.
                maxpages: limits the total number of records returned (1 page = 10 records)

            Returns: an array of consult data
        """
        try:
            # Build the query string
            url = "/consult"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data

        except:
            self.logger.error("ERROR: getConsult - something went wrong.", exc_info=True)
