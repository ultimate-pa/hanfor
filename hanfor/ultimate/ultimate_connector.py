import requests
import json

from configuration.ultimate_config import ULTIMATE_API_URL


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
    def start_job(code: str, toolchain_id: str, code_file_extension: str,
                  user_settings: str, ultimate_toolchain_xml: str) -> (str, str):
        url = ULTIMATE_API_URL
        payload = {'action': 'execute',
                   'code': code,
                   'toolchain[id]': toolchain_id,
                   "code_file_extension": code_file_extension,
                   "user_settings": user_settings,
                   "ultimate_toolchain_xml": ultimate_toolchain_xml}
        r = requests.post(url, data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        content = json.loads(r.text)
        return content

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
        print(content)
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
        print(content)
        return {'status': content['status'],
                'requestId': '',
                'result': content['msg']}
