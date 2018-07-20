from hanfor import db
from hanfor.boogie_parsing import boogie_parsing
from hanfor.models import Pattern, Scope

available_patterns = {
    'Invariant':
        'it is always the case that if {R} holds, then {S} holds as well',
    'Absence':
        'it is never the case that {R} holds',
    'Universality':
        'it is always the case that {R} holds',
    'Existence':
        '{R} eventually holds',
    'BoundedExistence':
        'transitions to states in which {R} holds occur at most twice',
    'Precedence':
        'it is always the case that if {R} holds then {S} previously held',
    'PrecedenceChain1-2':
        'it is always the case that if {R} holds and is succeeded by {S}, then {T} previously held',
    'PrecedenceChain2-1':
        'it is always the case that if {R} holds then {S} previously held and was preceded by {T}',
    'Response':
        'it is always the case that if {R} holds then {S} eventually holds',
    'ResponseChain1-2':
        'it is always the case that if {R} holds then {S} eventually holds and is succeeded by {T}',
    'ResponseChain2-1':
        'it is always the case that if {R} holds and is succeeded by {S}, '
        'then {T} eventually holds after {S}',
    'ConstrainedChain':
        'it is always the case that if {R} holds then {S} eventually holds and is succeeded by {T}, '
        'where {U} does not hold between {S} and {T}',
    'MinDuration':
        'it is always the case that once {R} becomes satisfied, it holds for at least {S} time units',
    'MaxDuration':
        'it is always the case that once {R} becomes satisfied, it holds for less than {S} time units',
    'BoundedRecurrence':
        'it is always the case that {R} holds at least every {S} time units',
    'BoundedResponse':
        'it is always the case that if {R} holds, then {S} holds after at most {T} time units',
    'BoundedInvariance':
        'it is always the case that if {R} holds, then {S} holds for at least {T} time units',
    'TimeConstrainedMinDuration':
        'it is always the case that if {R} holds for at least {S} time units, then {T} holds afterwards for '
        'at least {U} time units',
    'TimeConstrainedInvariant':
        'it is always the case that if {R} holds for at least {S} time units, then {T} holds afterwards',
    'ConstrainedTimedExistence':
        'it is always the case that if {R} holds, then {S} holds after at most {T} time units for at least '
        '{U} time units',
    'NotFormalizable': '// not formalizable'
}


available_scopes = {
    'GLOBALLY': 'Globally',
    'BEFORE': 'Before "{P}"',
    'AFTER': 'After "{P}"',
    'BETWEEN': 'Between "{P}" and "{Q}"',
    'AFTER_UNTIL': 'After "{P}" until "{Q}"',
    'NONE': '// None'
}

scope_env = {
    'GLOBALLY': {
    },
    'BEFORE': {
        'P': [boogie_parsing.BoogieType.bool]
    },
    'AFTER': {
        'P': [boogie_parsing.BoogieType.bool]
    },
    'BETWEEN': {
        'P': [boogie_parsing.BoogieType.bool],
        'Q': [boogie_parsing.BoogieType.bool]
    },
    'AFTER_UNTIL': {
        'P': [boogie_parsing.BoogieType.bool],
        'Q': [boogie_parsing.BoogieType.bool]
    },
    'NONE': {
    }
}

pattern_env = {
        'Invariant': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool]
        },
        'Absence': {
            'R': [boogie_parsing.BoogieType.bool]
        },
        'Universality': {
            'R': [boogie_parsing.BoogieType.bool]
        },
        'Existence': {
            'R': [boogie_parsing.BoogieType.bool]
        },
        'BoundedExistence': {
            'R': [boogie_parsing.BoogieType.bool]
        },
        'Precedence': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool]
        },
        'PrecedenceChain1-2': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool],
            'T': [boogie_parsing.BoogieType.bool]
        },
        'PrecedenceChain2-1': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool],
            'T': [boogie_parsing.BoogieType.bool]
        },
        'Response': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool]
        },
        'ResponseChain1-2': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool],
            'T': [boogie_parsing.BoogieType.bool]
        },
        'ResponseChain2-1': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool],
            'T': [boogie_parsing.BoogieType.bool]
        },
        'ConstrainedChain': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool],
            'T': [boogie_parsing.BoogieType.bool]
        },
        'MinDuration': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.real, boogie_parsing.BoogieType.int],
        },
        'MaxDuration': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.real, boogie_parsing.BoogieType.int],
        },
        'BoundedRecurrence': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.real, boogie_parsing.BoogieType.int],
        },
        'BoundedResponse': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool],
            'T': [boogie_parsing.BoogieType.real, boogie_parsing.BoogieType.int],
        },
        'BoundedInvariance': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool],
            'T': [boogie_parsing.BoogieType.real, boogie_parsing.BoogieType.int],
        },
        'TimeConstrainedMinDuration': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.real, boogie_parsing.BoogieType.int],
            'T': [boogie_parsing.BoogieType.bool],
            'U': [boogie_parsing.BoogieType.real, boogie_parsing.BoogieType.int],
        },
        'TimeConstrainedInvariant': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.real, boogie_parsing.BoogieType.int],
            'T': [boogie_parsing.BoogieType.bool],
        },
        'ConstrainedTimedExistence': {
            'R': [boogie_parsing.BoogieType.bool],
            'S': [boogie_parsing.BoogieType.bool],
            'T': [boogie_parsing.BoogieType.real, boogie_parsing.BoogieType.int],
            'U': [boogie_parsing.BoogieType.real, boogie_parsing.BoogieType.int],
        },
        'NotFormalizable': {}
}


def populate_patterns():
    for name, pattern in available_patterns.items():
        p = Pattern()
        p.name = name
        p.pattern = pattern
        p.allowed_types = pattern_env[name]
        db.session.add(p)
        db.session.commit()


def populate_scopes():
    for name, scope in available_scopes.items():
        s = Scope()
        s.name = name
        s.scope = scope
        s.allowed_types = scope_env[name]
        db.session.add(s)
        db.session.commit()
