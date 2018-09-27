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

    def __init__(self, settings, logger, sandbox=None):
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
        if sandbox is not None:
            self.url = settings["PROD_URL"]
        else:
            self.url = settings["SAND_URL"]
        self.initConnection()

    def initConnection(self):
        try:
            self.s = requests.session()
            for attempt in range(20):
                try:
                    # lets see if we have a stored token
                    self.token = readJson("token.json")
                    if self.token is None:
                        self.token = self.fetchToken()
                    # Lets test the Token
                        if self.testToken() is None:
                            self.logger.info("Token not working, retry.")
                            self.token = self.fetchToken()
                            if self.testToken() is None:
                                self.logger.error("ERROR: Refreshing token did not work, quiting.")
                                sys.exit(2)

                except requests.exceptions.ReadTimeout:
                    self.logger.error("ERROR: initConnection(self): exceptions.ReadTimeout, trying re-init.", exc_info=True)
                    time.sleep(60)
                    continue
                break

        except:
            self.logger.error("ERROR: init Failed", exc_info=True)
            return None

    def testToken(self):
        """ Test the token stored in self.token """
        try:
            headers = {
                "authorization": "Bearer " + self.token["access_token"],
                'Cache-Control': "no-cache"
            }
            # Get some trivial data to test the token
            r = requests.request("POST", self.url + "/address?country_id=153", headers=headers)
            return r.content
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
                "partner_id": self.settings['PARTNER_ID'],
                "client_id": self.settings['CLIENT_ID'],
                "client_secret": self.settings['CLIENT_SECRET'],
                "grant_type": "client_credentials",
                "scope":"read-address"
            }
            headers = {
                'Content-Type': "application/x-www-form-urlencoded",
                'Cache-Control': "no-cache"
            }
            r = requests.request("POST", self.url + "/oauth/access_token", json=payload, headers=headers)
            token = r.json()
            if "access_token" not in token:
                self.logger.error("ERROR: We got a message not an access token")
                self.logger.error(pformat(token))
                writeJson(token, "err.json")
                sys.exit(2)
            writeJson(token, "token.json")
            return token

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
