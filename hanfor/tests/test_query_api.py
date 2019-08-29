import json

from tests.mock_hanfor import MockHanfor
from unittest import TestCase


class TestQueryAPI(TestCase):
    def setUp(self) -> None:
        self.mock_hanfor = MockHanfor(
            session_tags=['simple'],
            test_session_source='test_query_api'
        )
        self.mock_hanfor.setUp()

    def tearDown(self) -> None:
        self.mock_hanfor.tearDown()

    def test_new_query(self):
        self.mock_hanfor.startup_hanfor('simple.csv', 'simple', [])
        # We expect there is no stored query.
        initial_query = self.mock_hanfor.app.get('api/query').json['data']
        self.assertEqual(initial_query, dict())

        # Create a query
        simple_query = self.mock_hanfor.app.post(
            '/api/query',
            json={'name': 'MyQuery', 'query': ':DATA_TARGET:`Tags`has_formalization'}
        ).json['data']
        self.assertDictEqual(
            simple_query,
            {
                'query': ':DATA_TARGET:`Tags`has_formalization',
                'hits': 1,
                'result': ['SysRS FooXY_42'],
                'name': 'MyQuery'
            }
        )

        # Create another query
        simple_query = self.mock_hanfor.app.post(
            '/api/query',
            json={'name': 'MyQuery_no_2', 'query': ''}
        ).json['data']
        self.assertListEqual(
            sorted(simple_query['result']),
            sorted(['SysRS FooXY_42', 'SysRS FooXY_91'])
        )
        print(simple_query)
