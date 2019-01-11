# ezyVetCli

**A library and command line interface for the ezyVet v1 API written in Python.**  
For more information about ezyVet, the cloud-based veterinary practice management
system visit https://www.ezyvet.com/.

## License
**Copyright (C) 2018 - DoveLewis**  
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
To use this application, you will need to register and receive an API key
from the ezyVet API team.    
The application can be found https://www.ezyvet.com/api-signup

## Important version note
This program implements the ezyVet version 22.8 API, all options may not
be available in the version you are running. To check the availability of
features in your version navigate to your API reference:
https://YOURCLINICNAME.ezyvet.com/api/docs

## Contributing
This is an open source project and we hope you contribute. For more Information
about the ezyVet API, which this application is built upon, see:
https://apisandbox.trial.ezyvet.com/api/docs/.

## Requirements
This program has been tested under Ubuntu Linux 16.10 and 18.10. It should
run under POSIX compatable OS that can run Python 3.5+ but it has not been
tested.

## Setup
Copy `setting_Example.py` as `settings.py` and fill in your credentials.
This file is should never be under source control and should be explicitly
ignored in your `.gitignore` file.

### Clone the production (stable) branch.
Git: https://github.com/genepool99/ezyVetCLI.git   
`git clone -b production git@https://github.com/genepool99/ezyVetCLI.git`  

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
>(venv) user@computer:~/home/user/ezyvetcli$

### Install the dependencies
In the base ezyvetcli directory run  
`pip install -r requirements.txt`  

### Test your environment
`python3 ezyvet_cli.py --debug -T`  
There will be a verbose output, but you should see no "ERROR:" messages and ending with:    
>"INFO:__main__:Init Complete."

### When your done leave the virtual env with:  
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
#### Getting Started Examples
To test your credentials and setup with verbose output:  
`python3 ezyvet_cli -v -T`

Get help using the program:  
`python3 ezyvet_cli.py --help`

Get the list of appointment status codes:  
`python3 ezyvet_cli.py --appointmentStatus ''`

To get the first page of active records for hospitalized patients (assuming "In Hospital" is code 9):  
`python3 ezyvet_cli.py --appointment '{"active":"true", "appointment_status_id":9}'`

#### More Examples
Lookup a countries (1 page):  
`python3 ezyvet_cli.py -p --country ''`

Lookup invoice #50003:  
`python3 ezyvet_cli.py -p --invoice '{"id":50003}'`

Lookup invoice ID 50003 items:  
`python3 ezyvet_cli.py -p --invoiceLine '{"invoice_id":50003}' -m 30`

Lookup animals named foo:
`python3 ezyvet_cli.py -p --animal '{"name":"foo"}'`

Lookup contact ID 104834:  
`python3 ezyvet_cli.py -p --contact '{"id":104834}'`

Lookup contact details:  
`python3 ezyvet_cli.py -p --contactDetail '{"id":104834}'`

#### Building more complex filters
To build complex filters, see https://apisandbox.trial.ezyvet.com/api/docs for
a listing of query parameters.
