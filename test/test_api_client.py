from collections import namedtuple
import logging
import unittest
from unittest.mock import patch

import requests

import sys
sys.path.append('..')

import apiclient  # noqa: E402


FakeTextResponse = namedtuple('FakeTextResponse', 'ok status_code text json')
FakeBinaryResponse = namedtuple('FakeBinaryResponse', 'ok status_code text content')

logging.disable(logging.CRITICAL)  # disable logging from the apiclient code


class TestGetCurrentState(unittest.TestCase):
    @patch('apiclient.requests.get', side_effect=requests.exceptions.ConnectionError)
    def test_connection_error_sets_flag(self, mock_requests_get):
        client = apiclient.ApiClient('http://address/')
        self.assertFalse(client.connection_error)
        state = client.get_current_state()
        self.assertEqual(state.status, None)
        self.assertTrue(client.connection_error)

    @patch('apiclient.requests.get', side_effect=[
        requests.exceptions.ConnectionError,
        FakeTextResponse(ok=False, status_code=500, text='', json=None)
    ])
    def test_successful_connection_clears_flag(self, mock_requests_get):
        client = apiclient.ApiClient('http://address/')
        self.assertFalse(client.connection_error)

        # first call: sets flag
        state = client.get_current_state()
        self.assertEqual(state.status, None)
        self.assertTrue(client.connection_error)

        # second call: clears flag
        state = client.get_current_state()
        self.assertFalse(client.connection_error)

    @patch('apiclient.requests.get',
           return_value=FakeTextResponse(ok=False, status_code=500, text='', json=None))
    def test_non_ok_response(self, mock_requests_get):
        client = apiclient.ApiClient('http://address/')
        state = client.get_current_state()
        self.assertEqual(state.status, None)

    @patch('apiclient.requests.get',
           return_value=FakeTextResponse(ok=True, status_code=200, text='', json=lambda: None))
    def test_non_json_repsonse(self, mock_requests_get):
        client = apiclient.ApiClient('http://address/')
        state = client.get_current_state()
        self.assertEqual(state.status, None)

    @patch('apiclient.requests.get',
           return_value=FakeTextResponse(ok=True, status_code=200, text='', json=lambda: {}))
    def test_json_without_status(self, mock_requests_get):
        client = apiclient.ApiClient('http://address/')
        state = client.get_current_state()
        self.assertEqual(state.status, None)

    @patch('apiclient.requests.get', side_effect=[
        FakeTextResponse(ok=True, status_code=200, text='', json=lambda: {'PlayerStatus': 'stopped'}),
        FakeTextResponse(ok=True, status_code=200, text='', json=lambda: {'PlayerStatus': 'playing'}),
        FakeTextResponse(ok=True, status_code=200, text='', json=lambda: {'PlayerStatus': 'paused'}),
    ])
    def test_status_values(self, mock_requests_get):
        client = apiclient.ApiClient('http://address/')
        self.assertEqual(client.get_current_state().status, "stopped")
        self.assertEqual(client.get_current_state().status, "playing")
        self.assertEqual(client.get_current_state().status, "paused")


class TestGetArtworkInfo(unittest.TestCase):
    @patch('apiclient.requests.get', side_effect=requests.exceptions.ConnectionError)
    def test_connection_error_sets_flag(self, mock_requests_get):
        client = apiclient.ApiClient('http://address/')
        self.assertFalse(client.connection_error)
        info = client.get_artwork_info('/artworkinfo/27')
        self.assertEqual(info.width, None)
        self.assertEqual(info.height, None)
        self.assertEqual(info.imageuri, None)
        self.assertTrue(client.connection_error)

    @patch('apiclient.requests.get', side_effect=[
        requests.exceptions.ConnectionError,
        FakeTextResponse(ok=False, status_code=500, text='', json=None)
    ])
    def test_successful_connection_clears_flag(self, mock_requests_get):
        client = apiclient.ApiClient('http://address/')
        self.assertFalse(client.connection_error)

        # first call: sets flag
        state = client.get_artwork_info('/artworkinfo/27')
        self.assertEqual(state.width, None)
        self.assertTrue(client.connection_error)

        # second call: clears flag
        state = client.get_artwork_info('/artworkinfo/27')
        self.assertFalse(client.connection_error)

    @patch('apiclient.requests.get',
           return_value=FakeTextResponse(ok=False, status_code=500, text='', json=None))
    def test_non_ok_response(self, mock_requests_get):
        client = apiclient.ApiClient('http://address/')
        info = client.get_artwork_info('/artworkinfo/784')
        self.assertEqual(info.width, None)
        self.assertEqual(info.height, None)
        self.assertEqual(info.imageuri, None)

    @patch('apiclient.requests.get',
           return_value=FakeTextResponse(ok=True, status_code=200, text='', json=lambda: None))
    def test_non_json_repsonse(self, mock_requests_get):
        client = apiclient.ApiClient('http://address/')
        info = client.get_artwork_info('/artworkinfo/784')
        self.assertEqual(info.width, None)
        self.assertEqual(info.height, None)
        self.assertEqual(info.imageuri, None)

    @patch('apiclient.requests.get',
           return_value=FakeTextResponse(ok=True,
                                         status_code=200,
                                         text='',
                                         json=lambda: {"width": 44, "height": 55, "image": "/artwork/12"})
           )
    def test_status_values(self, mock_requests_get):
        client = apiclient.ApiClient('http://address/')
        info = client.get_artwork_info('/artworkinfo/12')
        self.assertEqual(info.width, 44)
        self.assertEqual(info.height, 55)
        self.assertEqual(info.imageuri, "/artwork/12")


class TestGetArtwork(unittest.TestCase):
    def test_get_none(self):
        client = apiclient.ApiClient('http://address/')
        artwork = client.get_artwork(None)
        self.assertEqual(artwork, None)

    @patch('apiclient.requests.get', side_effect=requests.exceptions.ConnectionError)
    def test_connection_error_returns_none_and_sets_flag(self, mock_requests_get):
        client = apiclient.ApiClient('http://address/')
        self.assertFalse(client.connection_error)
        artwork = client.get_artwork('/artwork/123')
        self.assertEqual(artwork, None)
        self.assertTrue(client.connection_error)

    @patch('apiclient.requests.get', side_effect=[
        requests.exceptions.ConnectionError,
        FakeBinaryResponse(ok=False, status_code=500, text='', content=None)
    ])
    def test_successful_connection_clears_flag(self, mock_requests_get):
        client = apiclient.ApiClient('http://address/')
        self.assertFalse(client.connection_error)

        # first call: sets flag
        artwork = client.get_artwork('/artwork/123')
        self.assertEqual(artwork, None)
        self.assertTrue(client.connection_error)

        # second call: clears flag
        artwork = client.get_artwork('/artwork/123')
        self.assertFalse(client.connection_error)

    @patch('apiclient.requests.get',
           return_value=FakeBinaryResponse(ok=False, status_code=500, text='', content=None))
    def test_non_ok_response(self, mock_requests_get):
        client = apiclient.ApiClient('http://address/')
        artwork = client.get_artwork('/artwork/123')
        self.assertEqual(artwork, None)

    @patch('apiclient.requests.get',
           return_value=FakeBinaryResponse(ok=True, status_code=200, text='', content='MyArtworkHere'))
    def test_ok_response(self, mock_requests_get):
        client = apiclient.ApiClient('http://address/')
        artwork = client.get_artwork('/artwork/123')
        self.assertEqual(artwork, 'MyArtworkHere')


if __name__ == '__main__':
    unittest.main()
