from collections import namedtuple
import logging

import requests

CurrentStatus = namedtuple('CurrentStatus', 'status, current_track, volume')
# status: str, one of "stopped", "playing", "paused"
# current_track: dict  (never None)
# volume: int  (never None)

ArtworkInfo = namedtuple('ArtworkInfo', 'width height imageuri')
# width: int or None
# height: int or None
# imageuri: str or None


class ApiClient:
    def __init__(self, base_uri):
        if base_uri.endswith('/'):
            base_uri = base_uri[:-1]
        self.base_uri = base_uri
        self.connection_error = False

    def get_current_state(self) -> CurrentStatus:
        try:
            response = requests.get(self.base_uri + '/')
        except requests.exceptions.ConnectionError:
            logging.error("Unable to connect to piju")
            self.connection_error = True
            return CurrentStatus(status=None, current_track={}, volume=None)

        self.connection_error = False
        if not response.ok:
            logging.error('Failed to get response from piju: status=%u, error=%s',
                          response.status_code,
                          response.text)
            return CurrentStatus(status=None, current_track={}, volume=None)

        response_body = response.json()
        if not response_body:
            logging.error("Unable to decode json response body: %s", response.text)
            return CurrentStatus(status=None, current_track={}, volume=None)

        status = response_body.get('PlayerStatus')
        if not status:
            logging.error("Response did not include status: %s", response.text)
            return CurrentStatus(status=None, current_track={}, volume=None)

        # TODO: Error handling if status is not a string

        status = status.lower()
        if '.' in status:
            status = status.rsplit('.', 1)[-1]
        if status not in ('playing', 'paused'):
            status = 'stopped'

        current_track = response_body.get('CurrentTrack', {})

        current_volume = 50  # TODO

        return CurrentStatus(status, current_track, current_volume)

    def get_artwork_info(self, info_uri_path):
        if info_uri_path is None:
            return ArtworkInfo(None, None, None)

        assert info_uri_path.startswith('/')
        uri = self.base_uri + info_uri_path
        try:
            response = requests.get(uri)
        except requests.exceptions.ConnectionError:
            logging.error("Unable to connect to piju")
            self.connection_error = True
            return ArtworkInfo(None, None, None)

        self.connection_error = False
        if not response.ok:
            logging.error('Failed to get artwork info from piju: status=%u, error=%s',
                          response.status_code,
                          response.text)
            return ArtworkInfo(None, None, None)

        response_body = response.json()
        if not response_body:
            logging.error("Unable to decode json response body: %s", response.text)
            return ArtworkInfo(None, None, None)

        return ArtworkInfo(response_body.get('width'),
                           response_body.get('height'),
                           response_body.get('image'))

    def get_artwork(self, artwork_uri_path):
        if artwork_uri_path is None:
            return None

        assert artwork_uri_path.startswith('/')
        uri = self.base_uri + artwork_uri_path
        try:
            response = requests.get(uri)
        except requests.exceptions.ConnectionError:
            logging.error("Unable to connect to piju")
            self.connection_error = True
            return None

        self.connection_error = False
        if not response.ok:
            logging.error("Failed to get artwork %s from piju: status=%u, error=%s",
                          uri,
                          response.status_code,
                          response.text)
            return None

        return response.content

    def pause(self):
        uri = self.base_uri + '/player/pause'
        response = requests.post(uri)
        return response.ok

    def resume(self):
        uri = self.base_uri + '/player/resume'
        response = requests.post(uri)
        return response.ok

    def previous(self):
        uri = self.base_uri + '/player/previous'
        response = requests.post(uri)
        return response.ok

    def next(self):
        uri = self.base_uri + '/player/next'
        response = requests.post(uri)
        return response.ok
