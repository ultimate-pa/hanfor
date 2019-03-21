""" Configuration for the reqtransformer flask App.

@copyright: 2017 Samuel Roth <samuel@smel.de>
@licence: GPLv3
"""
################################################################################
#                               Storage and folders                            #
################################################################################
# Set the SESSION_BASE_FOLDER to a path hanfor will store/load sessions.
# If set to None, hanfor will store its sessions in ./data
SESSION_BASE_FOLDER = None

################################################################################
#                         Script results for variables                         #
################################################################################
# Settings in this section determine the results in the "Script results" column
# in the variables table.
#
# To add a script evaluation:
# * The script must be available in the ./script_utils folder.
# * Add a entry to SCRIPT_EVALUATIONS e.g.
#     SCRIPT_EVALUATIONS = {
#         'search_sysrt.sh': ['foo', '$VAR_NAME']
#     }
#   Will evaluate search_sysrt.sh once for each variable VAR_NAME
#   using `foo $VAR_NAME` as input.
# * The script will be evaluated once at startup and on request (refresh script results)
#
# Available placeholders are:
# * $VAR_NAME -> The variable name.
SCRIPT_EVALUATIONS = {
    'search_sysrt.sh': ['', '/abs/path/to/sysrt.csv', '$VAR_NAME']
}

################################################################################
#                                DEBUG and logging                             #
################################################################################

# Set DEBUG_MODE to true if you want to run the flask app in debug mode.
DEBUG_MODE = True

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
LOG_TO_FILE = False
LOG_FILE = 'hanfor.log'

# Set PYCHARM_DEBUG to True to suppresss the flask debugging so it
# won't interfere with the pycharm debugger.
PYCHARM_DEBUG = False

################################################################################
#                         App and web server section                           #
################################################################################

# If you are running the app with a url prefix set URL_PREFIX like
# URL_PREFIX = '/hanfor'
URL_PREFIX = ''

# set a 'SECRET_KEY' to enable the Flask session cookies
SECRET_KEY = 'weguiwhwfpoqijwefgpwoejfqpwofej'

# Specify the PORT the app should be running at
PORT = 5000

# Set the host
HOST = '127.0.0.1'
