################################################################################
#                               Miscellaneous                                  #
################################################################################
# Additional static terms to be included into the autocomplete field.
VARIABLE_AUTOCOMPLETE_EXTENSION = ["abs()"]

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
    "Response": {
        "pattern": "it is always the case that if {R} holds then {S} eventually holds",
        "countertraces": {
            "GLOBALLY": [],
            "BEFORE": ["⌈!P⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉;⌈P⌉;true"],
            "AFTER": [],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": [],
        },
        "env": {
            "R": ["bool"],
            "S": ["bool"],
        },
        "group": "Order",
        "pattern_order": 0,
    },
    "ResponseChain1-2": {
        "pattern": "it is always the case that if {R} holds then {S} eventually holds and is succeeded by {T}",
        "countertraces": {
            "GLOBALLY": [],
            "BEFORE": [
                "⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !S)⌉;⌈P⌉;true",
                "⌈!P⌉;⌈(!P && R)⌉;⌈!P⌉;⌈(!P && S)⌉;⌈(!P && !T)⌉;⌈P⌉;true",
            ],
            "AFTER": [],
            "BETWEEN": [
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉;⌈Q⌉;true",
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈(!Q && !T)⌉;⌈Q⌉;true",
            ],
            "AFTER_UNTIL": [],
        },
        "env": {
            "R": ["bool"],
            "S": ["bool"],
            "T": ["bool"],
        },
        "group": "Order",
        "pattern_order": 2,
    },
    "ConstrainedChain": {
        "pattern": "it is always the case that if {R} holds then {S} eventually holds and is succeeded by {T}, where {U} does not hold between {S} and {T}",
        "countertraces": {
            "GLOBALLY": [],
            "BEFORE": [
                "⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !S)⌉;⌈P⌉;true",
                "⌈!P⌉;⌈(!P && R)⌉;⌈!P⌉;⌈(!P && S)⌉;⌈(!P && !T)⌉;⌈P⌉;true",
                "⌈!P⌉;⌈(!P && R)⌉;⌈!P⌉;⌈(!P && S)⌉;⌈(!P && !T)⌉;⌈(!P && (!T && U))⌉;⌈!P⌉;⌈(!P && T)⌉;⌈!P⌉;⌈P⌉;true",
            ],
            "AFTER": [],
            "BETWEEN": [
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉;⌈Q⌉;true",
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈(!Q && !T)⌉;⌈Q⌉;true",
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈(!Q && !T)⌉;⌈(!Q && (!T && U))⌉;⌈!Q⌉;⌈(!Q && T)⌉;⌈!Q⌉;⌈Q⌉;true",
            ],
            "AFTER_UNTIL": [],
        },
        "group": "Order",
        "pattern_order": 4,
    },
    "Precedence": {
        "pattern": "it is always the case that if {R} holds then {S} previously held",
        "countertraces": {
            "GLOBALLY": ["⌈!S⌉;⌈R⌉;true"],
            "BEFORE": ["⌈(!P && !S)⌉;⌈(!P && R)⌉;true"],
            "AFTER": ["true;⌈P⌉;⌈!S⌉;⌈R⌉;true"],
            "BETWEEN": ["true;⌈(P && (!Q && !S))⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;true"],
        },
        "env": {"R": ["bool"], "S": ["bool"]},
        "group": "Order",
        "pattern_order": 4,
    },
    "PrecedenceChain2-1": {
        "pattern": "it is always the case that if {R} holds then {S} previously held and was preceded by {T}",
        "countertraces": {
            "GLOBALLY": ["⌈!T⌉;⌈R⌉;true", "⌈!S⌉;⌈R⌉;true", "⌈!T⌉;⌈(S && !T)⌉;⌈!T⌉;⌈(!S && T)⌉;⌈!S⌉;⌈R⌉;true"],
            "BEFORE": [
                "⌈(!P && !T)⌉;⌈(!P && R)⌉;true",
                "⌈(!P && !S)⌉;⌈(!P && R)⌉;true",
                "⌈(!P && !T)⌉;⌈(!P && (S && !T))⌉;⌈(!P && !T)⌉;⌈(!P && (!S && T))⌉;⌈(!P && !S)⌉;⌈(!P && R)⌉;true",
            ],
            "AFTER": [
                "true;⌈P⌉;⌈!T⌉;⌈R⌉;true",
                "true;⌈P⌉;⌈!S⌉;⌈R⌉;true",
                "true;⌈P⌉;⌈!T⌉;⌈(S && !T)⌉;⌈!T⌉;⌈(!S && T)⌉;⌈!S⌉;⌈R⌉;true",
            ],
            "BETWEEN": [
                "true;⌈(P && !Q)⌉;⌈(!Q && !T)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true",
                "true;⌈(P && !Q)⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true",
                "true;⌈(P && !Q)⌉;⌈(!Q && !T)⌉;⌈(!Q && (S && !T))⌉;⌈(!Q && !T)⌉;⌈(!Q && (!S && T))⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true",
            ],
            "AFTER_UNTIL": [
                "true;⌈P⌉;⌈(!Q && !T)⌉;⌈(!Q && R)⌉;true",
                "true;⌈P⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;true",
                "true;⌈P⌉;⌈(!Q && !T)⌉;⌈(!Q && (S && !T))⌉;⌈(!Q && !T)⌉;⌈(!Q && (!S && T))⌉;⌈(!Q && !S)⌉;⌈(!Q && R)⌉;true",
            ],
        },
        "env": {"R": ["bool"], "S": ["bool"], "T": ["bool"]},
        "group": "Order",
        "pattern_order": 5,
    },
    "PrecedenceChain1-2": {
        "pattern": "it is always the case that if {R} holds and is succeeded by {S}, then {T} previously held",
        "countertraces": {
            "GLOBALLY": ["⌈!T⌉;⌈R⌉;true;⌈S⌉;true"],
            "BEFORE": ["⌈(!P && !T)⌉;⌈(!P && R)⌉;⌈!P⌉;⌈(!P && S)⌉;true"],
            "AFTER": ["true;⌈P⌉;⌈!T⌉;⌈R⌉;true;⌈S⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈(!Q && !T)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈(!Q && !T)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈(!Q && S)⌉;true"],
        },
        "env": {"R": ["bool"], "S": ["bool"], "T": ["bool"]},
        "group": "Order",
        "pattern_order": 6,
    },
    "Universality": {
        "pattern": "it is always the case that {R} holds",
        "countertraces": {
            "GLOBALLY": ["true;⌈!R⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && !R)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈!R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;true"],
        },
        "env": {"R": ["bool"]},
        "group": "Occurence",
        "pattern_order": 0,
    },
    # TODO: maybe a new pattern ?
    "UniversalityDelay": {
        "pattern": "it is always the case that {R} holds after at most {S} time units",
        "countertraces": {
            "GLOBALLY": ["true ∧ ℓ ≥ S;⌈!R⌉;true"],
            "BEFORE": ["⌈!P⌉ ∧ ℓ ≥ S;⌈(!P && !R)⌉;true"],
            "AFTER": ["true;⌈P⌉;true ∧ ℓ ≥ S;⌈!R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉ ∧ ℓ ≥ S;⌈(!Q && !R)⌉;true;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉ ∧ ℓ ≥ S;⌈(!Q && !R)⌉;true"],
        },
        "env": {
            "R": ["bool"],
            "S": ["real"],
        },
        "group": "Real-time",
        "pattern_order": 5,
    },
    # TODO: new name ExistenceBoundU
    "BoundedExistence": {
        "pattern": "transitions to states in which {R} holds occur at most twice",
        "countertraces": {
            "GLOBALLY": ["true;⌈R⌉;⌈!R⌉;⌈R⌉;⌈!R⌉;⌈R⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉;⌈!R⌉;⌈R⌉;⌈!R⌉;⌈R⌉;true"],
            "BETWEEN": [
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true"
            ],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;true"],
        },
        "env": {"R": ["bool"]},
        "group": "Occurence",
        "pattern_order": 3,
    },
    # TODO: new name Invariance
    "Invariant": {
        "pattern": "it is always the case that if {R} holds, then {S} holds as well",
        "countertraces": {
            "GLOBALLY": ["true;⌈(R && !S)⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && (R && !S))⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈(R && !S)⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;true"],
        },
        "env": {"R": ["bool"], "S": ["bool"]},
        "group": "Occurence",
        "pattern_order": 2,
    },
    "Absence": {
        "pattern": "it is never the case that {R} holds",
        "countertraces": {
            "GLOBALLY": ["true;⌈R⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;true"],
        },
        "env": {"R": ["bool"]},
        "group": "Occurence",
        "pattern_order": 4,
    },
    # TODO: new name ResponseDelay
    "BoundedResponse": {
        "pattern": "it is always the case that if {R} holds, then {S} holds after at most {T} time units",
        "countertraces": {
            "GLOBALLY": ["true;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉ ∧ ℓ > T;true"],
            "AFTER": ["true;⌈P⌉;true;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true"],
        },
        "env": {"R": ["bool"], "S": ["bool"], "T": ["real"]},
        "group": "Real-time",
        "pattern_order": 0,
    },
    # TODO: new name ReccurrenceBound
    "BoundedRecurrence": {
        "pattern": "it is always the case that {R} holds at least every {S} time units",
        "countertraces": {
            "GLOBALLY": ["true;⌈!R⌉ ∧ ℓ > S;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && !R)⌉ ∧ ℓ > S;true"],
            "AFTER": ["true;⌈P⌉;true;⌈!R⌉ ∧ ℓ > S;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉ ∧ ℓ > S;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉ ∧ ℓ > S;true"],
        },
        "env": {"R": ["bool"], "S": ["real"]},
        "group": "Real-time",
        "pattern_order": 0,
    },
    # TODO: new name DurationBoundU
    "MaxDuration": {
        "pattern": "it is always the case that once {R} becomes satisfied, it holds for less than {S} time units",
        "countertraces": {
            "GLOBALLY": ["true;⌈R⌉ ∧ ℓ ≥ S;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ S;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ S;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;true"],
        },
        "env": {"R": ["bool"], "S": ["real"]},
        "group": "Real-time",
        "pattern_order": 0,
    },
    # TODO: new name ResponseBoundL12
    "TimeConstrainedMinDuration": {
        "pattern": "it is always the case that if {R} holds for at least {S} time units, then {T} holds afterwards for at least {U} time units",
        "countertraces": {
            "GLOBALLY": ["true;⌈R⌉ ∧ ℓ ≥ S;⌈T⌉ ∧ ℓ <₀ U;⌈!T⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ S;⌈(!P && T)⌉ ∧ ℓ <₀ U;⌈(!P && !T)⌉;true"],
            "AFTER": ["true;⌈P⌉;⌈R⌉ ∧ ℓ ≥ S;⌈T⌉ ∧ ℓ <₀ U;⌈!T⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && T)⌉ ∧ ℓ <₀ U;⌈(!Q && !T)⌉;true;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && T)⌉ ∧ ℓ <₀ U;⌈(!Q && !T)⌉;true"],
        },
        "env": {"R": ["bool"], "S": ["real"], "T": ["bool"], "U": ["real"]},
        "group": "Real-time",
        "pattern_order": 0,
    },
    # TODO: new name InvarianceBoundL2
    "BoundedInvariance": {
        "pattern": "it is always the case that if {R} holds, then {S} holds for at least {T} time units",
        "countertraces": {
            "GLOBALLY": ["true;⌈R⌉;true ∧ ℓ < T;⌈!S⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉;⌈!P⌉ ∧ ℓ < T;⌈(!P && !S)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉;true ∧ ℓ < T;⌈!S⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ < T;⌈(!Q && !S)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ < T;⌈(!Q && !S)⌉;true"],
        },
        "env": {"R": ["bool"], "S": ["bool"], "T": ["real"]},
        "group": "Real-time",
        "pattern_order": 0,
    },
    # TODO: new name ResponseBoundL1
    "TimeConstrainedInvariant": {
        "pattern": "it is always the case that if {R} holds for at least {S} time units, then {T} holds afterwards",
        "countertraces": {
            "GLOBALLY": ["true;⌈R⌉ ∧ ℓ ≥ S;⌈!T⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ S;⌈(!P && !T)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ S;⌈!T⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && !T)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && !T)⌉;true"],
        },
        "env": {"R": ["bool"], "S": ["real"], "T": ["bool"]},
        "group": "Real-time",
        "pattern_order": 0,
    },
    # TODO: new name DurationBoundL
    "MinDuration": {
        "pattern": "it is always the case that once {R} becomes satisfied, it holds for at least {S} time units",
        "countertraces": {
            "GLOBALLY": ["true;⌈!R⌉;⌈R⌉ ∧ ℓ < S;⌈!R⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉ ∧ ℓ < S;⌈(!P && !R)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈!R⌉;⌈R⌉ ∧ ℓ < S;⌈!R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ < S;⌈(!Q && !R)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ < S;⌈(!Q && !R)⌉;true"],
        },
        "env": {"R": ["bool"], "S": ["real"]},
        "group": "Real-time",
        "pattern_order": 0,
    },
    # TODO: new name ResponseDelayBoundL2
    "ConstrainedTimedExistence": {
        "pattern": "it is always the case that if {R} holds, then {S} holds after at most {T} time units for at least {U} time units",
        "countertraces": {
            "GLOBALLY": ["true;⌈R⌉;⌈!S⌉ ∧ ℓ > T;true", "true;⌈R⌉;⌈!S⌉ ∧ ℓ <₀ T;⌈S⌉ ∧ ℓ < U;⌈!S⌉;true"],
            "BEFORE": [
                "⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !S)⌉ ∧ ℓ > T;true",
                "⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !S)⌉ ∧ ℓ <₀ T;⌈(!P && S)⌉ ∧ ℓ < U;⌈(!P && !S)⌉;true",
            ],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉;⌈!S⌉ ∧ ℓ > T;true", "true;⌈P⌉;true;⌈R⌉;⌈!S⌉ ∧ ℓ <₀ T;⌈S⌉ ∧ ℓ < U;⌈!S⌉;true"],
            "BETWEEN": [
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true;⌈Q⌉;true",
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉ ∧ ℓ <₀ T;⌈(!Q && S)⌉ ∧ ℓ < U;⌈(!Q && !S)⌉;true;⌈Q⌉;true",
            ],
            "AFTER_UNTIL": [
                "true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true",
                "true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !S)⌉ ∧ ℓ <₀ T;⌈(!Q && S)⌉ ∧ ℓ < U;⌈(!Q && !S)⌉;true",
            ],
        },
        "env": {"R": ["bool"], "S": ["bool"], "T": ["real"], "U": ["real"]},
        "group": "Real-time",
        "pattern_order": 0,
    },
    # TODO: new name TriggerResponseBoundL1
    "BndTriggeredEntryConditionPattern": {
        "pattern": "it is always the case that after {R} holds for at least {S} time units and {T} holds, then {U} holds",
        "countertraces": {
            "GLOBALLY": ["true;⌈R⌉ ∧ ℓ ≥ S;⌈(R && (T && !U))⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ S;⌈(!P && (R && (T && !U)))⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ S;⌈(R && (T && !U))⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && (R && (T && !U)))⌉;true;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && (R && (T && !U)))⌉;true"],
        },
        "env": {"R": ["bool"], "S": ["real"], "T": ["bool"], "U": ["bool"]},
        "group": "Real-time",
        "pattern_order": 0,
    },
    # TODO: new name TriggerResponseDelayBoundL1
    "BndTriggeredEntryConditionPatternDelayed": {
        "pattern": "it is always the case that after {R} holds for at least {S}  time units and {T} holds, then {U} holds after at most {V}  time units",
        "countertraces": {
            "GLOBALLY": ["true;⌈R⌉ ∧ ℓ ≥ S;⌈(R && (T && !U))⌉;⌈!U⌉ ∧ ℓ > V;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉ ∧ ℓ ≥ S;⌈(!P && (R && (T && !U)))⌉;⌈(!P && !U)⌉ ∧ ℓ > V;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉ ∧ ℓ ≥ S;⌈(R && (T && !U))⌉;⌈!U⌉ ∧ ℓ > V;true"],
            "BETWEEN": [
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && (R && (T && !U)))⌉;⌈(!Q && !U)⌉ ∧ ℓ > V;true;⌈Q⌉;true"
            ],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉ ∧ ℓ ≥ S;⌈(!Q && (R && (T && !U)))⌉;⌈(!Q && !U)⌉ ∧ ℓ > V;true"],
        },
        "env": {
            "R": ["bool"],
            "S": ["real"],
            "T": ["bool"],
            "U": ["bool"],
            "V": ["real"],
        },
        "group": "Real-time",
        "pattern_order": 0,
    },
    # TODO: new name EdgeResponseDelay
    "EdgeResponsePatternDelayed": {
        "pattern": "it is always the case that once {R} becomes satisfied, {S} holds after at most {T} time units",
        "countertraces": {
            "GLOBALLY": ["true;⌈!R⌉;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉ ∧ ℓ > T;true"],
            "AFTER": ["true;⌈P⌉;true;⌈!R⌉;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true"],
        },
        "env": {"R": ["bool"], "S": ["bool"], "T": ["real"]},
        "group": "Real-time",
        "pattern_order": 0,
    },
    # TODO: new name EdgeResponseBoundL2
    "BndEdgeResponsePattern": {
        "pattern": "it is always the case that once {R} becomes satisfied, {S} holds for at least {T} time units",
        "countertraces": {
            "GLOBALLY": ["true;⌈!R⌉;⌈R⌉;⌈S⌉ ∧ ℓ < T;⌈!S⌉;true", "true;⌈!R⌉;⌈(R && !S)⌉;true"],
            "BEFORE": [
                "⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉;⌈(!P && S)⌉ ∧ ℓ < T;⌈(!P && !S)⌉;true;⌈(!P && !S)⌉;true",
                "⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && (R && !S))⌉;true",
            ],
            "AFTER": ["true;⌈P⌉;true;⌈!R⌉;⌈R⌉;⌈S⌉ ∧ ℓ < T;⌈!S⌉;true", "true;⌈P⌉;true;⌈!R⌉;⌈(R && !S)⌉;true"],
            "BETWEEN": [
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈(!Q && S)⌉ ∧ ℓ < T;⌈(!Q && !S)⌉;⌈!Q⌉;⌈Q⌉;true",
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈!Q⌉;⌈Q⌉;true",
            ],
            "AFTER_UNTIL": [
                "true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈(!Q && S)⌉ ∧ ℓ < T;⌈(!Q && !S)⌉;true",
                "true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;true",
            ],
        },
        "env": {"R": ["bool"], "S": ["bool"], "T": ["real"]},
        "group": "Real-time",
        "pattern_order": 0,
    },
    # TODO: new name EdgeResponseDelayBoundL2
    "BndEdgeResponsePatternDelayed": {
        "pattern": "it is always the case that once {R} becomes satisfied, {S} holds after at most {T} time units for at least {U} time units",
        "countertraces": {
            "GLOBALLY": ["true;⌈!R⌉;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true", "true;⌈!R⌉;⌈R⌉;true ∧ ℓ < T;⌈S⌉ ∧ ℓ < U;⌈!S⌉;true"],
            "BEFORE": [
                "⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && (R && !S))⌉;⌈(!P && !S)⌉ ∧ ℓ > T;true",
                "⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉;⌈!P⌉ ∧ ℓ < T;⌈(!P && S)⌉ ∧ ℓ < U;⌈(!P && !S)⌉;true",
            ],
            "AFTER": [
                "true;⌈P⌉;true;⌈!R⌉;⌈(R && !S)⌉;⌈!S⌉ ∧ ℓ > T;true",
                "true;⌈P⌉;true;⌈!R⌉;⌈R⌉;true ∧ ℓ < T;⌈S⌉ ∧ ℓ < U;⌈!S⌉;true",
            ],
            "BETWEEN": [
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true;⌈Q⌉;true",
                "true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ < T;⌈(!Q && S)⌉ ∧ ℓ < U;⌈(!Q && !S)⌉;true;⌈Q⌉;true",
            ],
            "AFTER_UNTIL": [
                "true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && (R && !S))⌉;⌈(!Q && !S)⌉ ∧ ℓ > T;true",
                "true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉;⌈!Q⌉ ∧ ℓ < T;⌈(!Q && S)⌉ ∧ ℓ < U;⌈(!Q && !S)⌉;true",
            ],
        },
        "env": {"R": ["bool"], "S": ["bool"], "T": ["real"], "U": ["real"]},
        "group": "Real-time",
        "pattern_order": 0,
    },
    # TODO: new name EdgeResponseBoundU1
    "BndEdgeResponsePatternTU ": {
        "pattern": "it is always the case that once {R} becomes satisfied and holds for at most {S} time units, then {T} holds  afterwards",
        "countertraces": {
            "GLOBALLY": ["true;⌈!R⌉;⌈R⌉ ∧ ℓ ≤ S;⌈(!R && !T)⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && !R)⌉;⌈(!P && R)⌉ ∧ ℓ ≥ S;⌈(!P && (!R && !T))⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈!R⌉;⌈R⌉ ∧ ℓ ≤ S;⌈(!R && !T)⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ ≤ S;⌈(!Q && (!R && !T))⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && !R)⌉;⌈(!Q && R)⌉ ∧ ℓ ≤ S;⌈(!Q && (!R && !T))⌉;true"],
        },
        "env": {"R": ["bool"], "S": ["real"], "T": ["bool"]},
        "group": "Real-time",
        "pattern_order": 0,
    },
    # TODO: new pattern
    "Initialization ": {
        "pattern": "it is always the case that initially {R} holds",
        "countertraces": {
            "GLOBALLY": ["⌈!R⌉;true"],
            "BEFORE": ["⌈(!P && !R)⌉;true"],
            "AFTER": ["true;⌈P⌉;⌈!R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈(!Q && !R)⌉;true;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈(!Q && !R)⌉;true"],
        },
        "env": {"R": ["bool"]},
        "group": "Order",
        "pattern_order": 6,
    },
    # TODO: new pattern
    "Persistence": {
        "pattern": "it is always the case that if {R} holds, then it holds persistently",
        "countertraces": {
            "GLOBALLY": ["true;⌈R⌉;⌈!R⌉;true"],
            "BEFORE": ["⌈!P⌉;⌈(!P && R)⌉;⌈(!P && !R)⌉;true"],
            "AFTER": ["true;⌈P⌉;true;⌈R⌉;⌈!R⌉;true"],
            "BETWEEN": ["true;⌈(P && !Q)⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;⌈!Q⌉;⌈Q⌉;true"],
            "AFTER_UNTIL": ["true;⌈P⌉;⌈!Q⌉;⌈(!Q && R)⌉;⌈(!Q && !R)⌉;true"],
        },
        "env": {"R": ["bool"]},
        "group": "Order",
        "pattern_order": 7,
    },
    # TODO: new pattern
    "InvarianceDelay": {
        "pattern": "it is always the case that if {R} holds, then {S} holds as well after at most {T} time units",
        "countertraces": {
            "GLOBALLY": ["true;⌈R && S⌉;⌈R && !S⌉;true", "true;⌈R && !S⌉;⌈!S⌉ ∧ ℓ > T;true"],
            "BEFORE": [],
            "AFTER": [],
            "BETWEEN": [],
            "AFTER_UNTIL": [],
        },
        "env": {"R": ["bool"], "S": ["bool"], "T": ["real"]},
        "group": "Real-time",
        "pattern_order": 10,
    },
    "NotFormalizable": {"pattern": "no pattern set", "env": {}, "group": "not_formalizable", "pattern_order": 0},
    ################################################################################
    #                         Legacy Patterns                                      #
    ################################################################################
    # TODO: Legacy, not implemented
    "Toggle1": {
        "pattern": "it is always the case that if {R} holds then {S} toggles {T}",
        "countertraces": {"GLOBALLY": [], "BEFORE": [], "AFTER": [], "BETWEEN": [], "AFTER_UNTIL": []},
        "env": {"R": ["bool"], "S": ["bool"], "T": ["bool"]},
        "group": "Legacy",
        "pattern_order": 0,
    },
    # TODO: Legacy, not implemented
    "Toggle2": {
        "pattern": "it is always the case that if {R} holds then {S} toggles {T} at most {U} time units later",
        "countertraces": {"GLOBALLY": [], "BEFORE": [], "AFTER": [], "BETWEEN": [], "AFTER_UNTIL": []},
        "env": {"R": ["bool"], "S": ["bool"], "T": ["bool"], "U": ["real"]},
        "group": "Legacy",
        "pattern_order": 0,
    },
    # TODO: Legacy, not implemented
    "BndEntryConditionPattern": {
        "pattern": "it is always the case that after {R} holds for at least {S}  time units, then {T} holds",
        "countertraces": {"GLOBALLY": [], "BEFORE": [], "AFTER": [], "BETWEEN": [], "AFTER_UNTIL": []},
        "env": {"R": ["bool"], "S": ["real"], "T": ["bool"]},
        "group": "Legacy",
        "pattern_order": 0,
    },
    # TODO: Legacy, not implemented
    "ResponseChain2-1": {
        "pattern": "it is always the case that if {R} holds and is succeeded by {S}, then {T} eventually holds after {S}",
        "countertraces": {"GLOBALLY": [], "BEFORE": [], "AFTER": [], "BETWEEN": [], "AFTER_UNTIL": []},
        "env": {"R": ["bool"], "S": ["bool"], "T": ["bool"]},
        "group": "Legacy",
        "pattern_order": 1,
    },
    # TODO: Legacy, not implemented
    "Existence": {
        "pattern": "{R} eventually holds",
        "countertraces": {"GLOBALLY": [], "BEFORE": [], "AFTER": [], "BETWEEN": [], "AFTER_UNTIL": []},
        "env": {"R": ["bool"]},
        "group": "Legacy",
        "pattern_order": 1,
    },
}
