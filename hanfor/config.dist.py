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
#
# Example:
# SCRIPT_EVALUATIONS = {
#     'search_sysrt.sh': ['', '/abs/path/to/sysrt.csv', '$VAR_NAME']
# }
SCRIPT_EVALUATIONS = {}

################################################################################
#                                DEBUG and logging                             #
################################################################################

# Sentry error tracking setup
USE_SENTRY = False
SENTRY_DSN = '<add_your_sentry_dsn>'

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
# generate one for production with, for example, openssl rand -base64 64
SECRET_KEY = os.environ.get('HANFOR_SECRET_KEY', default='tRKGzHAD3NHfk0u6jV7rMb42RBo/ldFIePPG2tgXrEZhAyOwQ/3aN0Uekt+mXmV2JGzMtiKSZBDhYKiO1fgu7A==')

# Specify the PORT the app should be running at
PORT = os.environ.get('HANFOR_PORT', default=5000)

# Set the host
HOST = os.environ.get('HANFOR_HOST',default='127.0.0.1')

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
    'ResponseChain2-1': {
        'pattern': 'it is always the case that if {R} holds and is succeeded by {S}, then {T} eventually holds after {S}',
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['bool']
        },
        'group': 'Order',
        'pattern_order': 1
    },
    'ResponseChain1-2': {
        'pattern': 'it is always the case that if {R} holds then {S} eventually holds and is succeeded by {T}',
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['bool'],
        },
        'group': 'Order',
        'pattern_order': 2
    },
    'ConstrainedChain': {
        'pattern': 'it is always the case that if {R} holds then {S} eventually holds and is succeeded by {T}, where {U} does not hold between {S} and {T}',
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['bool']
        },
        'group': 'Order',
        'pattern_order': 3
    },
    'Precedence': {
        'pattern': 'it is always the case that if {R} holds then {S} previously held',
        'env': {
            'R': ['bool'],
            'S': ['bool']
        },
        'group': 'Order',
        'pattern_order': 4
    },
    'PrecedenceChain2-1': {
        'pattern': 'it is always the case that if {R} holds then {S} previously held and was preceded by {T}',
        'env': {
            'R': ['bool'],
            'S': ['bool'], 'T': ['bool']
        },
        'group': 'Order',
        'pattern_order': 5
    },
    'PrecedenceChain1-2': {
        'pattern': 'it is always the case that if {R} holds and is succeeded by {S}, then {T} previously held',
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['bool']
        },
        'group': 'Order',
        'pattern_order': 6
    },
    'Universality': {
        'pattern': 'it is always the case that {R} holds',
        'env': {
            'R': ['bool']
        },
        'group': 'Occurence',
        'pattern_order': 0
    },
    'BoundedExistence': {
        'pattern': 'transitions to states in which {R} holds occur at most twice',
        'env': {
            'R': ['bool']
        },
        'group': 'Occurence',
        'pattern_order': 3
    },
    'Invariant': {
        'pattern': 'it is always the case that if {R} holds, then {S} holds as well',
        'env': {
            'R': ['bool'],
            'S': ['bool']
        },
        'group': 'Occurence',
        'pattern_order': 2
    },
    'Existence': {
        'pattern': '{R} eventually holds',
        'env': {
            'R': ['bool']
        },
        'group': 'Occurence',
        'pattern_order': 1
    },
    'Absence': {
        'pattern': 'it is never the case that {R} holds',
        'env': {
            'R': ['bool']
        },
        'group': 'Occurence',
        'pattern_order': 4
    },
    'BoundedResponse': {
        'pattern': 'it is always the case that if {R} holds, then {S} holds after at most {T} time units',
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
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
    'BoundedRecurrence': {
        'pattern': 'it is always the case that {R} holds at least every {S} time units',
        'env': {
            'R': ['bool'],
            'S': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'MaxDuration': {
        'pattern': 'it is always the case that once {R} becomes satisfied, it holds for less than {S} time units',
        'env': {
            'R': ['bool'],
            'S': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'TimeConstrainedMinDuration': {
        'pattern': 'it is always the case that if {R} holds for at least {S} time units, then {T} holds afterwards for at least {U} time units',
        'env': {
            'R': ['bool'],
            'S': ['real', 'int'],
            'T': ['bool'],
            'U': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'BoundedInvariance': {
        'pattern': 'it is always the case that if {R} holds, then {S} holds for at least {T} time units',
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'TimeConstrainedInvariant': {
        'pattern': 'it is always the case that if {R} holds for at least {S} time units, then {T} holds afterwards',
        'env': {
            'R': ['bool'],
            'S': ['real', 'int'],
            'T': ['bool']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'MinDuration': {
        'pattern': 'it is always the case that once {R} becomes satisfied, it holds for at least {S} time units',
        'env': {
            'R': ['bool'],
            'S': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'Toggle2': {
        'pattern': 'it is always the case that if {R} holds then {S} toggles {T} at most {U} time units later',
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['bool'],
            'U': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'ConstrainedTimedExistence': {
        'pattern': 'it is always the case that if {R} holds, then {S} holds after at most {T} time units for at least {U} time units',
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['real', 'int'],
            'U': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'BndTriggeredEntryConditionPattern': {
        'pattern': 'it is always the case that after {R} holds for at least {S} time units and {T} holds, then {U} holds',
        'env': {
            'R': ['bool'],
            'S': ['real', 'int'],
            'T': ['bool'],
            'U': ['bool']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'NotFormalizable': {
        'pattern': '// not formalizable',
        'env': {

        },
        'group': 'not_formalizable',
        'pattern_order': 0
    }
}

# Define the ordering for pattern grouping in the pattern selection of hanfors frontent.
# All groups used in PATTERNS must be covered.
PATTERNS_GROUP_ORDER = [
    'Occurence',
    'Order',
    'Real-time',
    'not_formalizable'
]
