import datetime
import uuid

from utils import generate_req_file_content


class UltimateRun:
    def __init__(self, req_ids, app):
        self.results = None
        self.ultimate_run_id = None
        self._queue_time = datetime.datetime.now()
        self._id = None
        self._api_job_id = None
        self._status = None
        self._req_ids = req_ids
        self._req_file_content = None
        self._meta_infos = dict()
        self.generate_req_file_content(app)

    @property
    def id(self):
        return self._id

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def meta_infos(self):
        return self._meta_infos

    @meta_infos.setter
    def meta_infos(self, value):
        self._meta_infos = value

    def _fetch_api(self):
        pass

    def queue(self, app):
        self._queue_time = datetime.datetime.now()
        self._id = str(uuid.uuid1())
        if 'name' not in self._meta_infos:
            self._meta_infos['name'] = self._id

    def generate_req_file_content(self, app):
        self._req_file_content = generate_req_file_content(app, self._req_ids)

    def to_dict(self):
        return {
            'id': self.id,
            'queued_human': self._queue_time.strftime("%d %b %Y - %H:%M:%S"),
            'status': self._status,
            'req_file_content': self._req_file_content,
            'ultimate_run_id': self.ultimate_run_id,
            'results': self.results,
            'meta_infos': self._meta_infos
        }
