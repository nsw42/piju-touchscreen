from collections import namedtuple
import logging
import unittest
from unittest.mock import patch

import requests

import sys
sys.path.append('..')

import apiclient  # noqa: E402


FakeResponse = namedtuple('FakeResponse', 'ok status_code text json')

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
        FakeResponse(ok=False, status_code=500, text='', json=None)
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

    @patch('apiclient.requests.get', return_value=FakeResponse(ok=False, status_code=500, text='', json=None))
    def test_non_ok_response(self, mock_requests_get):
        client = apiclient.ApiClient('http://address/')
        state = client.get_current_state()
        self.assertEqual(state.status, None)

    @patch('apiclient.requests.get', return_value=FakeResponse(ok=True, status_code=200, text='', json=lambda: None))
    def test_non_json_repsonse(self, mock_requests_get):
        client = apiclient.ApiClient('http://address/')
        state = client.get_current_state()
        self.assertEqual(state.status, None)

    @patch('apiclient.requests.get', return_value=FakeResponse(ok=True, status_code=200, text='', json=lambda: {}))
    def test_json_without_status(self, mock_requests_get):
        client = apiclient.ApiClient('http://address/')
        state = client.get_current_state()
        self.assertEqual(state.status, None)

    @patch('apiclient.requests.get', side_effect=[
        FakeResponse(ok=True, status_code=200, text='', json=lambda: {'PlayerStatus': 'PlayerStatus.INSTANTIATED'}),
        FakeResponse(ok=True, status_code=200, text='', json=lambda: {'PlayerStatus': 'PlayerStatus.IDLE'}),
        FakeResponse(ok=True, status_code=200, text='', json=lambda: {'PlayerStatus': 'Foobar'}),
        FakeResponse(ok=True, status_code=200, text='', json=lambda: {'PlayerStatus': 'PlayerStatus.PLAYING'}),
        FakeResponse(ok=True, status_code=200, text='', json=lambda: {'PlayerStatus': 'PlayerStatus.PAUSED'}),
        FakeResponse(ok=True, status_code=200, text='', json=lambda: {'PlayerStatus': 'Stopped'})
    ])
    def test_status_values(self, mock_requests_get):
        client = apiclient.ApiClient('http://address/')
        self.assertEqual(client.get_current_state().status, "stopped")  # PlayerStatus.INSTANTIATED
        self.assertEqual(client.get_current_state().status, "stopped")  # PlayerStatus.IDLE
        self.assertEqual(client.get_current_state().status, "stopped")  # Foobar
        self.assertEqual(client.get_current_state().status, "playing")  # PlayerStatus.PLAYING
        self.assertEqual(client.get_current_state().status, "paused")  # PlayerStatus.PAUSED
        self.assertEqual(client.get_current_state().status, "stopped")  # PlayerStatus.Stopped


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
        FakeResponse(ok=False, status_code=500, text='', json=None)
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

    @patch('apiclient.requests.get', return_value=FakeResponse(ok=False, status_code=500, text='', json=None))
    def test_non_ok_response(self, mock_requests_get):
        client = apiclient.ApiClient('http://address/')
        info = client.get_artwork_info('/artworkinfo/784')
        self.assertEqual(info.width, None)
        self.assertEqual(info.height, None)
        self.assertEqual(info.imageuri, None)

    @patch('apiclient.requests.get', return_value=FakeResponse(ok=True, status_code=200, text='', json=lambda: None))
    def test_non_json_repsonse(self, mock_requests_get):
        client = apiclient.ApiClient('http://address/')
        info = client.get_artwork_info('/artworkinfo/784')
        self.assertEqual(info.width, None)
        self.assertEqual(info.height, None)
        self.assertEqual(info.imageuri, None)

    @patch('apiclient.requests.get',
           return_value=FakeResponse(ok=True,
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


if __name__ == '__main__':
    unittest.main()
