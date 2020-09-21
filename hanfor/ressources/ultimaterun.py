import uuid


class UltimateRun:
    def __init__(self, req_ids):
        self._id = None
        self._status = None
        self._req_ids = req_ids

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
        self._id = uuid.uuid1()

    def to_dict(self):
        return {
            'id': self.id
        }
