import pickle
import os
import requests
from requests import HTTPError

from ressources import Ressource
from ressources.ultimaterun import UltimateRun


class UltimateAPI(Ressource):
    def __init__(self, app, request, ressource):
        super().__init__(app, request)
        self._runs = dict()
        self._ressource = ressource
        self._storage_path = os.path.join(app.config['SESSION_FOLDER'], 'ultimate_runs.pickle')
        self.load_runs()

    def GET(self):
        if self._ressource == 'version':
            if self.ping_ultimate_api():
                self.fetch_ultimate_api_version()
                self.response.data = {'ultimate_api_version': ''}
            else:
                self.response.success = False
        else:
            self.response.data = [run.to_dict() for run in self._runs.values()]

    def POST(self):
        self.add_new_run()
        self.store_runs()

    def DELETE(self):
        pass

    def add_new_run(self):
        ultimate_run = UltimateRun(self.request.get_json())
        ultimate_run.queue()
        self._runs[ultimate_run.id] = ultimate_run

    def load_runs(self):
        if not os.path.isfile(self._storage_path) or not os.path.getsize(self._storage_path) > 0:
            return

        with open(self._storage_path, mode='rb') as f:
            self._runs = pickle.load(f)

    def store_runs(self):
        with open(self._storage_path, mode='wb') as out_file:
            pickle.dump(self._runs, out_file)

    def fetch_ultimate_api_version(self):
        response = requests.get(self.app.config['ULTIMATE_API_URL'] + '/api/version')
        print(response)

    def ping_ultimate_api(self) -> bool:
        success = True
        try:
            requests.get(self.app.config['ULTIMATE_API_URL'] + '/api').raise_for_status()
        except HTTPError:
            success = False

        return success
