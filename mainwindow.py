import os.path

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # noqa: E402 # need to call require_version before we can call this
from gi.repository import Gdk  # noqa: E402 # need to call require_version before we can call this
from gi.repository import GdkPixbuf  # noqa: E402 # need to call require_version before we can call this
gi.require_version('Pango', '1.0')
from gi.repository import Pango  # noqa: E402 # need to call require_version before we can call this

from jsonrpc import JsonRPC  # noqa: E402 # libraries before local imports


MAX_IMAGE_SIZE = 300


def load_local_image(icon_name, icon_size):
    leafname = icon_name
    if icon_size:
        leafname += '_%u' % icon_size
    leafname += '.png'
    icon_filename = os.path.join(os.path.dirname(__file__), leafname)
    assert os.path.exists(icon_filename)
    return Gtk.Image.new_from_file(icon_filename)


def set_font(label, weight, font_size, colour):
    context = label.create_pango_context()
    font_desc = context.get_font_description()
    font_desc.set_family('sans')
    font_desc.set_weight(weight)
    font_desc.set_size(font_size * Pango.SCALE)
    label.override_font(font_desc)
    label.modify_fg(Gtk.StateType.NORMAL, colour)


class MainWindow(Gtk.ApplicationWindow):
    """
    Main application window
    """

    def __init__(self, jsonrpc: JsonRPC, full_screen, show_close_button, hide_mouse_pointer):
        Gtk.Window.__init__(self, title="PiJu")
        self.connect("destroy", self.on_quit)
        self.jsonrpc = jsonrpc
        if full_screen:
            self.fullscreen()
        else:
            self.set_size_request(800, 480)

        self.play_icon = None
        self.pause_icon = None

        self.artwork = Gtk.Image()
        self.artwork.set_hexpand(False)
        self.artwork.set_vexpand(False)
        self.artwork.set_size_request(MAX_IMAGE_SIZE, MAX_IMAGE_SIZE)
        self.artist_label = Gtk.Label()
        self.track_name_label = Gtk.Label()
        for label in (self.artist_label, self.track_name_label):
            label.set_hexpand(True)
            label.set_vexpand(True)
            label.set_line_wrap(True)
            label.set_justify(Gtk.Justification.LEFT)
        self.prev_button = Gtk.Button()
        self.prev_button.connect('clicked', self.on_previous)
        self.play_pause_button = Gtk.Button()
        self.next_button = Gtk.Button()
        self.next_button.connect('clicked', self.on_next)
        self.prev_button.set_halign(Gtk.Align.START)
        self.play_pause_button.set_halign(Gtk.Align.CENTER)
        self.next_button.set_halign(Gtk.Align.END)
        for button in (self.prev_button, self.play_pause_button, self.next_button):
            button.set_valign(Gtk.Align.CENTER)

        set_font(self.track_name_label, Pango.Weight.BOLD, 32, Gdk.Color.from_floats(0.0, 0.0, 0.0))
        set_font(self.artist_label, Pango.Weight.NORMAL, 24, Gdk.Color.from_floats(0.3, 0.3, 0.3))

        self.play_pause_button.connect('clicked', self.on_play_pause)

        self.play_pause_action = None

        # image          track
        #  ..            artist
        #  prev  play/pause   next

        track_artist_container = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
        track_artist_container.pack_start(self.track_name_label, expand=True, fill=True, padding=10)
        track_artist_container.pack_start(self.artist_label, expand=True, fill=True, padding=10)

        top_row_container = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 10)
        top_row_container.pack_start(self.artwork, expand=False, fill=False, padding=10)
        top_row_container.pack_start(track_artist_container, expand=True, fill=True, padding=10)
        top_row_container.set_valign(Gtk.Align.START)

        bottom_row_container = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 10)
        bottom_row_container.pack_start(self.prev_button, expand=True, fill=False, padding=10)
        bottom_row_container.pack_start(self.play_pause_button, expand=True, fill=False, padding=10)
        bottom_row_container.pack_start(self.next_button, expand=True, fill=False, padding=10)
        bottom_row_container.set_valign(Gtk.Align.END)

        child_container = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
        child_container.pack_start(top_row_container, expand=True, fill=True, padding=10)
        child_container.pack_start(bottom_row_container, expand=True, fill=False, padding=10)

        if show_close_button:

            overlay = Gtk.Overlay()
            overlay.add(child_container)

            close_icon = load_local_image('window-close-solid', 0)
            close = Gtk.Button()
            close.set_image(close_icon)
            close.connect('clicked', self.on_quit)
            top_right = Gtk.Alignment.new(1, 0, 0, 0)
            top_right.add(close)
            overlay.add_overlay(top_right)
            overlay.set_overlay_pass_through(top_right, True)

            self.add(overlay)

        else:
            self.add(child_container)

        self.hide_mouse_pointer = hide_mouse_pointer
        self.connect('realize', self.on_realized)

    def on_next(self, *args):
        self.jsonrpc.request('core.playback.next')

    def on_play_pause(self, *args):
        if self.play_pause_action:
            self.jsonrpc.request(self.play_pause_action)

    def on_previous(self, *args):
        self.jsonrpc.request('core.playback.previous')

    def on_quit(self, *args):
        Gtk.main_quit()

    def on_realized(self, *args):
        if self.hide_mouse_pointer:
            self.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.BLANK_CURSOR))
        icon_size = 200 if (self.get_allocated_width() > 1000) else 100
        self.pause_icon = load_local_image('pause-solid', icon_size)
        self.play_icon = load_local_image('play-solid', icon_size)
        prev_icon = load_local_image('backward-solid', icon_size)
        self.prev_button.set_image(prev_icon)
        next_icon = load_local_image('forward-solid', icon_size)
        self.next_button.set_image(next_icon)

    def show_now_playing(self, connection_error, now_playing):
        if connection_error:
            self.artist_label.set_label("Connection error")
            self.track_name_label.set_label("")
            self.artwork.hide()
            self.play_pause_button.set_image(self.play_icon)
            self.prev_button.set_sensitive(False)
            self.play_pause_button.set_sensitive(False)
            self.next_button.set_sensitive(False)
        else:
            if now_playing.is_track:
                self.artist_label.set_label('Unknown artist' if now_playing.artist_name is None else now_playing.artist_name)
                self.track_name_label.set_label('Unknown track' if now_playing.track_name is None else now_playing.track_name)
            else:
                self.artist_label.set_label('No track')
                self.track_name_label.set_label('')
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
                    pixbuf = pixbuf.scale_simple(dest_width, dest_height, GdkPixbuf.InterpType.BILINEAR)
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

            if now_playing.track_number:
                self.prev_button.set_sensitive(now_playing.track_number > 1)
                self.play_pause_button.set_sensitive(True)
                self.next_button.set_sensitive(now_playing.track_number < now_playing.album_tracks)
            else:
                self.prev_button.set_sensitive(False)
                self.play_pause_button.set_sensitive(False)
                self.next_button.set_sensitive(False)
