from collections import namedtuple
import logging

import requests

CurrentStatus = namedtuple('CurrentStatus', 'status, current_track, current_stream, current_artwork, '
                                            'volume, scanning, '
                                            'current_track_index, maximum_track_index')
# status: str, one of "stopped", "playing", "paused", or None for error
# current_track: dict  (never None)
# volume: int  (or None if status is error)
# scanning: bool (or None if status is error)

ArtworkInfo = namedtuple('ArtworkInfo', 'width height imageuri')
# width: int (or None if there's no artwork)
# height: int (or None if there's no artwork)
# imageuri: str (or None if there's no artwork)

CURRENT_STATUS_ERROR = CurrentStatus(status=None, current_track={}, current_stream=None, current_artwork=None,
                                     volume=None, scanning=None,
                                     current_track_index=None, maximum_track_index=None)


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
            logging.error(f"Unable to connect to {self.base_uri}")
            self.connection_error = True
            return CURRENT_STATUS_ERROR

        self.connection_error = False
        if not response.ok:
            logging.error('Failed to get response from piju: status=%u, error=%s',
                          response.status_code,
                          response.text)
            return CURRENT_STATUS_ERROR

        response_body = response.json()
        if not response_body:
            logging.error("Unable to decode json response body: %s", response.text)
            return CURRENT_STATUS_ERROR

        status = response_body.get('PlayerStatus')
        if not status:
            logging.error("Response did not include status: %s", response.text)
            return CURRENT_STATUS_ERROR

        # TODO: Error handling if status is not a string
        # player status should be one of playing/paused/stopped
        # no fixup should be required

        current_track = response_body.get('CurrentTrack', {})

        current_stream = response_body.get('CurrentStream')

        current_artwork = response_body.get('CurrentArtwork')

        current_volume = 50  # TODO

        scanning = (response_body.get('WorkerStatus', 'Idle').lower() != 'idle')

        current_track_index = response_body.get('CurrentTrackIndex', None)
        maximum_track_index = response_body.get('MaximumTrackIndex', None)

        return CurrentStatus(status, current_track, current_stream, current_artwork,
                             current_volume, scanning,
                             current_track_index, maximum_track_index)

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

        if artwork_uri_path.startswith('/'):
            uri = self.base_uri + artwork_uri_path
        else:
            uri = artwork_uri_path
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
        if not response.ok:
            logging.error("Failed to pause: status=%u, error=%s",
                          response.status_code,
                          response.text)
        return response.ok

    def resume(self):
        uri = self.base_uri + '/player/resume'
        response = requests.post(uri)
        if not response.ok:
            logging.error("Failed to resume: status=%u, error=%s",
                          response.status_code,
                          response.text)
        return response.ok

    def previous(self):
        uri = self.base_uri + '/player/previous'
        response = requests.post(uri)
        if not response.ok:
            logging.error("Failed to skip to previous track: status=%u, error=%s",
                          response.status_code,
                          response.text)
        return response.ok

    def next(self):
        uri = self.base_uri + '/player/next'
        response = requests.post(uri)
        if not response.ok:
            logging.error("Failed to skip to next track: status=%u, error=%s",
                          response.status_code,
                          response.text)
        return response.ok
