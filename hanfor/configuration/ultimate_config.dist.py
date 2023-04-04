"""The URL of the Ultimate server ending with /"""
ULTIMATE_API_URL = "https://ultimate.sopranium.de/api/"

"""
Folder of user_settings and toolchains,
leave empty for default (configuration/ultimate/[user_settings, toolchains])
"""
ULTIMATE_USER_SETTINGS_FOLDER = ""
ULTIMATE_TOOLCHAIN_FOLDER = ""

"""
Ultimate configurations
"""

ULTIMATE_CONFIGURATIONS = {
    'Standard': {'toolchain': 'ReqCheck', 'user_settings': 'ReqCheck-non-lin'}
}

"""
Automated Tags
If this option is enabled Hanfor will add tags to the corresponding requirements automatically when the Ultimate-PA job 
is done.
"""

AUTOMATED_TAGS = False
