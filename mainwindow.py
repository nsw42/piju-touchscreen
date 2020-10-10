import os.path

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # noqa: E402 # need to call require_version before we can call this
from gi.repository import GdkPixbuf  # noqa: E402 # need to call require_version before we can call this

import jsonrpc  # noqa: E402 # libraries before local imports


def load_local_image(leafname):
    icon_filename = os.path.join(os.path.dirname(__file__), leafname)
    return Gtk.Image.new_from_file(icon_filename)


class MainWindow(Gtk.ApplicationWindow):
    """
    Main application window
    """

    def __init__(self, show_close_button):
        Gtk.Window.__init__(self, title="PiJu")
        self.connect("destroy", self.on_quit)
        self.fullscreen()

        self.play_icon = load_local_image('play-solid.png')
        self.pause_icon = load_local_image('pause-solid.png')

        self.artwork = Gtk.Image()
        self.artist_label = Gtk.Label()
        self.track_name_label = Gtk.Label()
        self.artist_label.set_hexpand(True)
        self.track_name_label.set_hexpand(True)
        self.play_pause_button = Gtk.Button()
        self.play_pause_button.set_halign(Gtk.Align.END)
        self.play_pause_button.set_valign(Gtk.Align.CENTER)

        self.play_pause_button.connect('clicked', self.on_play_pause)

        self.play_pause_action = None

        # image     track      play/pause
        #  ..       artist
        layout_grid = Gtk.Grid()
        layout_grid.attach(self.artwork, left=0, top=0, width=1, height=2)
        layout_grid.attach(self.track_name_label, left=1, top=0, width=1, height=1)
        layout_grid.attach(self.artist_label, left=1, top=1, width=1, height=1)
        layout_grid.attach(self.play_pause_button, left=2, top=0, width=1, height=2)

        overlay = Gtk.Overlay()
        overlay.add(layout_grid)

        if show_close_button:
            close_icon = load_local_image('window-close-solid.png')
            close = Gtk.Button()
            close.set_image(close_icon)
            close.connect('clicked', self.on_quit)
            top_right = Gtk.Alignment.new(1, 0, 0, 0)
            top_right.add(close)
            overlay.add_overlay(top_right)

        self.add(overlay)

    def on_play_pause(self, *args):
        if self.play_pause_action:
            jsonrpc.jsonrpc(self.play_pause_action)

    def on_quit(self, *args):
        Gtk.main_quit()

    def show_now_playing(self, now_playing):
        self.artist_label.set_label(now_playing.artist_name)
        self.track_name_label.set_label(now_playing.track_name)
        if now_playing.image:
            loader = GdkPixbuf.PixbufLoader()
            loader.write(now_playing.image)
            pixbuf = loader.get_pixbuf()
            loader.close()
            self.artwork.set_from_pixbuf(pixbuf)
            self.artwork.show()
        else:
            self.artwork.hide()
        if now_playing.current_state == 'playing':
            self.play_pause_button.set_image(self.pause_icon)
            self.play_pause_action = 'core.playback.pause'
        else:
            self.play_pause_button.set_image(self.play_icon)
            self.play_pause_action = 'core.playback.play'