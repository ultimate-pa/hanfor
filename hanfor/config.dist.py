""" Configuration for the reqtransformer flask App.

@copyright: 2017 Samuel Roth <samuel@smel.de>
@licence: GPLv3
"""

import os

################################################################################
#                               Storage and folders                            #
################################################################################
# Set the SESSION_BASE_FOLDER to a path hanfor will store/load sessions.
# If set to None, hanfor will store its sessions in ./data
SESSION_BASE_FOLDER = None


################################################################################
#                                DEBUG and logging                             #
################################################################################

# Sentry error tracking setup
USE_SENTRY = False
SENTRY_DSN = "<add_your_sentry_dsn>"

# Set DEBUG_MODE to true if you want to run the flask app in debug mode.
DEBUG_MODE = False

# If ASSETS_DEBUG True, Bundles will output their individual source files.
# This will significantly slow down performance.
ASSETS_DEBUG = False

# Set this to false if you want to use DEBUG toolbar with a URL_PREFIX
DEBUG_TB_INTERCEPT_REDIRECTS = False

# Set the log level to increase or decrease the logging sensitivity.
# You can set LOG_LEVEL (in decreasing sensitivity to):
# 'DEBUG', 'INFO', 'WARNING', 'ERROR'
LOG_LEVEL = "DEBUG"

# Set LOG_TO_FILE to True if vou want to log to the file
# you specified in LOG_FILE
LOG_TO_FILE = False
LOG_FILE = "hanfor.log"

# Set PYCHARM_DEBUG to True to suppresss the flask debugging so it
# won't interfere with the pycharm debugger.
PYCHARM_DEBUG = False

################################################################################
#                         App and web server section                           #
################################################################################

# If you are running the app with a url prefix set URL_PREFIX like
# URL_PREFIX = '/hanfor'
URL_PREFIX = ""

# set a 'SECRET_KEY' to enable the Flask session cookies
# generate one for production with, for example, openssl rand -base64 64
SECRET_KEY = os.environ.get(
    "HANFOR_SECRET_KEY",
    default="tRKGzHAD3NHfk0u6jV7rMb42RBo/ldFIePPG2tgXrEZhAyOwQ/3aN0Uekt+mXmV2JGzMtiKSZBDhYKiO1fgu7A==",
)

# Specify the PORT the app should be running at
PORT = os.environ.get("HANFOR_PORT", default=5000)

# Set the host
HOST = os.environ.get("HANFOR_HOST", default="127.0.0.1")

################################################################################
#                               Miscellaneous                                  #
################################################################################
# Define the ordering for pattern grouping in the pattern selection of hanfors frontent.
# All groups used in PATTERNS must be covered.
PATTERNS_GROUP_ORDER = ["Occurence", "Order", "Real-time", "not_formalizable"]
