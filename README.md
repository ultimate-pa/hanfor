[![LGPL License](http://img.shields.io/badge/license-LGPLv3+LE-brightgreen.svg)](https://github.com/ultimate-pa/hanfor/LICENSE)
[![Build Status](http://monteverdi.informatik.uni-freiburg.de/ci/buildStatus/icon?job=Hanfor)](http://monteverdi.informatik.uni-freiburg.de/ci/job/Hanfor/)
[![Board](https://img.shields.io/badge/board-github%20project-blue.svg)](https://github.com/orgs/ultimate-pa/projects/1)
<!--[![Waffle.io](https://img.shields.io/waffle/label/ultimate-pa/hanfor/in%20progress.svg?maxAge=1800)](https://waffle.io/ultimate-pa/hanfor)-->

# Hanfor
**Hanfor** **h**elps **an**alyzing **an**d **for**malizing **r**equirements.


# Setup 
 * Hanfor is only tested with Python 3.6.x and requires Python.
 * We recommend using a virtual environment, e.g., `virtualenv hanfor_python` followed by `source hanfor_python/bin/activate`. 
 * Use `pip install -r requirements.txt` to install dependencies. 
 * Copy `config.dist.py` to `config.py`.
 * Edit the `config.py` according your needs.

# Usage
**Note:** 
 * Do not forget to enable the python virtual environment by `source hanfor_python/bin/activate`.

Start the app by running

    python app.py <tag>

You can see all available tags using the ''-L'' switch:

    python app.py -L

To start a fresh session use

    python app.py <tag> -c <path_to_input_csv>.csv
    
Point your browser to `localhost:<port in config.py>`

# How it works

The app will create a *session* naming it by the given `<tag>` argument.
A session creation process has the following steps:

 1. Create a session in a folder `config.py_SESSION_BASE_FOLDER/<tag>`.
 2. Read the given .csv file containing one requirement each row.
 3. Ask the user about a mapping of the csv-header-names for:
    * "ID", "Description", "Formalized Requirement", "Type"
 4. Create a Hanfor-Requirement for each row in the csv and store it to the session folder.
 5. Provide the Web-interface on the port specified in config.py
 
