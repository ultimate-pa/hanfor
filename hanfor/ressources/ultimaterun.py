import datetime
import uuid

from utils import generate_req_file_content


class UltimateRun:
    def __init__(self, req_ids, app):
        self._queue_time = datetime.datetime.now()
        self._id = None
        self._api_job_id = None
        self._status = None
        self._req_ids = req_ids
        self._req_file_content = None
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

    def _fetch_api(self):
        pass

    def queue(self):
        self._queue_time = datetime.datetime.now()
        self._id = uuid.uuid1()

    def generate_req_file_content(self, app):
        self._req_file_content = generate_req_file_content(app, self._req_ids)

    def to_dict(self):
        return {
            'id': self.id,
            'queued_human': self._queue_time.strftime("%d %b %Y - %H:%M:%S"),
            'status': self._status,
            'req_file_content': self._req_file_content
        }
