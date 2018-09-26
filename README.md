# ezyVetCli

A command line interface for ezyVet.

## setup
Copy `setting_Example.py` as `settings.py` and fill in your credential details.
This file is not tracked by git.

## Development server setup
### Clone the production branch
Git: https://gitlab.com/genepool99/ezyvet  
`git clone -b production git@gitlab.com:genepool99/ezyvet.git`  

### Install venv
`sudo pip install --upgrade virtualenv`  
or  
`sudo apt-get install python3-venv`  

### Create a new virtualenv
`python3 -m venv /ezyvet/venv`

### Activate the virtualenv
`$source path_to_virtualenv/bin/active`

### Install dependencies
`cd ezyvet`  
`pip install -r requirements.txt`  

### leave the virtual env
`deactivate`  

## Coding standards
Python3 (3.5.2+)  

### Directory structure
ezyvet
  -wenv       <- the virtual environment
    -static   <- any static assets we might want to serve, like an html page

### Saving dependencies
After adding or upgrading modules you must run `pip freeze > requirements.txt` and commit the requirments.txt.

## Using the CLI
