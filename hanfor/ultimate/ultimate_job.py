from dataclasses import dataclass, field, asdict
import json
from datetime import datetime
from os import path
from flask import current_app
from utils import get_requirements
from pydantic import parse_obj_as

from defaults import Color
from configuration.ultimate_config import AUTOMATED_TAGS
from tags.tags import TagsApi
from reqtransformer import Requirement

FILE_VERSION = 0


@dataclass(frozen=True, kw_only=True)
class UltimateJob:
    job_id: str
    requirement_file: str
    toolchain_id: str
    toolchain_xml: str
    usersettings_name: str
    usersettings_json: str
    results: list[dict] = field(default_factory=list)
    api_url: str = ''
    job_status: str = 'scheduled'
    request_time: str = datetime.now().strftime("%Y.%m.%d, %H:%M:%S.%f")
    last_update: str = datetime.now().strftime("%Y.%m.%d, %H:%M:%S.%f")

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
        job = parse_obj_as(cls, data)
        return job

    def save_to_file(self, save_dir: str) -> None:
        with open(path.join(save_dir, f"{self.job_id}.json"), 'w') as save_file:
            save_file.write(json.dumps(asdict(self), indent=4))

    def update(self, data: dict, save_dir: str) -> None:
        if not data['requestId'] == self.job_id:
            raise Exception("Missmatch of requestID")
        last_status = self.job_status
        object.__setattr__(self, 'last_update', datetime.now().strftime("%Y.%m.%d, %H:%M:%S.%f"))
        object.__setattr__(self, 'job_status', data['status'])
        if not data['result'] == '':
            object.__setattr__(self, 'results', data['result'])
        self.save_to_file(save_dir)
        if AUTOMATED_TAGS and last_status == 'scheduled' and self.job_status == 'done':
            add_tags(self)

    def get(self) -> dict:
        return {'status': self.job_status,
                'requestId': self.job_id,
                'result': self.results,
                'request_time': self.request_time,
                'last_update': self.last_update}

    def get_download(self) -> dict:
        return asdict(self)


def check_ultimate_tag_is_available() -> None:
    tags_api = TagsApi()
    if tags_api.get('Ultimate_raw_data') == {}:
        # ultimate_raw_data tag is not available
        tags_api.add('Ultimate_raw_data', Color.BS_GRAY.value, False, '')


def get_all_requirement_ids() -> list[(str, str)]:
    """"
    returns a list of (requirementID, requirementID without -)
    """
    requirements = get_requirements(current_app.config['REVISION_FOLDER'])
    result = []
    for requirement in requirements:
        result.append((requirement.rid, requirement.rid.replace('-', '_') + '_'))
    return result


def add_ultimate_result_to_requirement(requirement_id: str,
                                       ultimate_results: list[dict],
                                       ultimate_job: UltimateJob) -> None:
    requirement = Requirement.load_requirement_by_id(requirement_id, current_app)
    if not requirement:
        return
    tmp = f"# {ultimate_job.job_id} ({ultimate_job.last_update})\n"
    for result in ultimate_results:
        result_text = result['longDesc'].replace('\n ', '\n\t')
        tmp += f"\n{result['type']}: {result_text}"
    if 'Ultimate_raw_data' in requirement.tags:
        requirement.tags['Ultimate_raw_data'] = f"{tmp}\n\n---\n\n{requirement.tags['Ultimate_raw_data']}"
    else:
        requirement.tags['Ultimate_raw_data'] = f"{tmp}"

    requirement.store()


def add_tags(ultimate_job: UltimateJob) -> None:
    check_ultimate_tag_is_available()
    requirements = get_all_requirement_ids()
    tags: dict[str, list[dict]] = {}
    for result in ultimate_job.results:
        for requirement in requirements:
            if requirement[1] in result['longDesc']:
                if requirement[0] in tags:
                    tags[requirement[0]].append(result)
                else:
                    tags[requirement[0]] = [result]
    for requirement, results in tags.items():
        add_ultimate_result_to_requirement(requirement, results, ultimate_job)
