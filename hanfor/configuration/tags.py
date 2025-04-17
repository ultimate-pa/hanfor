from configuration.defaults import Color



# Standard Tags which are added when a new project is created. The standard Tags can also be added with the
# 'add standard tags' button at the tags page.
STANDARD_TAGS = {
    # Tags for violation of requirements quality (follow Davis et al. "Identifying and Measuring Quality" in SRS)
    "non-atomic": {
        "color": Color.ORANGE.value,
        "internal": False,
        "description": (
            "The requirement describes more than one requirement and should be split.\n"
            "Note: requirements with _less_ than one requirement are incomplete not non-atomic."
        ),
    },
    "non-atomic/for each": {
        "color": Color.ORANGE.value,
        "internal": False,
        "description": (
            "The requirement uses a formulation quantifying over a group of things "
            "(e.g. for each error signal) where elements of  the group are unclear and "
            "might be extended properly."
        ),
    },
    "incomplete": {
        "color": Color.ORANGE.value,
        "internal": False,
        "description": "The requirements lacks some crucial component like the precondition or effect.",
    },
    "incomplete/open enumeration": {
        "color": Color.ORANGE.value,
        "internal": False,
        "description": (
            "The requirement uses a formulation quantifying over a group of things where it is unclear "
            "what things belong to the group (e.g.: for all doors e.g. right driver, left passenger, ... )."
            "\nNote: Use non-atomic/for each if the elements are clear, but a requirement per element "
            "should be written"
        ),
    },
    "missing observables": {
        "color": Color.ORANGE.value,
        "internal": False,
        "description": (
            "The requirement contains (at least partly) no identifiable observables, "
            "and is thus not ready for formalization (but would be formalizable and should be formalised "
            "if the observables were present). Note: Also use if observables are somehow unclear."
        ),
    },
    "redundant": {
        "color": Color.ORANGE.value,
        "internal": False,
        "description": (
            "This requirement is subsumed in another requirement "
            "(thus does not influence the system behaviour)\n"
            "Note: not to be confused with the ultimate analysis using ultimate/redundant"
        ),
    },
    "ambiguous": {
        "color": Color.ORANGE.value,
        "internal": False,
        "description": "something in the requirement does have several possible meanings",
    },
    "ambiguous/operator precedence": {
        "color": Color.ORANGE.value,
        "internal": False,
        "description": "Binding of logical operators in the sentence is unclear and requires parenthesis.",
    },
    "incorrect/documentation": {
        "color": Color.ORANGE.value,
        "internal": False,
        "description": (
            "The (textual) representation of the requirement is erroneous (e.g. does not follow the style "
            "guide or formal notation, or necessary information is just stated as a hint)"
        ),
    },
    "incorrect/traceability": {
        "color": Color.ORANGE.value,
        "internal": False,
        "description": "links in the document and references for traceability is broken or otherwise incorrect.",
    },
    "alias": {
        "color": Color.ORANGE.value,
        "internal": False,
        "description": "An observable or variable is called by different names.",
    },
    "inconsistent/external": {
        "color": Color.ORANGE.value,
        "internal": False,
        "description": (
            "The requirement is in conflict with other artefacts (e.g. higher level requirements) or with "
            "the reality."
        ),
    },
    "imprecise": {
        "color": Color.ORANGE.value,
        "internal": False,
        "description": (
            "The requirement is imprecise (e.g. if it is raining a little bit)\n"
            "Note: Too complete to be incomplete, but also not formalizable because to few information."
        ),
    },
    "inconsistent": {
        "color": Color.ORANGE.value,
        "internal": False,
        "description": "Inconsistent in relation to other requirements",
    },
    "inconcise": {
        "color": Color.ORANGE.value,
        "internal": False,
        "description": "The requirement is too wordy, should be written more concisely.",
    },
    "incorrect": {
        "color": Color.ORANGE.value,
        "internal": False,
        "description": "The behaviour described by the requirement seems to be unfit for the system.",
    },
    # Communication tags (regarding formalisation and process)
    "process/note": {"color": Color.YELLOW.value, "internal": True, "description": "An internal note."},
    "not formalizable/no pattern": {
        "color": Color.YELLOW.value,
        "internal": True,
        "description": "We do not have a pattern to formalize this requirement.",
    },
    "process/postponed": {
        "color": Color.YELLOW.value,
        "internal": True,
        "description": (
            "The requirement was decided to be obsolete by the customer and thus does not need any " "formalisation."
        ),
    },
    "process/example": {
        "color": Color.YELLOW.value,
        "internal": True,
        "description": "The requirement is a good example for a problem in this requirements set.",
    },
    "not formalizable/contains increment": {
        "color": Color.YELLOW.value,
        "internal": True,
        "description": (
            "The requirement contains an expression of the form A := A + 1, i.e., an expression that "
            "updates an observable based on its old value. We currently do not support these."
        ),
    },
    "non functional/defines variable": {
        "color": Color.YELLOW.value,
        "internal": True,
        "description": "Requirement is formalised as a variable definition and/or invariant.",
    },
    "non functional": {
        "color": Color.YELLOW.value,
        "internal": True,
        "description": (
            "The requirement does not formulate any observable system behaviour i.e. it has no sensible "
            "formalisation. Usually does not tell you how something should work but only that something "
            "should work."
        ),
    },
    "non functional/obsolete": {
        "color": Color.YELLOW.value,
        "internal": True,
        "description": (
            "The requirement was decided to be obsolete by the customer and thus does not need any " "formalisation."
        ),
    },
    "unclear": {
        "color": Color.LILAC.value,
        "internal": False,
        "description": (
            "Meaning of the requirement is unclear and it can not be attributed to any other quality "
            "property (thus has to be cleared with the customer)"
        ),
    },
    # Analysis Tags (from formal Analysis with Ultimate ReqAnalyzer)
    "ultimate/vacuous": {
        "color": Color.VERMILION.value,
        "internal": False,
        "description": "The requirement can not be triggered because of a different requirement.",
    },
    "ultimate/rt-inconsistent": {
        "color": Color.VERMILION.value,
        "internal": False,
        "description": "The requirement is rt-inconsistent with other requirements.",
    },
    "ultimate/inconsistent": {
        "color": Color.VERMILION.value,
        "internal": False,
        "description": "The requirements set was proven to be inconsistent by Ultimate.",
    },
    "ultimate/redundant": {
        "color": Color.VERMILION.value,
        "internal": False,
        "description": "The requirement does not influence the system behaviour and is thus redundant.",
    },
}
