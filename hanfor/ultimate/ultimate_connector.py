import os
import requests
import json

from configuration.ultimate_config import ULTIMATE_API_URL, ULTIMATE_USER_SETTINGS_FOLDER, ULTIMATE_TOOLCHAIN_FOLDER
from ultimate.ultimate_job import UltimateJob


def get_user_settings(settings_name: str = "default") -> str | int:
    if ULTIMATE_USER_SETTINGS_FOLDER == "":
        path = "configuration/ultimate/user_settings/"
    else:
        path = ULTIMATE_USER_SETTINGS_FOLDER
        if not path.endswith("/"):
            path += "/"
    path += settings_name + ".json"
    if not os.path.isfile(path):
        return -1  # File does not exist
    with open(path, "r") as settings_file:
        tmp_json = json.loads(settings_file.read())
        return json.dumps(tmp_json)


def get_toolchain(toolchain_name: str) -> str | int:
    if ULTIMATE_TOOLCHAIN_FOLDER == "":
        path = "configuration/ultimate/toolchains/"
    else:
        path = ULTIMATE_TOOLCHAIN_FOLDER
        if not path.endswith("/"):
            path += "/"
    path += toolchain_name + ".xml"
    if not os.path.isfile(path):
        return -1  # File does not exist
    with open(path, "r") as toolchain_file:
        return toolchain_file.read()


class UltimateConnector:
    """"""

    def __init__(self):
        pass

    @staticmethod
    def get_version() -> str:
        r = requests.get(ULTIMATE_API_URL + 'version')
        if r.status_code != 200:
            return ''
        content = json.loads(r.text)
        if 'ultimate_version' in content.keys():
            return content['ultimate_version']
        return ''

    @staticmethod
    def start_job(code: bytes, code_file_extension: str, toolchain_id: str,
                  user_settings_name: str) -> UltimateJob:
        url = ULTIMATE_API_URL
        payload = {'action': 'execute',
                   'code': code,
                   'toolchain[id]': toolchain_id,
                   "code_file_extension": code_file_extension,
                   "user_settings": get_user_settings(user_settings_name),
                   "ultimate_toolchain_xml": get_toolchain(toolchain_id)}
        r = requests.post(url, data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        content = json.loads(r.text)
        uj = UltimateJob(job_id=content['requestId'],
                         requirement_file=code.decode("utf-8"),
                         toolchain_id=toolchain_id,
                         toolchain_xml=get_toolchain(toolchain_id),
                         usersettings_name=user_settings_name,
                         usersettings_json=get_user_settings(user_settings_name))
        return uj

    @staticmethod
    def get_job(job_id: str) -> dict | str:
        url = ULTIMATE_API_URL + 'job/get/' + job_id
        r = requests.get(url, headers={'Cache-Control': 'no-cache'})
        if r.status_code != 200:
            return ''
        content = json.loads(r.text)
        message = ""
        if 'results' in content.keys():
            message = content['results']
        return {'status': content['status'],
                'requestId': content['requestId'],
                'result': message}

    @staticmethod
    def delete_job(job_id: str) -> dict | str:
        url = ULTIMATE_API_URL + 'job/delete/' + job_id
        r = requests.get(url, headers={'Cache-Control': 'no-cache'})
        if r.status_code != 200:
            return ''
        content = json.loads(r.text)
        return {'status': content['status'],
                'requestId': '',
                'result': content['msg']}
