import argparse
import logging

import requests

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # noqa: E402 # need to call require_version before we can call this

gi.require_version('GLib', '2.0')
from gi.repository import GLib  # noqa: E402 # need to call require_version before we can call this

import jsonrpc  # noqa: E402  # local imports after libraries
from mainwindow import MainWindow  # noqa: E402  # local imports after libraries
from nowplaying import NowPlaying  # noqa: E402  # local imports after libraries


class ArtworkCache:
    def __init__(self):
        self.current_track_uri = None
        self.current_image_uri = None
        self.current_image = None
        self.current_image_width = None
        self.current_image_height = None

    def update(self, new_track_uri):
        if new_track_uri == self.current_track_uri:
            # nothing to do
            return

        image_dict = jsonrpc.jsonrpc("core.library.get_images", {
            "uris": [new_track_uri]
        })
        image_list = image_dict[new_track_uri] if image_dict else None
        image_dict = image_list[0] if image_dict else None
        image_uri = jsonrpc.BASE_URI + image_dict['uri'] if image_dict else None
        image_width = image_dict['width'] if image_dict else None
        image_height = image_dict['height'] if image_dict else None

        if image_uri == self.current_image_uri:
            # nothing to do
            return

        # if we get here, we need to update our cache
        if image_uri:
            response = requests.get(image_uri, allow_redirects=True)
            ok = response.ok
        else:
            ok = False

        if ok:
            self.current_image = response.content
            self.current_track_uri = new_track_uri
            self.current_image_uri = image_uri
        else:
            self.current_image = None
            self.current_track_uri = None
            self.current_image_uri = None
        self.current_image_width = image_width
        self.current_image_height = image_height


artwork_cache = ArtworkCache()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--close-button', action='store_true', dest='show_close_button',
                        help="Do not show a close button")
    parser.add_argument('--no-close-button', action='store_false', dest='show_close_button',
                        help="Do not show a close button")
    parser.set_defaults(show_close_button=True)
    args = parser.parse_args()
    return args


def get_current_track():
    current_state = jsonrpc.jsonrpc("core.playback.get_state")  # 'playing' or 'paused'
    current_track_dict = jsonrpc.jsonrpc("core.playback.get_current_track")
    current_track_uri = current_track_dict['uri'] if current_track_dict else None
    current_artist = current_track_dict['artists'] if current_track_dict else None
    current_artist = current_artist[0] if current_artist else None
    current_artist = current_artist['name'] if current_artist else None
    current_track = current_track_dict['name'] if current_track_dict else None
    current_volume = jsonrpc.jsonrpc("core.mixer.get_volume")
    current_volume = int(current_volume) if current_volume else 50

    artwork_cache.update(current_track_uri)

    now_playing = NowPlaying(current_artist,
                             current_track,
                             current_state,
                             current_volume,
                             artwork_cache.current_image)
    # logging.debug('now_playing: %s', now_playing)
    return now_playing


def update_track_display(window):
    now_playing = get_current_track()
    window.show_now_playing(now_playing)
    return True  # call again


def main():
    args = parse_args()
    window = MainWindow(args.show_close_button)
    window.show_all()
    GLib.timeout_add_seconds(1, update_track_display, window)
    Gtk.main()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
