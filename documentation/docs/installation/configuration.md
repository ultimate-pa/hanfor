toc_depth: 2

# Configuration

## Hanfor 
* Copy `./hanfor/config.dist.py` to `./hanfor/config.py`.
* Edit the file `/hanfor/config.py` according your needs.

### Hanfor config file:
A config file looks as follows: 
``` python
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
```

## ReqAnalyzer
*Coming soon*