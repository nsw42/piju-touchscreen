import argparse
import logging
from urllib.parse import urlparse, urlunparse

import requests

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # noqa: E402 # need to call require_version before we can call this

gi.require_version('GLib', '2.0')
from gi.repository import GLib  # noqa: E402 # need to call require_version before we can call this

from jsonrpc import JsonRPC  # noqa: E402  # local imports after libraries
from mainwindow import MainWindow  # noqa: E402  # local imports after libraries
from nowplaying import NowPlaying  # noqa: E402  # local imports after libraries


class ArtworkCache:
    def __init__(self):
        self.current_track_uri = None
        self.current_image_uri = None
        self.current_image = None
        self.current_image_width = None
        self.current_image_height = None

    def update(self, jsonrpc, new_track_uri):
        if new_track_uri == self.current_track_uri:
            # nothing to do
            return

        image_dict = jsonrpc.request("core.library.get_images", {
            "uris": [new_track_uri]
        })
        image_list = image_dict[new_track_uri] if image_dict else None
        image_dict = image_list[0] if image_list else None
        image_uri = jsonrpc.base_uri + image_dict['uri'] if image_dict else None
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


def construct_server_url(host):
    # host is expected to be something like localhost, mopidy:6680
    # but may include a scheme (http://) and even a base path, if
    # that's required for a network proxy reason
    parseresult = urlparse(host)
    if not parseresult.scheme:
        # absence of scheme results in misparsing:
        # 'localhost:6680' is interpreted as path, instead of netloc
        parseresult = urlparse('http://' + host)
    if not parseresult.port:
        parseresult = parseresult._replace(netloc=parseresult.netloc + ':6680')
    parseresult = parseresult._replace(params='', query='', fragment='')
    return urlunparse(parseresult)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', action='store',
                        help="IP address or hostname of mopidy server. "
                             "Can include :portnumber if required. Port defaults to 6680.")
    mainwindowgroup = parser.add_argument_group('Main Window options',
                                                description='Options related to the behaviour of the main window')
    mainwindowgroup.add_argument('--full-screen', action='store_true', dest='full_screen',
                                 help="Go full-screen (default)")
    mainwindowgroup.add_argument('--no-full-screen', action='store_false', dest='full_screen',
                                 help="Do not go full-screen")
    mainwindowgroup.add_argument('--close-button', action='store_true', dest='show_close_button',
                                 help="Show a close button (default)")
    mainwindowgroup.add_argument('--no-close-button', action='store_false', dest='show_close_button',
                                 help="Do not show a close button")
    mainwindowgroup.add_argument('--hide-mouse-pointer', action='store_true', dest='hide_mouse_pointer',
                                 help="Hide the mouse pointer over the window")
    mainwindowgroup.add_argument('--no-hide-mouse-pointer', action='store_false', dest='hide_mouse_pointer',
                                 help="Do not hide the mouse pointer (default)")
    parser.set_defaults(host='localhost',
                        full_screen=True,
                        show_close_button=True,
                        hide_mouse_pointer=False)
    args = parser.parse_args()
    args.host = construct_server_url(args.host)
    return args


def get_current_track(jsonrpc: JsonRPC):
    current_state = jsonrpc.request("core.playback.get_state")  # 'playing', 'paused' or 'stopped'
    current_track_dict = jsonrpc.request("core.playback.get_current_track")
    current_track_uri = current_track_dict['uri'] if current_track_dict else None
    current_artist = current_track_dict['artists'] if current_track_dict else None
    current_artist = current_artist[0] if current_artist else None
    current_artist = current_artist['name'] if current_artist else None
    current_track = current_track_dict['name'] if current_track_dict else None
    current_track_number = current_track_dict['track_no'] if current_track_dict else None
    album_dict = current_track_dict['album'] if current_track_dict else None
    album_num_tracks = album_dict['num_tracks'] if album_dict else None
    current_volume = jsonrpc.request("core.mixer.get_volume")
    current_volume = int(current_volume) if current_volume else 50

    artwork_cache.update(jsonrpc, current_track_uri)

    now_playing = NowPlaying(current_artist,
                             current_track,
                             current_track_number,
                             album_num_tracks,
                             current_state,
                             current_volume,
                             artwork_cache.current_image,
                             artwork_cache.current_image_width,
                             artwork_cache.current_image_height)
    # logging.debug('now_playing: %s', now_playing)
    return now_playing


def update_track_display(jsonrpc: JsonRPC, window: MainWindow):
    now_playing = get_current_track(jsonrpc)
    window.show_now_playing(now_playing)
    return True  # call again


def main():
    args = parse_args()
    jsonrpc = JsonRPC(args.host)
    window = MainWindow(args.full_screen, args.show_close_button, args.hide_mouse_pointer)
    window.show_all()
    GLib.timeout_add_seconds(1, update_track_display, jsonrpc, window)
    Gtk.main()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    main()
