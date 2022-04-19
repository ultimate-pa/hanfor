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
    'BndEntryConditionPattern': {
        'pattern': 'it is always the case that after {R} holds for at least {S}  time units, then {T} holds',
        'env': {
            'R': ['bool'],
            'S': ['real', 'int'],
            'T': ['bool']
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
    'BndTriggeredEntryConditionPatternDelayed': {
        'pattern': 'it is always the case that after {R} holds for at least {S}  time units and {T} holds, then {U} holds after at most {V}  time units',
        'env': {
            'R': ['bool'],
            'S': ['real', 'int'],
            'T': ['bool'],
            'U': ['bool'],
            'V': ['real', 'int'],
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'EdgeResponsePatternDelayed': {
        'pattern': 'it is always the case that once {R} becomes satisfied, {S} holds after at most {T} time units',
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'BndEdgeResponsePattern': {
        'pattern': 'it is always the case that once {R} becomes satisfied, {S} holds for at least {T} time units',
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'BndEdgeResponsePatternDelayed': {
        'pattern': 'it is always the case that once {R} becomes satisfied, {S} holds after at most {T} time units for at least {U} time units',
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['real', 'int'],
            'U': ['real', 'int']
        },
        'group': 'Real-time',
        'pattern_order': 0
    },
    'BndEdgeResponsePatternTU ': {
        'pattern': 'it is always the case that once {R} becomes satisfied and holds for at most {S} time units, then {T} holds  afterwards',
        'env': {
            'R': ['bool'],
            'S': ['real', 'int'],
            'T': ['bool']
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
    },
################################################################################
#                         Legacy Patterns                                      #
################################################################################
    'Toggle1': {
        'pattern': 'it is always the case that if {R} holds then {S} toggles {T}',
        'env': {
            'R': ['bool'],
            'S': ['bool'],
            'T': ['bool']
        },
        'group': 'Legacy',
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
        'group': 'Legacy',
        'pattern_order': 0
    },
}