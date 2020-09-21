

class UltimateRun:
    def __init__(self):
        self._status = None
        self._status_update_interval = 5
        self._last_status_update = 0

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value
        self._store()

    def _store(self):
        pass

    def _fetch_api(self):
        pass
