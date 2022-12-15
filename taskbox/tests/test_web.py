import unittest
from unittest import mock
import copy

from moto import mock_dynamodb

from taskbox.index import lambda_handler
from taskbox.utils.tools import LOG
from taskbox.tests import fixture


Fake_event = {
    "requestContext": {
        "http": {
            "method": "GET",
            "path": "/task",
            "protocol": "HTTP/1.1",
            "sourceIp": "112.64.93.19",
            "userAgent": "Mozilla/5.0"
        },
    },
    'body': b'aWQ9VGFza190ZXN0',
}

Fake_context = {}


@mock_dynamodb
class Test_web_tasks(unittest.TestCase):

    def setUp(self):
        self.table = fixture.create_table()

    def tearDown(self):
        self.table.delete()

    def test_get_tasks(self):
        resp = lambda_handler(Fake_event, Fake_context)
        print(resp.get('body'))
        self.assertIn('Task', resp.get('body'))

    def test_quary_single_task(self):
        tmp_event = copy.deepcopy(Fake_event)
        tmp_event['requestContext']['http']['path'] = '/task/Task_foo'
        print(lambda_handler(tmp_event, Fake_context))

    def test_run_cmd(self):
        tmp_event = copy.deepcopy(Fake_event)
        tmp_event['headers'] = {'cmd': 'ls'}
        tmp_event['requestContext']['http']['path'] = '/cmd'
        print(lambda_handler(tmp_event, Fake_context))

    def test_db_query(self):
        tmp_event = copy.deepcopy(Fake_event)
        tmp_event['requestContext']['http'].update(
            {'path': '/db', 'method': 'POST'}
        )
        resp = lambda_handler(tmp_event, Fake_context)
        self.assertIn('Quary db', resp.get('body', None))

    def test_db_putitem(self):
        tmp_event = copy.deepcopy(Fake_event)
        tmp_event['requestContext']['http'].update(
            {'path': '/db', 'method': 'POST'}
        )
        resp = lambda_handler(tmp_event, Fake_context)
        self.assertIn('Quary db', resp.get('body'))

    def test_auth_login_get(self):
        tmp_event = copy.deepcopy(Fake_event)
        tmp_event['requestContext']['http'].update(
            {'path': '/auth/login', 'method': 'GET'}
        )
        resp = lambda_handler(tmp_event, Fake_context)
        self.assertIn('Session will expire after one day.', resp.get('body'))

    def test_auth_login_post(self):
        tmp_event = copy.deepcopy(Fake_event)
        tmp_event['requestContext']['http'].update(
            {'path': '/auth/login', 'method': 'POST'}
        )
        import os
        os.getenv = mock.MagicMock()
        os.getenv.return_value = 'asd'
        resp = lambda_handler(tmp_event, Fake_context)
        self.assertIn('Login failed', resp.get('body'))
