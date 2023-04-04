from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import json
from datetime import datetime
from os import path
from flask import current_app
from utils import get_requirements

from defaults import Color
from configuration.ultimate_config import AUTOMATED_TAGS
from tags.tags import TagsApi
from reqtransformer import Requirement

FILE_VERSION = 0


def check_ultimate_tag_is_available() -> None:
    tags_api = TagsApi()
    if tags_api.get('Ultimate_raw_data') == {}:
        # ultimate_raw_data tag is not available
        tags_api.add('Ultimate_raw_data', Color.BS_GRAY.value, False, '')


def get_all_requirement_ids() -> list[str]:
    requirements = get_requirements(current_app.config['REVISION_FOLDER'])
    result = []
    for requirement in requirements:
        result.append(requirement.rid.replace('-', '_') + '_')
    return result


def add_ultimate_result_to_requirement(requirement_id: str, ultimate_result: dict) -> None:
    requirement = Requirement.load_requirement_by_id(requirement_id, current_app)
    if not requirement:
        return
    if 'Ultimate_raw_data' in requirement.tags:
        requirement.tags['Ultimate_raw_data'] += f"\n{ultimate_result['type']}: {ultimate_result['longDesc']}"
    else:
        requirement.tags['Ultimate_raw_data'] = f"{ultimate_result['type']}: {ultimate_result['longDesc']}"

    requirement.store()


def add_tags(results: list[dict]) -> None:
    check_ultimate_tag_is_available()
    requirements = get_all_requirement_ids()
    for result in results:
        for requirement in requirements:
            if requirement in result['longDesc']:
                add_ultimate_result_to_requirement(requirement[:-1].replace('_', '-'), result)


@dataclass_json
@dataclass(frozen=True, kw_only=True)
class UltimateJob:
    job_id: str
    requirement_file: str
    toolchain_id: str
    toolchain_xml: str
    usersettings_name: str
    usersettings_json: str
    api_url: str = ''
    job_status: str = 'scheduled'
    request_time: str = datetime.now().strftime("%Y.%m.%y, %H:%M:%S.%f")
    last_update: str = datetime.now().strftime("%Y.%m.%y, %H:%M:%S.%f")
    results: list[dict] = field(default_factory=list)

    @classmethod
    def from_file(cls, *, save_dir: str = None, job_id: str = None, file_name: str = None):
        # generate file_name from save_dir and job_id
        if file_name is None:
            if save_dir is None:
                raise Exception("save_dir is not defined!")
            if job_id is None:
                raise Exception("job_id is not defined!")
            file_name = path.join(save_dir, f"{job_id}.json")

        # check if file exist
        if not path.isfile(file_name):
            raise Exception(f"{file_name} can not be found!")

        # read file
        with open(file_name, 'r') as save_file:
            data = json.load(save_file)
        # TODO: check for old file version
        job = cls.from_dict(data)
        return job

    def save_to_file(self, save_dir: str) -> None:
        with open(path.join(save_dir, f"{self.job_id}.json"), 'w') as save_file:
            save_file.write(json.dumps(self.to_dict(), indent=4))

    def update(self, data: dict, save_dir: str) -> None:
        if not data['requestId'] == self.job_id:
            raise Exception("Missmatch of requestID")
        last_status = self.job_status
        object.__setattr__(self, 'last_update', datetime.now().strftime("%Y.%m.%y, %H:%M:%S.%f"))
        object.__setattr__(self, 'job_status', data['status'])
        object.__setattr__(self, 'results', data['result'])
        self.save_to_file(save_dir)
        if AUTOMATED_TAGS and last_status == 'scheduled' and self.job_status == 'done':
            add_tags(data['result'])

    def get(self) -> dict:
        return {'status': self.job_status,
                'requestId': self.job_id,
                'result': self.results,
                'request_time': self.request_time,
                'last_update': self.last_update}

    def get_download(self) -> dict:
        return self.to_dict()
