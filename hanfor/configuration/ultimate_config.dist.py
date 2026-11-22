"""The URL of the Ultimate server ending with /"""

ULTIMATE_API_URL = "https://ultimate.sopranium.de/api/"

"""
Folder of user_settings and toolchains.
default: (configuration/ultimate/[user_settings, toolchains])
"""
ULTIMATE_USER_SETTINGS_FOLDER = "configuration/ultimate/user_settings"
ULTIMATE_TOOLCHAIN_FOLDER = "configuration/ultimate/toolchains"

"""
Ultimate configurations
"""

ULTIMATE_CONFIGURATIONS = {
    "Standard": {"toolchain": "ReqCheck", "user_settings": "ReqCheck-non-lin"},
    # test scenarios against all requirements, one procedure each
    "Test scenarios": {"toolchain": "ReqCheck", "user_settings": "ReqCheck-TestScenarios"},
    # test scenarios of a requirement only against that requirement ("for ALL" still against all)
    "Test scenarios: only against their requirement": {
        "toolchain": "ReqCheck",
        "user_settings": "ReqCheck-TestScenarios-target",
    },
    # all test scenarios in one procedure: smaller file, slower to verify
    "Test scenarios: all in one procedure": {
        "toolchain": "ReqCheck",
        "user_settings": "ReqCheck-TestScenarios-one-procedure",
    },
}

"""
Automated Tags
If this option is enabled Hanfor will add tags to the corresponding requirements automatically when the Ultimate-PA job 
is done.
"""

AUTOMATED_TAGS = False

"""
Display Requirements without formalisation at the analysis page
"""
DISPLAY_REQUIREMENTS_WITHOUT_FORMALISATION = True
