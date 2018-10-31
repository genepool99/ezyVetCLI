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

    TOTO: Finish Methods Doc

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
        """
            Initializes the connection to ezyVet using a new or stored access token.
            If the first test fails, the token has probabily gone bad, so we refresh
            and retry. Two failures stops the program.
        """
        try:
            self.s = requests.session()
            for attempt in range(1):                                            # number to make repeated attempts to init
                try:
                    self.logger.info("Reading stored access token.")
                    self.token = readJson(self.home_dir + "token.json")         # lets see if we have a stored token
                    if self.token is None:
                        self.logger.info("No stored token, fetching new one.")
                        self.token = self.fetchToken()

                    self.logger.info("Testing token.")
                    if self.testToken() is not 200:                             # Lets test the Token
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
            Parameters
            ----------

            Returns
            -------
            int
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
            self.logger.error("ERROR: Token did not work something went wrong.", exc_info=True)

    def fetchToken(self):
        """
        Get a fresh access token from the API. If sucessful write it to file
        and store it in self.token.
        Parameters
        ----------

        Returns
        -------
        int
            Response code from the API
        """
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
            Parameters
            ----------
            url : string
                URL of the API endpoint
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
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

                r = requests.request("GET", str(self.url) + str(url), headers=headers)
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

    def getAddress(self, filter=None, maxpages=1):
        """ Get addresses(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#address

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/address"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getAddress - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getAddress - something went wrong.", exc_info=True)

    def getAnimal(self, filter=None, maxpages=1):
        """ Get animal(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#animal

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/animal"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getAnimal - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getAnimal - something went wrong.", exc_info=True)

    def getAnimalColor(self, filter=None, maxpages=1):
        """ Get animal color(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#animalcolour

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/animalcolor"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getAnimalColor - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getAnimalColor - something went wrong.", exc_info=True)

    def getAppointment(self, filter=None, maxpages=1):
        """ Get appointment(s) given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#appointment

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/appointment"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getAppointment - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getAppointment - something went wrong.", exc_info=True)

    def getApptStatus(self):
        """ Get all of the appointment status codes.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#appointmentstatus

        Parameters
        ----------

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            return self.getData("/appointmentstatus",maxpages=10)               # TODO: I hardcoded maxpages=10, I don't think it needs that many.

        except:
            self.logger.error("ERROR: getApptStatus went wrong.", exc_info=True)

    def getApptType(self):
        """ Get all of the appointment type codes.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#appointmenttype

        Parameters
        ----------

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            return self.getData("/appointmenttype",maxpages=10)                 # TODO: I hardcoded maxpages=10, I don't think it needs that many.

        except:
            self.logger.error("ERROR: getApptType went wrong.", exc_info=True)

    def getAssessment(self, filter=None, maxpages=1):
        """ Get assessment(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#assessment

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/assessment"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data

        except TypeError:
            self.logger.error("ERROR: getAssessment - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getAssessment - something went wrong.", exc_info=True)

    def getAttachment(self, filter=None, maxpages=1):
        """ Get attachment(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#attachment

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/attachment"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data

        except TypeError:
            self.logger.error("ERROR: getAttachment - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getAttachment - something went wrong.", exc_info=True)

    def getBreed(self, filter=None, maxpages=1):
        """ Get breed(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#breed

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/breed"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data

        except TypeError:
            self.logger.error("ERROR: getBreed - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getBreed - something went wrong.", exc_info=True)

    def getCommunication(self, filter=None, maxpages=1):
        """ Get communication(s) given filters. Note: This function
            requires the read-communication scope, which is not currently available
            to me. Sadly, I cannot test.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#communication

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.

        """
        try:
            url = "/communication"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getCommunication - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getCommunications - something went wrong.", exc_info=True)

    def getConsult(self, filter=None, maxpages=1):
        """ Get consult(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#consult

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/consult"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data

        except TypeError:
            self.logger.error("ERROR: getConsult - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getConsult - something went wrong.", exc_info=True)

    def getContact(self, filter=None, maxpages=1):
        """ Get contact(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#contact

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/contact"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getContact - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getConsult - something went wrong.", exc_info=True)

    def getContactDetail(self, filter=None, maxpages=1):
        """ Get contact detail(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#contactdetail

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/contactdetail"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getContactDetail - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getContactDetail - something went wrong.", exc_info=True)

    def getContactDetailType(self):
        """ Get all of the contact detail types contact method, such as “Mobile” or “Email”.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#contactdetailtype

        Parameters
        ----------

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            return self.getData("/contactdetailtype",maxpages=10)               # TODO: I hardcoded maxpages=10, I don't think it needs that many.

        except:
            self.logger.error("ERROR: getContactDetailType something went wrong.", exc_info=True)

    def getCountry(self, filter=None, maxpages=1):
        """ Get country(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#country

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/country"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getCountry - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getCountry - something went wrong.", exc_info=True)

    def getDiagnostic(self, filter=None, maxpages=1):
        """ Get diagnostic(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#diagnostic

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/diagnostic"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getDiagnostic - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getDiagnostic - something went wrong.", exc_info=True)

    def getDiagnosticResult(self, filter=None, maxpages=1):
        """ Get diagnostic result(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#diagnosticresult

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/diagnosticresult"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getDiagnosticResult - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getDiagnosticResult - something went wrong.", exc_info=True)

    def getDiagnosticResultItem(self, filter=None, maxpages=1):
        """ Get diagnostic result items(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#diagnosticresultitem

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/diagnosticresultitem"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getDiagnosticResultItem - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getDiagnosticResultItem - something went wrong.", exc_info=True)

    def getDiagnosticRequest(self, filter=None, maxpages=1):
        """ Get diagnostic request(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#diagnosticrequest

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/diagnosticrequest"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getDiagnosticRequst - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getDiagnosticRequst - something went wrong.", exc_info=True)

    def getDiagnosticRequstItem(self, filter=None, maxpages=1):
        """ Get diagnostic request item(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#diagnosticrequestitem

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/diagnosticrequestitem"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getDiagnosticRequstItem - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getDiagnosticRequstItem - something went wrong.", exc_info=True)

    def getFile(self, filter=None, maxpages=1):
        """ Get files(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#fetch-a-file

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/file"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getFile - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getFile - something went wrong.", exc_info=True)

    def getIntegratedDiagnostic(self, filter=None, maxpages=1):
        """ Get integrated partner diagnostic(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#integrateddiagnostic

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/integrateddiagnostic"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getIntegratedDiagnostic - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getIntegratedDiagnostic - something went wrong.", exc_info=True)

    def getHealthStatus(self, filter=None, maxpages=1):
        """ Get health status metrics(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#healthstatus

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/healthstatus"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getHealthStatus - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getHealthStatus - something went wrong.", exc_info=True)

    def getHistory(self, filter=None, maxpages=1):
        """ Get history result(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#history

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/history"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getHistory - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getHistory - something went wrong.", exc_info=True)

    def getInvoice(self, filter=None, maxpages=1):
        """ Get invoice(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#invoice

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/invoice"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getInvoice - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getInvoice - something went wrong.", exc_info=True)

    def getInvoiceLine(self, filter=None, maxpages=1):
        """ Get invoice lines(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#invoiceline

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/invoiceline"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getInvoiceLine - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getInvoiceLine - something went wrong.", exc_info=True)

    def getOperation(self, filter=None, maxpages=1):
        """ Get operation(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#operation

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/operation"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getOperation - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getOperation - something went wrong.", exc_info=True)

    def getPayment(self, filter=None, maxpages=1):
        """ Get payment(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#payment

            Parameters
            ----------
            filter : dictonary
                A dictionary of filter arguments to be used in the querystring.
            maxpages : int
                The maximum number of pages to return. Each page has up to 10 records.

            Returns
            -------
            array or None
                The "items" data  in an array of dictionaries.
        """
        try:
            url = "/payment"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getPayment - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getPayment - something went wrong.", exc_info=True)

    def getPaymentMethod(self, filter=None, maxpages=1):
        """ Get payment method(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#paymentmethod

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/paymentmethods"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getPaymentMethod - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getPaymentMethod - something went wrong.", exc_info=True)

    def getPhysicalExam(self, filter=None, maxpages=1):
        """ Get physical exam(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#physicalexam

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/physicalexam"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getPhysicalExam - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getPhysicalExam - something went wrong.", exc_info=True)

    def getPlan(self, filter=None, maxpages=1):
        """ Get paln(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#plan

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/plan"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getPlan - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getPlan - something went wrong.", exc_info=True)

    def getPrescription(self, filter=None, maxpages=1):
        """ Get prescription(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#prescription

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/prescription"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getPrescription - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getPrescription - something went wrong.", exc_info=True)

    def getPrescriptionItem(self, filter=None, maxpages=1):
        """ Get prescription item(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#prescriptionitem

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/prescriptionitem"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getPrescriptionItem - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getPrescriptionItem something went wrong.", exc_info=True)

    def getPresentingProblem(self, filter=None, maxpages=1):
        """ Get presenting problem(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#presentingproblem

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/presentingproblem"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getPresentingProblem - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getPresentingProblem - something went wrong.", exc_info=True)

    def getPresentingProblemLink(self, filter=None, maxpages=1):
        """ Get presenting problem link(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#presentingproblemlink

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/presentingproblemlink"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getPresentingProblemLink - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getPresentingProblemLink - something went wrong.", exc_info=True)

    def getProduct(self, filter=None, maxpages=1):
        """ Get product(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#product

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/product"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getProduct - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getProduct - something went wrong.", exc_info=True)

    def getProductGroup(self, filter=None, maxpages=1):
        """ Get product groups(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#productgroup

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/productgroup"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getProductGroup - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getProductGroup - something went wrong.", exc_info=True)

    def getPurchaseOrder(self, filter=None, maxpages=1):
        """ Get purchase order(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#purchaseorder

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/purchaseorder"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getPurchaseOrder - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getPurchaseOrder - something went wrong.", exc_info=True)

    def getPurchaseOrderItem(self, filter=None, maxpages=1):
        """ Get purchase order items(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#purchaseorderitem

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/purchaseorderitem"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getPurchaseOrderItem - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getPurchaseOrderItem - something went wrong.", exc_info=True)

    def getReceiveInvoice(self, filter=None, maxpages=1):
        """ Get receive invoice(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#receiveinvoice

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/receiveinvoice"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getReceiveInvoice - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getReceiveInvoice something went wrong.", exc_info=True)

    def getReceiveInvoiceItem(self, filter=None, maxpages=1):
        """ Get receive invoice items(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#receiveinvoiceitem

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/receiveinvoiceitem"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getReceiveInvoiceItem - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getReceiveInvoiceItem - something went wrong.", exc_info=True)

    def getResource(self, filter=None, maxpages=1):
        """ Get resource(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#resource

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/resource"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getResource - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getResource - something went wrong.", exc_info=True)

    def getSeparation(self, filter=None, maxpages=1):
        """ Get separation(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#separation

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/separation"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getSeparation - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getSeparation - something went wrong.", exc_info=True)

    def getSex(self, filter=None, maxpages=1):
        """ Get sex(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#sex

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/sex"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getSex - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getSex -  something went wrong.", exc_info=True)

    def getSpecies(self, filter=None, maxpages=1):
        """ Get species(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#species

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/species"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getSpecies - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getSpecies -  something went wrong.", exc_info=True)

    def getTag(self, filter=None, maxpages=1):
        """ Get tag(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#tag

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/tag"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getTag - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getTag -  something went wrong.", exc_info=True)

    def getTagCategory(self, filter=None, maxpages=1):
        """ Get tag category(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#tagcategory

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/tagcategory"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getTagCategory - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getTagCategory -  something went wrong.", exc_info=True)

    def getTherapeutic(self, filter=None, maxpages=1):
        """ Get therapeutic(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#therapeutic

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/therapeutic"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getTherapeutic - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getTherapeutic -  something went wrong.", exc_info=True)

    def getSystemSetting(self):
        """ Get systemsetting data.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#systemsetting

        Parameters
        ----------

        Returns
        -------
        array or None
            The "items" data in an array of dictionaries or None for failure.
        """
        try:
            url = "/systemsetting"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getSystemSetting - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getSystemSetting -  something went wrong.", exc_info=True)

    def getUser(self, filter=None, maxpages=1):
        """ Get user(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#user

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/user"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getUser - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getUser -  something went wrong.", exc_info=True)

    def getVaccination(self, filter=None, maxpages=1):
        """ Get user(s) data given filters.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#vaccination

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/vaccination"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getVaccination - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getVaccination -  something went wrong.", exc_info=True)

    def getWebHookEvents(self):
        """ Get wehooks(s) events list.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#webhookevents

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/webhookevents"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getWebHookEvents - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getWebHookEvents -  something went wrong.", exc_info=True)

    def getWebHooks(self):
        """ Get webhooks(s) list.
            See: https://apisandbox.trial.ezyvet.com/api/docs/#webhooks

        Parameters
        ----------
        filter : dictonary
            A dictionary of filter arguments to be used in the querystring.
        maxpages : int
            The maximum number of pages to return. Each page has up to 10 records.

        Returns
        -------
        array or None
            The "items" data  in an array of dictionaries or None for failure.
        """
        try:
            url = "/webhooks"
            data = self.getData(url,filter=filter,maxpages=maxpages)
            self.logger.info("Returned " + str(len(data)) + " records.")
            return data
        except TypeError:
            self.logger.error("ERROR: getWebHooks - something went wrong, getData returned None.", exc_info=True)
        except:
            self.logger.error("ERROR: getWebHooks -  something went wrong.", exc_info=True)

    def lookupApptStatus(self, lookup):
        """ Lookup a status code or names.
            This is a helper function and has no reference in the API.

            Parameters
            ----------
            lookup : int or string
                What to lookup, could be an ID or name of a status

            Returns
            -------
            int or string or None
                Given an ID, it will return the status code name. Given a name,
                it will return the ID.
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

            codes = self.getApptStatus()         # get a fresh list of codes TODO: This coud be chached
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
                    if name is None:
                        return {"name":rvalue}
                    else:
                        return {"id":rvalue}

        except:
            self.logger.error("ERROR: lookupApptStatus - something went wrong.", exc_info=True)
