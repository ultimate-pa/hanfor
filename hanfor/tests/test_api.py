from unittest import TestCase

import os

import utils
from app import app, api
from reqtransformer import Reqtransformer


class TestApi(TestCase):
    def setUp(self):
        app.config['SESSION_TAG'] = 'test_api'
        app.wsgi_app.prefix = ''
        # Load requirements
        session_folder = os.path.join('test_sessions', app.config['SESSION_TAG'])
        app.config['REVISION_FOLDER'] = session_folder
        app.config['SESSION_VARIABLE_COLLECTION'] = os.path.join(
            app.config['REVISION_FOLDER'],
            'session_variable_collection.pickle'
        )
        self.app = app.test_client()
        if not os.path.exists(session_folder):
            raise NotImplementedError

    def test_api(self):
        return
        result = self.app.get('api/req/get?id=cGW_SysRS_33')

    def test_generate_csv_session(self):
        return
        result = self.app.get('api/tools/csv_file')
