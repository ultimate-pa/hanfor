import requests
import json

from configuration.ultimate_config import ULTIMATE_API_URL


class UltimateConnector:
    """"""
    def __init__(self):
        pass

    @staticmethod
    def get_version() -> str:
        r = requests.get(ULTIMATE_API_URL + "version")
        if r.status_code != 200:
            return ''
        content = json.loads(r.text)
        if 'ultimate_version' in content.keys():
            return content['ultimate_version']
        return ''
