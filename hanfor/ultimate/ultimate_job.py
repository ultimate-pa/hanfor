from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import json
from datetime import datetime
from os import path

FILE_VERSION = 0


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

    def save_to_file(self, save_dir: str):
        with open(path.join(save_dir, f"{self.job_id}.json"), 'w') as save_file:
            save_file.write(json.dumps(self.to_dict(), indent=4))

    def update(self, data: dict, save_dir: str):
        if not data['requestId'] == self.job_id:
            raise Exception("Missmatch of requestID")
        object.__setattr__(self, 'last_update', datetime.now().strftime("%Y.%m.%y, %H:%M:%S.%f"))
        object.__setattr__(self, 'job_status', data['status'])
        object.__setattr__(self, 'results', data['result'])
        self.save_to_file(save_dir)

    def get(self):
        return {'status': self.job_status,
                'requestId': self.job_id,
                'result': self.results,
                'request_time': self.request_time,
                'last_update': self.last_update}

    def get_download(self):
        return self.to_dict()
