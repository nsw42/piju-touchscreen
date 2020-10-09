import argparse
import logging

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # noqa: E402 # need to call require_version before we can call this

gi.require_version('GLib', '2.0')
from gi.repository import GLib  # noqa: E402 # need to call require_version before we can call this

from jsonrpc import jsonrpc
from mainwindow import MainWindow


def parse_args():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    return args

def get_current_track():
    current_state = jsonrpc("core.playback.get_state")
    current_track = jsonrpc("core.playback.get_current_track")
    current_volume = jsonrpc("core.mixer.get_volume")
    logging.debug('now_playing: %s, %s, %s', current_state, current_track, current_volume)
    return True  # call again
    
def main():
    args = parse_args()
    window = MainWindow()
    window.show_all()
    GLib.timeout_add_seconds(1, get_current_track)
    Gtk.main()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()

