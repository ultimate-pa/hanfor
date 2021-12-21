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
SECRET_KEY = os.environ.get('HANFOR_SECRET_KEY',
                            default='tRKGzHAD3NHfk0u6jV7rMb42RBo/ldFIePPG2tgXrEZhAyOwQ/3aN0Uekt+mXmV2JGzMtiKSZBDhYKiO1fgu7A==')

# Specify the PORT the app should be running at
PORT = os.environ.get('HANFOR_PORT', default=5000)

# Set the host
HOST = os.environ.get('HANFOR_HOST', default='127.0.0.1')

################################################################################
#                               Miscellaneous                                  #
################################################################################
# Additional static terms to be included into the autocomplete field.
VARIABLE_AUTOCOMPLETE_EXTENSION = [
    'abs()'
]

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
    'Absence': {
        'pattern': 'it is never the case that {R} holds',
        'countertrace': {
            'globally':     ['true;⌈R⌉;true'],
            'before':       ['⌈!P⌉;⌈(!P && R)⌉;true'],
            'after':        ['true;⌈P⌉;true;⌈R⌉;true'],
            'between':      ['true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;true']
        },
        'env': {
            'R': ['bool']
        },
        'group': 'Occurence',
        'pattern_order': 4
    },
    'ConstrainedChain': {
        'pattern': 'it is always the case that if {R} holds then {S} eventually holds and is succeeded by {T}, where {U} does not hold between {S} and {T}',
        'countertrace': {
            'globally':     [],
            'before':       ['⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !S)⌉;⌈P⌉;true',
                             '⌈!P⌉;⌈(!P && R)⌉;⌈!P⌉;⌈(!P && S)⌉;⌈(!P && !T)⌉;⌈P⌉;true',
                             '⌈!P⌉;⌈(!P && R)⌉;⌈!P⌉;⌈(!P && S)⌉;⌈(!P && !T)⌉;⌈(!P && (!T && U))⌉;⌈!P⌉;⌈(!P && T)⌉;⌈!P⌉;⌈P⌉;true'],
            'after':        [],
            'between':      ['true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉;⌈Q⌉;true',
                             'true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈(!Q && !T)⌉;⌈Q⌉;true',
                             'true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈(!Q && !T)⌉;⌈(!Q && (!T && U))⌉;⌈!Q⌉;⌈(!Q && T)⌉;⌈!Q⌉;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉;⌈Q⌉;true',
                             'true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈(!Q && !T)⌉;⌈Q⌉;true',
                             'true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈(!Q && !T)⌉;⌈(!Q && (!T && U))⌉;⌈!Q⌉;⌈(!Q && T)⌉;⌈!Q⌉;⌈Q⌉;true']
        },
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['bool']
        },
        'group': 'Order',
        'pattern_order': 3
    },
    'DurationBoundL': {
        'pattern': 'it is always the case that once {R} becomes satisfied, it holds for at least {S} time units',
        'countertrace': {
            'globally':     ['true;⌈!R⌉;⌈R⌉ ∧ ℓ < S;⌈!R⌉;true'],
            'before':       ['⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉ ∧ ℓ < S;⌈(!P && !R)⌉;true'],
            'after':        ['true;⌈P⌉;true;⌈!R⌉;⌈R⌉ ∧ ℓ < S;⌈!R⌉;true'],
            'between':      ['true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ < S;⌈(!Q && !R)⌉;⌈!Q⌉;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ < S;⌈(!Q && !R)⌉;true']
        },
        'env': {
            'R': ['bool'],
            'S': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'DurationBoundU': {
        'pattern': 'it is always the case that once {R} becomes satisfied, it holds for less than {S} time units',
        'countertrace': {
            'globally':     ['true;⌈R⌉ ∧ ℓ ≥ S;true'],
            'before':       ['⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ S;true'],
            'after':        ['true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ S;true'],
            'between':      ['true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈!Q⌉;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;true']
        },
        'env': {
            'R': ['bool'],
            'S': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'EdgeResponseBoundL2': {
        'pattern': 'it is always the case that once {R} becomes satisfied, {S} holds for at least {T} time units',
        'countertrace': {
            'globally':     ['true;⌈!R⌉;⌈R⌉;⌈S⌉ ∧ ℓ < T;⌈!S⌉;true',
                             'true;⌈!R⌉;⌈(R && !S)⌉;true'],
            'before':       ['⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉;⌈(!P && S)⌉ ∧ ℓ < T;⌈(!P && !S)⌉;true;⌈(!P && !S)⌉;true',
                             '⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && (R && !S))⌉;true'],
            'after':        ['true;⌈P⌉;true;⌈!R⌉;⌈R⌉;⌈S⌉ ∧ ℓ < T;⌈!S⌉;true',
                             'true;⌈P⌉;true;⌈!R⌉;⌈(R && !S)⌉;true'],
            'between':      ['true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈(!Q && S)⌉ ∧ ℓ < T;⌈(!Q && !S)⌉;⌈!Q⌉;⌈Q⌉;true',
                             'true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈!Q⌉;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈(!Q && S)⌉ ∧ ℓ < T;⌈(!Q && !S)⌉;true',
                             'true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;true']
        },
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'EdgeResponseBoundU1': {
        'pattern': 'it is always the case that once {R} becomes satisfied and holds for at most {T} time units, then {S} holds  afterwards',
        'countertrace': {
            'globally':     ['true;⌈!R⌉;⌈R⌉ ∧ ℓ ≤ T;⌈(!R && !S)⌉;true'],
            'before':       ['⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉ ∧ ℓ ≥ T;⌈(!P && (!R && !S))⌉;true'],
            'after':        ['true;⌈P⌉;true;⌈!R⌉;⌈R⌉ ∧ ℓ ≤ T;⌈(!R && !S)⌉;true'],
            'between':      ['true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ ≤ T;⌈(!Q && (!R && !S))⌉;⌈!Q⌉;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ ≤ T;⌈(!Q && (!R && !S))⌉;true']
        },
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'EdgeResponseDelayBoundL2': {
        'pattern': 'it is always the case that once {R} becomes satisfied, {S} holds after at most {T} time units for at least {U} time units',
        'countertrace': {
            'globally':     ['true;⌈!R⌉;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true',
                             'true;⌈!R⌉;⌈R⌉;⌈true⌉ ∧ ℓ < T;⌈S⌉ ∧ ℓ < U;⌈!S⌉;true'],
            'before':       ['⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉ ∧ ℓ > T;true',
                             '⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉;⌈!P⌉ ∧ ℓ < T;⌈(!P && S)⌉ ∧ ℓ < U;⌈(!P && !S)⌉;true'],
            'after':        ['true;⌈P⌉;true;⌈!R⌉;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true',
                             'true;⌈P⌉;true;⌈!R⌉;⌈R⌉;⌈true⌉ ∧ ℓ < T;⌈S⌉ ∧ ℓ < U;⌈!S⌉;true'],
            'between':      ['true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true;⌈Q⌉;true',
                             'true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ < T;⌈(!Q && S)⌉ ∧ ℓ < U;⌈(!Q && !S)⌉;true;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true',
                             'true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ < T;⌈(!Q && S)⌉ ∧ ℓ < U;⌈(!Q && !S)⌉;true']
        },
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['real', 'int'],
            'U': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'EdgeResponseDelay': {
        'pattern': 'it is always the case that once {R} becomes satisfied, {S} holds after at most {T} time units',
        'countertrace': {
            'globally':     ['true;⌈!R⌉;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true'],
            'before':       ['⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉ ∧ ℓ > T;true'],
            'after':        ['true;⌈P⌉;true;⌈!R⌉;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true'],
            'between':      ['true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true']
        },
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'ExistenceBoundU': {
        'pattern': 'transitions to states in which {R} holds occur at most twice',
        'countertrace': {
            'globally':     ['true;⌈R⌉;⌈!R⌉;⌈R⌉;⌈!R⌉;⌈R⌉;true'],
            'before':       ['⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉;true'],
            'after':        ['true;⌈P⌉;true;⌈R⌉;⌈!R⌉;⌈R⌉;⌈!R⌉;⌈R⌉;true'],
            'between':      ['true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;true']
        },
        'env': {
            'R': ['bool']
        },
        'group': 'Occurence',
        'pattern_order': 3
    },
    'Initialization': {
        'pattern': 'it is always the case that initially "R" holds',
        'countertrace': {
            'globally':     ['⌈!R⌉;true'],
            'before':       ['⌈(!P && !R)⌉;true'],
            'after':        ['true;⌈P⌉;⌈!R⌉;true'],
            'between':      ['true;⌈(P && !Q)⌉;⌈(!Q && !R)⌉;true;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈(!Q && !R)⌉;true']
        },
        'env': {
            'R': ['bool']
        },
        'group': 'Order',
        'pattern_order': 0
    },
    'InvarianceBoundL2': {
        'pattern': 'it is always the case that if {R} holds, then {S} holds for at least {T} time units',
        'countertrace': {
            'globally':     ['true;⌈R⌉;⌈true⌉ ∧ ℓ < T;⌈!S⌉;true'],
            'before':       ['⌈!P⌉;⌈(!P && R)⌉;⌈!P⌉ ∧ ℓ < T;⌈(!P && !S)⌉;true'],
            'after':        ['true;⌈P⌉;true;⌈R⌉;⌈true⌉ ∧ ℓ < T;⌈!S⌉;true'],
            'between':      ['true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ < T;⌈(!Q && !S)⌉;⌈!Q⌉;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ < T;⌈(!Q && !S)⌉;true']
        },
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'Invariance': {
        'pattern': 'it is always the case that if {R} holds, then {S} holds as well',
        'countertrace': {
            'globally':     ['true;⌈(R && !S)⌉;true'],
            'before':       ['⌈!P⌉;⌈(!P && (R && !S))⌉;true'],
            'after':        ['true;⌈P⌉;true;⌈(R && !S)⌉;true'],
            'between':      ['true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈!Q⌉;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;true']
        },
        'env': {
            'R': ['bool'],
            'S': ['bool']
        },
        'group': 'Occurence',
        'pattern_order': 2
    },
    'PrecedenceChain12': {
        'pattern': 'it is always the case that if {R} holds and is succeeded by {S}, then {T} previously held',
        'countertrace': {
            'globally':     ['⌈!T⌉;⌈R⌉;true;⌈S⌉;true'],
            'before':       ['⌈(!P && !T)⌉;⌈(!P && R)⌉;⌈!P⌉;⌈(!P && S)⌉;true'],
            'after':        ['true;⌈P⌉;⌈!T⌉;⌈R⌉;true;⌈S⌉;true'],
            'between':      ['true;⌈(P && !Q)⌉;⌈(!Q && !T)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈!Q⌉;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈(!Q && !T)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;true']
        },
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['bool']
        },
        'group': 'Order',
        'pattern_order': 6
    },
    'PrecedenceChain2-1': {
        'pattern': 'it is always the case that if {R} holds then {S} previously held and was preceded by {T}',
        'countertrace': {
            'globally':     ['⌈!T⌉;⌈R⌉;true',
                             '⌈!S⌉;⌈R⌉;true',
                             '⌈!T⌉;⌈(S && !T)⌉;⌈!T⌉;⌈(!S && T)⌉;⌈!S⌉;⌈R⌉;true'],
            'before':       ['⌈(!P && !T)⌉;⌈(!P && R)⌉;true',
                             '⌈(!P && !S)⌉;⌈(!P && R)⌉;true',
                             '⌈(!P && !T)⌉;⌈(!P && (S && !T))⌉;⌈(!P && !T)⌉;⌈(!P && (!S && T))⌉;⌈(!P && !S)⌉;⌈(!P && R)⌉;true'],
            'after':        ['true;⌈P⌉;⌈!T⌉;⌈R⌉;true',
                             'true;⌈P⌉;⌈!S⌉;⌈R⌉;true',
                             'true;⌈P⌉;⌈!T⌉;⌈(S && !T)⌉;⌈!T⌉;⌈(!S && T)⌉;⌈!S⌉;⌈R⌉;true'],
            'between':      ['true;⌈(P && !Q)⌉;⌈(!Q && !T)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true',
                             'true;⌈(P && !Q)⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true',
                             'true;⌈(P && !Q)⌉;⌈(!Q && !T)⌉;⌈(!Q && (S && !T))⌉;⌈(!Q && !T)⌉;⌈(!Q && (!S && T))⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈(!Q && !T)⌉;⌈(!Q && R)⌉;true',
                             'true;⌈P⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;true',
                             'true;⌈P⌉;⌈(!Q && !T)⌉;⌈(!Q && (S && !T))⌉;⌈(!Q && !T)⌉;⌈(!Q && (!S && T))⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;true']
        },
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['bool']
        },
        'group': 'Order',
        'pattern_order': 5
    },
    'Precedence': {
        'pattern': 'it is always the case that if {R} holds then {S} previously held',
        'countertrace': {
            'globally':     ['⌈!S⌉;⌈R⌉;true'],
            'before':       ['⌈(!P && !S)⌉;⌈(!P && R)⌉;true'],
            'after':        ['true;⌈P⌉;⌈!S⌉;⌈R⌉;true'],
            'between':      ['true;⌈(P && (!Q && !S))⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;true']
        },
        'env': {
            'R': ['bool'],
            'S': ['bool']
        },
        'group': 'Order',
        'pattern_order': 4
    },
    'ReccurrenceBound': {
        'pattern': 'it is always the case that {R} holds at least every {S} time units',
        'countertrace': {
            'globally':     ['true;⌈!R⌉ ∧ ℓ > S;true'],
            'before':       ['⌈!P⌉;⌈(!P && !R)⌉ ∧ ℓ > S;true'],
            'after':        ['true;⌈P⌉;true;⌈!R⌉ ∧ ℓ > S;true'],
            'between':      ['true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉ ∧ ℓ > S;⌈!Q⌉;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉ ∧ ℓ > S;true']
        },
        'env': {
            'R': ['bool'],
            'S': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'ResponseBoundL12': {
        'pattern': 'it is always the case that if {R} holds for at least {T} time units, then {S} holds afterwards for at least {U} time units',
        'countertrace': {
            'globally':     ['true;⌈R⌉ ∧ ℓ ≥ T;⌈S⌉ ∧ ℓ <₀ U;⌈!S⌉;true'],
            'before':       ['⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ T;⌈(!P && S)⌉ ∧ ℓ <₀ U;⌈(!P && !S)⌉;true'],
            'after':        ['true;⌈P⌉;⌈R⌉ ∧ ℓ ≥ T;⌈S⌉ ∧ ℓ <₀ U;⌈!S⌉;true'],
            'between':      ['true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ T;⌈(!Q && S)⌉ ∧ ℓ <₀ U;⌈(!Q && !S)⌉;true;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ T;⌈(!Q && S)⌉ ∧ ℓ <₀ U;⌈(!Q && !S)⌉;true']
        },
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['real', 'int'],
            'U': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'ResponseBoundL1': {
        'pattern': 'it is always the case that if {R} holds for at least {T} time units, then {S} holds afterwards',
        'countertrace': {
            'globally':     ['true;⌈R⌉ ∧ ℓ ≥ T;⌈!S⌉;true'],
            'before':       ['⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ T;⌈(!P && !S)⌉;true'],
            'after':        ['true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ T;⌈!S⌉;true'],
            'between':      ['true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ T;⌈(!Q && !S)⌉;⌈!Q⌉;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ T;⌈(!Q && !S)⌉;true']
        },
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'ResponseChain1-2': {
        'pattern': 'it is always the case that if {R} holds then {S} eventually holds and is succeeded by {T}',
        'countertrace': {
            'globally': [],
            'before':       ['⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !S)⌉;⌈P⌉;true',
                             '⌈!P⌉;⌈(!P && R)⌉;⌈!P⌉;⌈(!P && S)⌉;⌈(!P && !T)⌉;⌈P⌉;true'],
            'after':        [],
            'between':      ['true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉;⌈Q⌉;true',
                             'true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈(!Q && !T)⌉;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉;⌈Q⌉;true',
                             'true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈(!Q && !T)⌉;⌈Q⌉;true']
        },
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['bool'],
        },
        'group': 'Order',
        'pattern_order': 2
    },
    'ResponseDelayBoundL1': {
        'pattern': 'it is always the case that if {R} holds for at least {T} time units, then {S} holds after at most {U} time units',
        'countertrace': {
            'globally':     ['true;⌈R⌉ ∧ ℓ ≥ T;⌈!S⌉ ∧ ℓ > U;true'],
            'before':       ['⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ T;⌈(!P && !S)⌉ ∧ ℓ > U;true'],
            'after':        ['true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ T;⌈!S⌉ ∧ ℓ > U;true'],
            'between':      ['true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ T;⌈(!Q && !S)⌉ ∧ ℓ > U;true;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ T;⌈(!Q && !S)⌉ ∧ ℓ > U;true']
        },
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['real', 'int'],
            'U': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'ResponseDelayBoundL2': {
        'pattern': 'it is always the case that if {R} holds, then {S} holds after at most {T} time units for at least {U} time units',
        'countertrace': {
            'globally':     ['true;⌈R⌉;⌈!S⌉ ∧ ℓ > T;true',
                             'true;⌈R⌉;⌈!S⌉ ∧ ℓ <₀ T;⌈S⌉ ∧ ℓ < U;⌈!S⌉;true'],
            'before':       ['⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !S)⌉ ∧ ℓ > T;true',
                             '⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !S)⌉ ∧ ℓ <₀ T;⌈(!P && S)⌉ ∧ ℓ < U;⌈(!P && !S)⌉;true'],
            'after':        ['true;⌈P⌉;true;⌈R⌉;⌈!S⌉ ∧ ℓ > T;true',
                             'true;⌈P⌉;true;⌈R⌉;⌈!S⌉ ∧ ℓ <₀ T;⌈S⌉ ∧ ℓ < U;⌈!S⌉;true'],
            'between':      ['true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true;⌈Q⌉;true',
                             'true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉ ∧ ℓ <₀ T;⌈(!Q && S)⌉ ∧ ℓ < U;⌈(!Q && !S)⌉;true;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true',
                             'true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉ ∧ ℓ <₀ T;⌈(!Q && S)⌉ ∧ ℓ < U;⌈(!Q && !S)⌉;true']
        },
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['real', 'int'],
            'U': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'ResponseDelay': {
        'pattern': 'it is always the case that if {R} holds, then {S} holds after at most {T} time units',
        'countertrace': {
            'globally':     ['true;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true'],
            'before':       ['⌈!P⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉ ∧ ℓ > T;true'],
            'after':        ['true;⌈P⌉;true;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true'],
            'between':      ['true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;⌈!Q⌉;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true']
        },
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'Response': {
        'pattern': 'it is always the case that if {R} holds then {S} eventually holds',
        'countertrace': {
            'globally':     [],
            'before':       ['⌈!P⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉;⌈P⌉;true'],
            'after':        [],
            'between':      ['true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉;⌈Q⌉;true']
        },
        'env': {
            'R': ['bool'],
            'S': ['bool'],
        },
        'group': 'Order',
        'pattern_order': 0
    },
    'TriggerResponseBoundL1': {
        'pattern': 'it is always the case that after {R} holds for at least {U} time units and {S} holds, then {T} holds',
        'countertrace': {
            'globally':     ['true;⌈R⌉ ∧ ℓ ≥ U;⌈(R && (S && !T))⌉;true'],
            'before':       ['⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ U;⌈(!P && (R && (S && !T)))⌉;true'],
            'after':        ['true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ U;⌈(R && (S && !T))⌉;true'],
            'between':      ['true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ U;⌈(!Q && (R && (S && !T)))⌉;true;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ U;⌈(!Q && (R && (S && !T)))⌉;true']
        },
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['bool'],
            'U': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'TriggerResponseDelayBoundL1': {
        'pattern': 'it is always the case that after {R} holds for at least {U} time units and {S} holds, then {T} holds after at most {V}  time units',
        'countertrace': {
            'globally':     ['true;⌈R⌉ ∧ ℓ ≥ U;⌈(R && (S && !T))⌉;⌈!T⌉ ∧ ℓ > V;true'],
            'before':       ['⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ U;⌈(!P && (R && (S && !T)))⌉;⌈(!P && !T)⌉ ∧ ℓ > V;true'],
            'after':        ['true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ U;⌈(R && (S && !T))⌉;⌈!T⌉ ∧ ℓ > V;true'],
            'between':      ['true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ U;⌈(!Q && (R && (S && !T)))⌉;⌈(!Q && !T)⌉ ∧ ℓ > V;true;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ U;⌈(!Q && (R && (S && !T)))⌉;⌈(!Q && !T)⌉ ∧ ℓ > V;true']
        },
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['bool'],
            'U': ['real', 'int'],
            'V': ['real', 'int'],
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'UniversalityDelay': {
        'pattern': 'it is always the case that {R} holds after at most {S} time units',
        'countertrace': {
            'globally':     ['⌈true⌉ ∧ ℓ ≥ S;⌈!R⌉;true'],
            'before':       ['⌈!P⌉ ∧ ℓ ≥ S;⌈(!P && !R)⌉;true'],
            'after':        ['true;⌈P⌉;⌈true⌉ ∧ ℓ ≥ S;⌈!R⌉;true'],
            'between':      ['true;⌈(P && !Q)⌉;⌈!Q⌉ ∧ ℓ ≥ S;⌈(!Q && !R)⌉;true;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈!Q⌉ ∧ ℓ ≥ S;⌈(!Q && !R)⌉;true']
        },
        'env': {
            'R': ['bool'],
            'S': ['real', 'int'],
        },
        'group': 'Real-time',
        'pattern_order': 5
    },
    'Universality': {
        'pattern': 'it is always the case that {R} holds',
        'countertrace': {
            'globally':     ['true;⌈!R⌉;true'],
            'before':       ['⌈!P⌉;⌈(!P && !R)⌉;true'],
            'after':        ['true;⌈P⌉;true;⌈!R⌉;true'],
            'between':      ['true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈!Q⌉;⌈Q⌉;true'],
            'after until':  ['true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;true']
        },
        'env': {
            'R': ['bool']
        },
        'group': 'Occurence',
        'pattern_order': 0
    },
    'NotFormalizable': {
        'pattern': '// not formalizable',
        'countertrace': {
            'globally': [],
            'before': [],
            'after': [],
            'between': [],
            'after until': []
        },
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

# Not implemented in Ultimate
# 'Existence': {
#        'pattern': '{R} eventually holds',
#        'countertrace': {
#        	'globally': [],
#        	'before': [],
#        	'after': [],
#        	'between': [],
#        	'after until': []
#        },
#        'env': {
#            'R': ['bool']
#        },
#        'group': 'Occurence',
#        'pattern_order': 1
#    },

# Not implemented in Ultimate
#    'ResponseChain2-1': {
#        'pattern': 'it is always the case that if {R} holds and is succeeded by {S}, then {T} eventually holds after {S}',
#        'countertrace': {
#        	'globally': [],
#        	'before': [],
#        	'after': [],
#        	'between': [],
#        	'after until': []
#        },
#        'env': {
#            'R': ['bool'],
#            'S': ['bool'],
#            'T': ['bool']
#        },
#        'group': 'Order',
#        'pattern_order': 1
#    },

# Not implemented in Ultimate
#    'Toggle1': {
#        'pattern': 'it is always the case that if {R} holds then {S} toggles {T}',
#        'countertrace': {
#        	'globally': [],
#        	'before': [],
#        	'after': [],
#        	'between': [],
#        	'after until': []
#        },
#        'env': {
#            'R': ['bool'],
#            'S': ['bool'],
#            'T': ['bool']
#        },
#        'group': 'Real-time',
#        'pattern_order': 0
#    },

# Not implemented in Ultimate
#    'Toggle2': {
#        'pattern': 'it is always the case that if {R} holds then {S} toggles {T} at most {U} time units later',
#        'countertrace': {
#        	'globally': [],
#        	'before': [],
#        	'after': [],
#        	'between': [],
#        	'after until': []
#        },
#        'env': {
#            'R': ['bool'],
#            'S': ['bool'],
#            'T': ['bool'],
#            'U': ['real', 'int']
#        },
#        'group': 'Real-time',
#        'pattern_order': 0
#    },

# Deprecated Pattern
#    'BndEntryConditionPattern': {
#        'pattern': 'it is always the case that after {R} holds for at least {S} time units, then {T} holds',
#        'countertrace': {
#        	'globally': [],
#        	'before': [],
#        	'after': [],
#        	'between': [],
#        	'after until': []
#        },
#        'env': {
#            'R': ['bool'],
#            'S': ['real', 'int'],
#            'T': ['bool']
#        },
#        'group': 'Real-time',
#        'pattern_order': 0
#    },
