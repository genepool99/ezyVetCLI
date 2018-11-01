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

import json
import logging
import sys
import os

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# A collection of generic helper functions for use in this project

def writeJson(data, filename):
    """Given a filename (path) write json to file. """
    try:
        if os.path.isabs(filename):                             # check if it is an absolute path
            if not os.path.exists(os.path.dirname(filename)):   # check if the directory portion of the path exists
                os.mkdir(os.path.dirname(filename))             # create it
        with open(filename, 'w') as outfile:
            json.dump(data, outfile)
    except OSError:
        logger.error("ERROR: Could not write to " + self.home_dir + " check the path and permissions and try again.")
    except:
        logger.error("Write JSON Failed", exc_info=True)

def readJson(filename):
    """ Given a filename, read file as json"""
    try:
        with open(filename) as f:
            data = json.load(f)
        return data
    except ValueError as e:
        logger.error("ERROR: Error reading JSON file.")
    except:
        logger.error("Read JSON Failed", exc_info=True)
