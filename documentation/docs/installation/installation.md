toc_depth: 2

# Preliminaries
Clone the repository:
```bash
$ git clone https://github.com/ultimate-pa/hanfor.git -b master --single-branch /your/hanfor/destination 
```

Hanfor requires [Python](https://www.python.org/) and is only tested with Python 3.6.x.
You can check if you have python already installed from the command line:
```bash
$ python -- version
Python 3.6.2
```

We recommend using a [virtual environment](https://virtualenv.pypa.io/en/latest/installation/). Create a new virtual environment with: 
```bash
$ virtualenv hanfor_python 
```
And activate it by sourcing:
```bash
$ source hanfor_python/bin/activate
```

Now the python dependencies needed to be installed into the virtual environment.
Inside the repository run:
```bash
$ pip install -r requirements.txt
```

# Configuration
- Copy `./hanfor/config.dist.py` to `./hanfor/config.py`.
- Edit the file `/hanfor/config.py` according your needs.
A config file looks as follows: 


```python
################################################################################
#                               Storage and folders                            #
################################################################################
# Set the SESSION_BASE_FOLDER to a path hanfor will store/load sessions.
# If set to None, hanfor will store its sessions in ./data
SESSION_BASE_FOLDER = './data'

################################################################################
#                                DEBUG and logging                             #
################################################################################

# Set DEBUG_MODE to true if you want to run the flask app in debug mode.
# In Production this should be set to False.
DEBUG_MODE = False

# If ASSETS_DEBUG True, Bundles will output their individual source files.
# This will significantly slow down performance.
ASSETS_DEBUG = False

# Set this to false if you want to use DEBUG toolbar with a URL_PREFIX
DEBUG_TB_INTERCEPT_REDIRECTS = False

# Set the log level to increase or decrease the logging sensitivity.
# You can set LOG_LEVEL (in decreasing sensitivity to):
# 'DEBUG', 'INFO', 'WARNING', 'ERROR'
LOG_LEVEL = 'DEBUG'

# Set LOG_TO_FILE to True if vou want to log to the file
# you specified in LOG_FILE
LOG_TO_FILE = True
LOG_FILE = 'hanfor.log'

# Set PYCHARM_DEBUG to True to supresss the flask debugging so it
# won't interfere with the pycharm debugger.
PYCHARM_DEBUG = False

################################################################################
#                         App and web server section                           #
################################################################################

# If you are running the app with a url prefix set URL_PREFIX like
# URL_PREFIX = '/hanfor'
URL_PREFIX = ''

# set a 'SECRET_KEY' to enable the Flask session cookies
SECRET_KEY = 'somesecretkeythatisonlyknowntoyou'

# Specify the PORT the app should be running at
PORT = 5000

# Set the host
HOST = '127.0.0.1'


################################################################################
#                             Available patterns                               #
################################################################################

""" Add available pattern to the PATTERNS dict.
* A single pattern should look like:
'pattern_name': {
    'pattern': 'if {R} then for {S} min nothing works.', # You can use [R, S, T, U]
    'env': {  # The allowed types for the variables/expressions.
              # Must cover all placeholders used in 'pattern'
        'R': ['bool'],        # Must be a sublist of ['bool', 'int', 'real']
        'S': ['int', 'real']  # Must be a sublist of ['bool', 'int', 'real']
    },
    'group': 'Your Group Name',  # Cluster the patterns in the hanfor frontend.
                                 # Must be appear in config PATTERNS_GROUP_ORDER
                                 # else it wont show up in the frontend.
    'pattern_order': 3  # Place the pattern appears in the frontend within its group.
}
"""
PATTERNS = {
    'Response': {
        'pattern': 'it is always the case that if {R} holds then {S} eventually holds',
        'env': {
            'R': ['bool'],
            'S': ['bool'],
        },
        'group': 'Order',
        'pattern_order': 0
    },
    'Absence': {
        'pattern': 'it is never the case that {R} holds',
        'env': {
            'R': ['bool']
        },
        'group': 'Occurence',
        'pattern_order': 4
    },
    'Toggle1': {
        'pattern': 'it is always the case that if {R} holds then {S} toggles {T}',
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['bool']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
}

# Define the ordering for pattern grouping in the pattern selection of hanfors frontent.
# All groups used in PATTERNS must be covered.
PATTERNS_GROUP_ORDER = [
    'Occurence',
    'Order',
    'Real-time'
]
```

## ReqAnalyzer
You can formalize requirements using hanfor and export them. 
The ReqAnalyzer is a tool to analyze the formalized requirements and part of the released tools of [Ultimate](https://github.com/ultimate-pa/ultimate).

#### Variant 1: Use the latest release

1. Install `Java JRE (1.8)`

Download the latest [Release](https://github.com/ultimate-pa/ultimate/releases).
The asset you need is called `UReqCheck-linux.zip`. 


#### Variant 2: Build the latest dev-version

1. Install `Java JDK (1.8)` and `Maven (>3.0)`
2. Clone the repository: `git clone https://github.com/ultimate-pa/ultimate`.
3. Navigate to the release scripts `cd ultimate/releaseScripts/default`
4. Generate a fresh binary `./makeFresh.sh`

You have now successfully forged binaries, which are located in `UReqCheck-linux`.

# Quick start
To start a fresh session use
```bash
$ python app.py <tag> -c <path_to_input_csv>.csv
```
    
Point your browser to [`http://127.0.0.1:<port in config.py>`](http://127.0.0.1:5000)

If you want to start an existing session, use
```bash
$ python app.py <tag>
```

You can see all available tags using the `-L` switch:
```bash
$ python app.py -L
```

The app will create a *session* naming it by the given `<tag>` argument.
A session creation process has the following steps:

 1. Create a session in a folder `config.py_SESSION_BASE_FOLDER/<tag>`.
 2. Read the given .csv file containing one requirement each row.
 3. Ask the user about a mapping of the csv-header-names for:
    * "ID", 
    * "Description", 
    * "Formalized Requirement", 
    * "Type"
 4. Create a Hanfor-Requirement for each row in the csv and store it to the session folder.
 5. Serve the Web-interface on the port specified in config.py