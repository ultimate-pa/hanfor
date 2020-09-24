import logging
import pickle
import os
import requests

from ressources import Ressource
from ressources.ultimaterun import UltimateRun


class UltimateAPI(Ressource):
    def __init__(self, app, request, ressource):
        super().__init__(app, request)
        self._runs = dict()
        self._ressource = ressource
        self._storage_path = os.path.join(app.config['SESSION_FOLDER'], 'ultimate_runs.pickle')
        self._load_runs()

    def GET(self):
        tasks = {
            'get_version': self.get_version,
            'get_runs': self.get_runs
        }

        task = tasks.get(self._get_task(), self.task_not_supported)
        task()

    def POST(self):
        tasks = {
            'add_new_run': self.add_new_run
        }

        task = tasks.get(self._get_task(), self.task_not_supported)
        task()

    def DELETE(self):
        pass

    def task_not_supported(self):
        self.response.success = False

    def get_run(self):
        self.response.data = [run.to_dict() for run in self._runs.values()]

    def get_runs(self):
        self.response.data = [run.to_dict() for run in self._runs.values()]

    def get_version(self):
        if self.ping_ultimate_api():
            self.fetch_ultimate_api_version()
            self.response.data = {'ultimate_api_version': ''}
        else:
            self.response.success = False
            self.response.errormsg = 'Ultimate API unreachable.'

    def add_new_run(self):
        if self.ping_ultimate_api():
            ultimate_run = UltimateRun(self.request.get_json()['req_ids'], self.app)
            ultimate_run.queue()
            self._runs[ultimate_run.id] = ultimate_run
            self._store_runs()
        else:
            self.response.success = False
            self.response.errormsg = 'Ultimate API not reachable.'


    def fetch_ultimate_api_version(self):
        version = 'Unknown'
        try:
            version = requests.get(self.app.config['ULTIMATE_API_URL'] + '/api/version').json()['ultimate_version']
        except Exception as e:
            logging.debug(f'Could not fetch API version: {e}')

        return version

    def ping_ultimate_api(self) -> bool:
        try:
            requests.get(self.app.config['ULTIMATE_API_URL'] + '/api').raise_for_status()
        except Exception as e:
            logging.debug(f'Could not ping ultimate API: {e}')
            return False

        return True

    def _load_runs(self):
        if not os.path.isfile(self._storage_path) or not os.path.getsize(self._storage_path) > 0:
            return

        with open(self._storage_path, mode='rb') as f:
            self._runs = pickle.load(f)

    def _store_runs(self):
        with open(self._storage_path, mode='wb') as out_file:
            pickle.dump(self._runs, out_file)

    def _get_task(self):
        task = 'unknown'
        if self._ressource == 'version':
            task = 'get_version'
        elif self._ressource == 'runs':
            task = 'get_runs'
        elif self._ressource == 'run':
            if self.request.is_json:
                task = self.request.get_json()['task']

        return task
