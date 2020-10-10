import os.path

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # noqa: E402 # need to call require_version before we can call this
from gi.repository import GdkPixbuf  # noqa: E402 # need to call require_version before we can call this

import jsonrpc  # noqa: E402 # libraries before local imports


MAX_IMAGE_SIZE = 300


def load_local_image(icon_name, icon_size):
    leafname = icon_name
    if icon_size:
        leafname += '_%u' % icon_size
    leafname += '.png'
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

        self.play_icon = None
        self.pause_icon = None

        self.artwork = Gtk.Image()
        self.artwork.set_hexpand(False)
        self.artwork.set_vexpand(False)
        self.artwork.set_size_request(MAX_IMAGE_SIZE, MAX_IMAGE_SIZE)
        self.artist_label = Gtk.Label()
        self.track_name_label = Gtk.Label()
        self.artist_label.set_hexpand(True)
        self.artist_label.set_vexpand(True)
        self.track_name_label.set_hexpand(True)
        self.track_name_label.set_vexpand(True)
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
        layout_grid.set_margin_start(20)
        layout_grid.set_margin_end(20)

        overlay = Gtk.Overlay()
        overlay.add(layout_grid)

        if show_close_button:
            close_icon = load_local_image('window-close-solid.png', 0)
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

    def get_icon_size(self):
        return 200 if (self.get_allocated_width() > 1000) else 150

    def show_now_playing(self, now_playing):
        self.artist_label.set_label(now_playing.artist_name if now_playing.artist_name else '<Unknown artist>')
        self.track_name_label.set_label(now_playing.track_name if now_playing.track_name else '<Unknown track>')
        if now_playing.image:
            loader = GdkPixbuf.PixbufLoader()
            loader.write(now_playing.image)
            pixbuf = loader.get_pixbuf()
            loader.close()
            if (now_playing.image_width > MAX_IMAGE_SIZE) or (now_playing.image_height > MAX_IMAGE_SIZE):
                if now_playing.image_width > now_playing.image_height:
                    dest_width = MAX_IMAGE_SIZE
                    dest_height = now_playing.image_height * dest_width / now_playing.image_width
                else:
                    dest_height = MAX_IMAGE_SIZE
                    dest_width = now_playing.image_width * dest_height / now_playing.image_height
                pixbuf = pixbuf.scale_simple(MAX_IMAGE_SIZE, MAX_IMAGE_SIZE, GdkPixbuf.InterpType.BILINEAR)
            self.artwork.set_from_pixbuf(pixbuf)
            self.artwork.show()
        else:
            self.artwork.hide()

        if now_playing.current_state == 'playing':
            if not self.pause_icon:
                self.pause_icon = load_local_image('pause-solid', self.get_icon_size())
            self.play_pause_button.set_image(self.pause_icon)
            self.play_pause_action = 'core.playback.pause'
        else:
            if not self.play_icon:
                self.play_icon = load_local_image('play-solid', self.get_icon_size())
            self.play_pause_button.set_image(self.play_icon)
            self.play_pause_action = 'core.playback.play'
