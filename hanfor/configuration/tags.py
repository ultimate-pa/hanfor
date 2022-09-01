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
    # Tags for violation of requirements quality (follow Davis et al. "Identifying and Measuring Quality in SRS)
    "version-revision-variant": {"color": orange, "internal": False,
                  "description": """There is somthing worng with version/revision/variant information
                  (e.g. the requirement is marked as rejected or belonging to other variant)"""},
    "atomic": {"color": orange, "internal": False,
               "description": """The requirement is not self-contained or constains more than one requirement.
                (e.g. preconditions are missing, two requirements listed under one item)"""},
    "ambiguous": {"color": orange, "internal": False,
                  "description": """The requirement has more than one possible meaning.
                  (e.g. binding of and and or are not uniquely identifiable)"""},
    "complete": {"color": orange, "internal": False,
                  "description": """Some part necessary to understand or for correctness of the requirement is missing."""},
    "correct": {"color": orange, "internal": False,
                   "description": """The behaviour descirbed by the requirement seems to be unfit for the system."""},
    "internally consistent": {"color": orange, "internal": False,
                "description": """The behaviour descirbed is inconsistent with some other requirement in this project."""},
    "externally consistent": {"color": orange, "internal": False,
                "description": """The behaviour descirbed is inconsistent with some thing outside this project"""},
    "formally correct": {"color": orange, "internal": False,
                  "description": """The (textual) representation of the requirement is erroneous."""},
    "concise": {"color": orange, "internal": False,
                  "description": """The requirement is wordy and should be shortened."""},
    "redundant": {"color": orange, "internal": False,
                  "description": """The requirement is stated more than once."""},
    "internally inconsistent": {"color": orange, "internal": False,
                  "description": """The requirement conflicts with another requirement or itself."""},
    "organised": {"color": orange, "internal": False,
                   "description": """Something with the organisational structure is wrong.
                   (e.g. heading does not fit the current requirement)"""},
    "precise": {"color": orange, "internal": False,
                    "description": """The requirement is imprecise.
                    (e.g. weaslewords, open enumerations)"""},
    "traceable": {"color": orange, "internal": False,
                "description": """Something wrong with references, links, references used for traceability.
                (e.g. a hardcoded reference to another requirement, a sudden link in the requirements)"""},
    "understandable": {"color": orange, "internal": False,
                "description": """The requirement is not written to be easily understandable.
                (e.g. requirement with complicated structure and many exception clauses)"""},
    # Communication tags (regarding formalisation and process)
    "rfc": {"color": yellow, "internal": False, "description":
        """The meaning of this Requirement is totally unclear (not ambigouous) 
        and should be reviewed together with an engineer to enable formalisation."""},
    "missing observables": {"color": yellow, "internal": False,
        "description": """The requirement is likely formalisable, but the observables are not obvious."""},
    "no pattern": {"color": yellow, "internal": True,
                    "description": """There is no pattern to formalise this requirement."""},
    "not formalisable": {"color": yellow, "internal": True,
                   "description": """The requirement is functional, but not formalisable for some reason."""},
    # Process tags
    "not functional": {"color": bluishgreen, "internal": True, "description":
        """This requirement has no functional behaviour (in the sense formalisability)."""},
    "post poned": {"color": bluishgreen, "internal": True, "description":
        """Attemt at formalisation is post-poned untli more information on the system is available."""},
    # Analysis Tags (from formal Analysis with Ultimate ReqAnalyzer)
    "vacuous": {"color": vermilion, "internal": False,
                "description": """The requirement does not influence the system behaviour."""},
    "rt-inconsistent": {"color": vermilion, "internal": False,
                "description": """The requirement is rt-inconsistent with other requirements."""},
}