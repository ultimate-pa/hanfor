[![LGPL License](http://img.shields.io/badge/license-LGPLv3+LE-brightgreen.svg)](https://github.com/ultimate-pa/hanfor/LICENSE)
[![Waffle.io - Columns and their card count](https://badge.waffle.io/aaa3217f1bcf93d0b14dc512da7cbac3e5b3a4f4a6ed2c939c2dd79c9404482b.svg?columns=all)](https://waffle.io/ultimate-pa/hanfor)
[![Board](https://img.shields.io/badge/board-github%20project-blue.svg)](https://github.com/orgs/ultimate-pa/projects/1)
<!--[![Waffle.io](https://img.shields.io/waffle/label/ultimate-pa/hanfor/in%20progress.svg?maxAge=1800)](https://waffle.io/ultimate-pa/hanfor)-->

# Hanfor
**Hanfor** **h**elps **an**alyzing **an**d **for**malizing **r**equirements.


# Setup 
We recommend using a virtual environment. 
Use `pip install -r requirements.txt` to install dependencies. 
Copy `config.dist.py` to `config.py`.
Edit the `config.py` according your needs.

# Usage
**Note:** 
 * Do not forget to enable the python virtual environment by sourcing bin/activate.
Start the app by running

    python app.py <path_to_input_csv>.csv <tag>

You can see all available tags using the ''-L'' switch:

    python app.py -L

If you use a tag not available a new session using this tag will be created.
    
Point your browser to `localhost:<port in config.py>`

# How it works

The app will create a session naming it by the given `<tag>` argument.
A session creation process has the following steps:

 1. Create a session in a folder `SESSION_BASE_FOLDER/<tag>`.
 2. Read the given .csv file containing one requirement each row.
 3. Ask the user to about a mapping of the csv header names for. 
    ID, Description, Formalized Requirement, Type
 4. Create a requirement for each row in the csv and store it to the session folder.
 5. Provide the Web-interface on the port specified in config.py
