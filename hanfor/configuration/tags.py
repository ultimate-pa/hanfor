# Tags added to the project when klicking 'add standard tags' in the tags interface

# orange E69F00 sky blue 56B4E9  009E73 F0E442 0072B2 D55E00 CC79A7 000000
orange = "#E69F00"
skyblue = "#56B4E9"
bluishgreen = "#009E73"
yellow = "#F0E442"
blue = "#0072B2"
vermilion = "#D55E00"
reddishpurple = "#CC79A7"

STANDARD_TAGS = {
    # Tags follow Davis et al. "Identifying and Measuring Quality in SRS
    "ambiguous": {"color": orange, "internal": False,
                  "description": """The requirement has more than one possible meaning."""},
    "incomplete": {"color": orange, "internal": False,
                  "description": """Some part necessary to understand the requirement is missing, 
                  or something is missing relative to the requirement."""},
    "incorrect": {"color": orange, "internal": False,
                   "description": """The behaviour descirbed by the requirement seems to be unfit for the system."""},
    "formally-incorrect": {"color": orange, "internal": False,
                  "description": """The (textual) representation of the requirement is erroneous."""},
    "inconcise": {"color": orange, "internal": False,
                  "description": """The requirement is wordy and therefore hard to read."""},
    "redundant": {"color": orange, "internal": False,
                  "description": """The requirement is stated more than once."""},
    "internally inconsistent": {"color": orange, "internal": False,
                  "description": """The requirement conflicts with another requirement or itself."""},
    "non-atomic": {"color": orange, "internal": False,
                  "description": """The requirement is not self-contained and only sensible if 
                  put together with other requirements. It is missing e.g.: some preconditions"""},
    "non-singular": {"color": orange, "internal": False,
                   "description": """The requirement contains more than one requirement."""},
    "wording": {"color": orange, "internal": False,
                    "description": """The requirement is written with bad grammar or uses the wrong words."""},
    # Communication tags
    "rfc": {"color": yellow, "internal": False, "description":
        """The meaning of this Requirement is unclear (not ambigouous) 
        and should be reviewed together with an engineer to enable formalisation."""},
    "missing-observables": {"color": yellow, "internal": False,
        "description": """The requirement is formalisable, but the observables are not obvious."""},
    "no-pattern": {"color": yellow, "internal": True,
                            "description": """There is no pattern to formalise this requirement."""},
    "not-formalisable": {"color": yellow, "internal": True,
                   "description": """The requirement is functional, but not formalisable for some reason."""},
    # Process tags
    "not-functional": {"color": bluishgreen, "internal": True, "description":
        """This requirement has no functional behaviour in the sense of formalisable behaviour."""},
    "post-poned": {"color": bluishgreen, "internal": True, "description":
        """For later, when there is more understanding of the system structure."""},
    # Analysis Tags
    "vacuous": {"color": vermilion, "internal": False,
                "description": """The requirement does not influence the system behaviour."""},
    "rt-inconsistent": {"color": vermilion, "internal": False,
                "description": """The requirement is rt-inconsistent with other requirements."""},
}