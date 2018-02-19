[![LGPL License](http://img.shields.io/badge/license-LGPLv3+LE-brightgreen.svg)](https://github.com/ultimate-pa/hanfor/LICENSE)
[![Waffle.io - Columns and their card count](https://badge.waffle.io/aaa3217f1bcf93d0b14dc512da7cbac3e5b3a4f4a6ed2c939c2dd79c9404482b.svg?columns=all)](https://waffle.io/ultimate-pa/hanfor)
<!--[![Waffle.io](https://img.shields.io/waffle/label/ultimate-pa/hanfor/in%20progress.svg?maxAge=1800)](https://waffle.io/ultimate-pa/hanfor)-->

# Hanfor
Hanfor helps analyzing and formalizing requirements.


# Setup 
We recommend using a virtual environment. 
Use ``pip install -r requirements.txt` to install dependencies. 
Copy `config.dist.py` to `config.py`.
Edit the `config.py` according your needs.

# Usage
Start the app by running

    python app.py <path_to_input_csv>.csv <tag>
    
Point your browser to `localhost:<port in config.py>`

## Concrete usage
**Note:** 
 * Do not forget to enable the python virtual environment by sourcing bin/activate 

You can see all available tags in the data directory (`ls -al data/`). 

You can create a .req file by using the ''-G'' switch: 
    
    python app.py -G <tag>

# How it works

The app will create a session naming it using the given `<tag>` argument.
A session is created by the steps:

 1. Create a session in a folder `data/<tag>`.
 2. Read the given .csv file containing one requirement each row.
 3. Ask the user to state mapping of the csv headers. 
 (ID, Description, Formalized Requirement, Type)
 4. Create a requirement for each row in the csv and store it to the session folder.
 5. Provide the Web-interface on the port specified in config.py
