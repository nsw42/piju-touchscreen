import argparse
import logging
import pathlib
import threading
import time
from urllib.parse import urlparse, urlunparse

import gi
gi.require_version('Gtk', '3.0')
# pylint: disable=wrong-import-position,wrong-import-order
# (need to call require_version before we can import the other gi libraries, and we want
# third-party libraries before local libraries)
from gi.repository import Gtk  # noqa: E402 # need to call require_version before we can call this

gi.require_version('GLib', '2.0')
from gi.repository import GLib  # noqa: E402 # need to call require_version before we can call this

from apiclient import ApiClient  # noqa: E402  # local imports after libraries
from artworkcache import ArtworkCache  # noqa: E402  # local imports after libraries
from mainwindow import MainWindow  # noqa: E402  # local imports after libraries
from nowplaying import NowPlaying  # noqa: E402  # local imports after libraries
import screenblankmgr  # noqa: E402  # local imports after libraries
# pylint: enable=wrong-import-position,wrong-import-order

artwork_cache = ArtworkCache()


def construct_server_url(host):
    # host is expected to be something like localhost, mopidy:5000
    # but may include a scheme (http://) and even a base path, if
    # that's required for a network proxy reason
    parseresult = urlparse(host)
    if not parseresult.scheme:
        # absence of scheme results in misparsing:
        # 'localhost:5000' is interpreted as path, instead of netloc
        parseresult = urlparse('http://' + host)
    if not parseresult.port:
        parseresult = parseresult._replace(netloc=parseresult.netloc + ':5000')
    parseresult = parseresult._replace(params='', query='', fragment='')
    return urlunparse(parseresult)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help="Enable debug logging")
    parser.add_argument('--logfile', action='store', type=pathlib.Path,
                        help="Write logging to LOGFILE")
    parser.add_argument('--host', action='store',
                        help="IP address or hostname of mopidy server. "
                             "Can include :portnumber if required. Port defaults to 5000.")
    mainwindowgroup = parser.add_argument_group('Main Window options',
                                                description='Options related to the behaviour of the main window')
    mainwindowgroup.add_argument('--full-screen', action='store_true', dest='full_screen',
                                 help="Go full-screen (default)")
    mainwindowgroup.add_argument('--no-full-screen', action='store_false', dest='full_screen',
                                 help="Do not go full-screen")
    mainwindowgroup.add_argument('--fixed-layout', action='store_true', dest='fixed_layout',
                                 help="Use a fixed layout to position controls")
    mainwindowgroup.add_argument('--no-fixed-layout', action='store_false', dest='fixed_layout',
                                 help="Use a dynamically resized layout for controls")
    mainwindowgroup.add_argument('--close-button', action='store_true', dest='show_close_button',
                                 help="Show a close button (default)")
    mainwindowgroup.add_argument('--no-close-button', action='store_false', dest='show_close_button',
                                 help="Do not show a close button")
    mainwindowgroup.add_argument('--hide-mouse-pointer', action='store_true', dest='hide_mouse_pointer',
                                 help="Hide the mouse pointer over the window")
    mainwindowgroup.add_argument('--no-hide-mouse-pointer', action='store_false', dest='hide_mouse_pointer',
                                 help="Do not hide the mouse pointer (default)")
    parser.add_argument('--screenblanker-profile', action='store', choices=screenblankmgr.profiles.keys(),
                        help="Actively manage the screen blank based on playback state")
    parser.set_defaults(debug=False,
                        logfile=None,
                        host='localhost',
                        full_screen=True,
                        fixed_layout=True,
                        show_close_button=True,
                        hide_mouse_pointer=False,
                        screenblanker_profile='none')
    args = parser.parse_args()
    args.host = construct_server_url(args.host)
    return args


def get_current_track(apiclient: ApiClient, now_playing: NowPlaying):
    status = apiclient.get_current_state()

    current_track = status.current_track
    artwork_cache.update(apiclient, status.current_artwork)

    now_playing.refresh_countdown = 5
    now_playing.is_track = bool(current_track)
    now_playing.artist_name = current_track.get('artist')
    now_playing.track_name = current_track.get('title')
    now_playing.track_number = status.current_track_index
    now_playing.album_tracks = status.maximum_track_index
    now_playing.stream_name = status.current_stream
    now_playing.current_state = status.status
    now_playing.current_volume = status.volume
    now_playing.image_uri = artwork_cache.current_image_uri
    now_playing.image = artwork_cache.current_image

    now_playing.scanning_active = status.scanning

    return now_playing


def update_track_display(apiclient: ApiClient, window: MainWindow, screenmgr: screenblankmgr.ScreenBlankMgr):
    def update_window(now_playing):
        window.show_now_playing(apiclient.connection_error, now_playing)
        screenmgr.set_state(now_playing.current_state)

    now_playing = NowPlaying()
    while True:
        get_current_track(apiclient, now_playing)
        logging.debug(now_playing)
        GLib.idle_add(update_window, now_playing)
        time.sleep(1)


def main():
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.ERROR,
                        filename=args.logfile)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    apiclient = ApiClient(args.host)
    window = MainWindow(apiclient, args.full_screen, args.fixed_layout, args.show_close_button, args.hide_mouse_pointer)
    window.show_all()
    screenmgr = screenblankmgr.ScreenBlankMgr(screenblankmgr.profiles[args.screenblanker_profile])

    thread = threading.Thread(target=update_track_display, args=(apiclient, window, screenmgr), daemon=True)
    thread.start()

    Gtk.main()


if __name__ == '__main__':
    main()
