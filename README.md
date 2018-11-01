# ezyVetCli

A command line interface and Python library for ezyVet API v1
(https://www.ezyvet.com/).

## License
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

## ezyVet API agreement
To use this application, you will need to register and receive an API key.  
The application can be found https://www.ezyvet.com/api-signup

## Contributing
This is an open source project and we hope you contribute. For more Information
about the ezyVet API, which this application is built upon, see
https://apisandbox.trial.ezyvet.com/api/docs/.

## Requirements
This program has been tested under Ubuntu Linux 16.10 and 18.10. It should
run under POSIX compatable OS that can run Python 3.5+ but it has not been
tested.

## Setup
Copy `setting_Example.py` as `settings.py` and fill in your credential details.
This file is should not be under source control and should be explicitly ignored.

### Clone the production branch which will always be stable.
Git: https://gitlab.com/genepool99/ezyvetcli  
`git clone -b production git@gitlab.com:genepool99/ezyvetcli.git`  

### Install venv on the system if you have not already
Using PIP:
`sudo pip install --upgrade virtualenv`  
or  
Using APT:
`sudo apt-get install python3-venv`  

### CD into the project directory and create a new virtualenv
`python3 -m venv venv`

### Activate the virtualenv using a bash shell (does not work with fish or csh)
`source venv/bin/activate`
You should now have a prompt that looks something like:
(venv) user@computer:~/home/user/ezyvetcli$

### Install the dependencies
In the base ezyvetcli directory run
`pip install -r requirements.txt`  

### Test your environment
`python3 ezyvet_cli.py --debug -T`
There will be a verbose output, but you should see no "ERROR:" messages and ending with:  
"INFO:__main__:Init Complete."

### When your done leave the virtual env with
`deactivate`  

## Coding Standards and Development
Python3 (3.5.2+)  
PEP 8 (https://www.python.org/dev/peps/pep-0008/)

### Directory structure
-ezyvetcli    <- root directory
  -venv       <- the virtual environment
  -ezyvet     <- the ezyvet library

### Saving dependencies
After adding or upgrading modules you must run `pip freeze > requirements.txt` and commit the requirments.txt.

### Contributing
Submit a pull request.

## Using the CLI

### Examples
To test your credentials and setup with verbose output:
`python3 ezyvet_cli -v -T`

Get help using the program:
`python3 ezyvet_cli.py --help`

Get the list of appointment status codes:
`python3 ezyvet_cli.py -s`

To get the first page of active records for hospitalized patients (assuming "In Hospital" is code 9):
`python3 ezyvet_cli.py -a '{"active":"true", "appointment_status_id":9}'`

### Building more complex filters
To build complex filters, see https://apisandbox.trial.ezyvet.com/api/docs form
a listing of query parameters.
