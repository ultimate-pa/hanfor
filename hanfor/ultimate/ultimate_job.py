import json
from datetime import datetime
from os import path

FILE_VERSION = 0


class UltimateJob:
    def __init__(self, job_id: str, save_dir: str):
        self.job_id = job_id
        self.job_status = 'scheduled'
        self.request_time = datetime.now()
        self.last_update = datetime.now()
        self.results: list[dict] = []
        if save_dir.endswith('.json'):
            self.file_name = save_dir
        else:
            self.file_name = path.join(save_dir, f"{job_id}.json")

    @classmethod
    def from_file(cls, save_dir: str, job_id: str):
        file_name = save_dir
        if not file_name.endswith("/"):
            file_name += "/"
        file_name += f"{job_id}.json"
        with open(file_name, 'r') as save_file:
            data = json.load(save_file)
        # check for old file version
        if data['save_file'] == 0:
            # nothing to do jet
            pass
        job = cls(job_id, file_name)
        job.job_status = data['job_status']
        job.request_time = datetime.strptime(data['request_time'], "%Y.%m.%y, %H:%M:%S.%f")
        job.last_update = datetime.strptime(data['last_update'], "%Y.%m.%y, %H:%M:%S.%f")
        job.results = data['results']
        return job

    def save_to_file(self):
        data = {'save_file': FILE_VERSION,
                'job_id': self.job_id,
                'job_status': self.job_status,
                'request_time': self.request_time.strftime("%Y.%m.%y, %H:%M:%S.%f"),
                'last_update': self.last_update.strftime("%Y.%m.%y, %H:%M:%S.%f"),
                'results': self.results}
        with open(self.file_name, 'w') as save_file:
            json.dump(data, save_file, indent=4)

    def update(self, data: dict):
        if not data['requestId'] == self.job_id:
            raise Exception("Missmatch of requestID")
        self.last_update = datetime.now()
        self.job_status = data['status']
        self.results = data['result']
        self.save_to_file()

    def get(self):
        return {'status': self.job_status,
                'requestId': self.job_id,
                'result': self.results}
