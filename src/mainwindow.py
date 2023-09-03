import logging
import os.path

import gi

from nowplaying import NowPlaying
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # noqa: E402 # need to call require_version before we can call this
from gi.repository import Gdk  # noqa: E402 # need to call require_version before we can call this
from gi.repository import GdkPixbuf  # noqa: E402 # need to call require_version before we can call this
gi.require_version('Pango', '1.0')
from gi.repository import Pango  # noqa: E402 # need to call require_version before we can call this

from apiclient import ApiClient  # noqa: E402 # libraries before local imports


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

MAX_IMAGE_SIZE = 300


def load_local_image(icon_name, icon_size):
    leafname = icon_name
    if icon_size:
        leafname += f'_{icon_size}'
    leafname += '.png'
    icon_filename = os.path.join(os.path.dirname(__file__), os.path.pardir, 'icons', leafname)
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


def mk_label(justification=Gtk.Justification.LEFT,
             large=True):
    label = Gtk.Label()
    label.set_hexpand(True)
    label.set_vexpand(True)
    label.set_line_wrap(True)
    label.set_justify(justification)
    set_font(label,
             Pango.Weight.BOLD if large else Pango.Weight.NORMAL,
             32 if large else 24,
             Gdk.Color.from_floats(0.0, 0.0, 0.0) if large else Gdk.Color.from_floats(0.3, 0.3, 0.3))
    return label


class MainWindow(Gtk.ApplicationWindow):
    """
    Main application window
    """

    def __init__(self,
                 apiclient: ApiClient,
                 full_screen: bool,
                 fixed_layout: bool,
                 show_close_button: bool,
                 hide_mouse_pointer: bool):
        Gtk.Window.__init__(self, title="PiJu")
        self.connect("destroy", self.on_quit)
        self.apiclient = apiclient
        if full_screen:
            self.fullscreen()
        else:
            self.set_size_request(SCREEN_WIDTH, SCREEN_HEIGHT)

        self.play_icon = None
        self.pause_icon = None

        self.current_image_uri = None

        self.artwork = Gtk.Image()
        self.artwork.set_hexpand(False)
        self.artwork.set_vexpand(False)
        self.artwork.set_size_request(MAX_IMAGE_SIZE, MAX_IMAGE_SIZE)
        self.track_name_label = mk_label(large=True)
        self.artist_label = mk_label(large=False)
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

        self.play_pause_button.connect('clicked', self.on_play_pause)

        self.play_pause_action = None

        self.scanning_indicator_icon = load_local_image('circle-solid', 16)

        close_icon = load_local_image('window-close-solid', 0)
        close = Gtk.Button()
        close.set_image(close_icon)
        close.connect('clicked', self.on_quit)

        # image          track
        #  ..            artist
        #  prev  play/pause   next

        if fixed_layout:
            self.no_track_label = mk_label(justification=Gtk.Justification.CENTER, large=False)

            fixed_container = Gtk.Fixed.new()
            x_padding = 10
            y0_padding = 10
            label_h = MAX_IMAGE_SIZE / 2
            fixed_container.put(self.artwork, x_padding, y0_padding)
            track_artist_x0 = x_padding + MAX_IMAGE_SIZE + x_padding
            fixed_container.put(self.track_name_label, track_artist_x0, y0_padding)
            artist_y0 = y0_padding + label_h + y0_padding
            fixed_container.put(self.artist_label, track_artist_x0, artist_y0)
            for label in (self.track_name_label, self.artist_label):
                label.set_size_request(SCREEN_WIDTH - track_artist_x0 - x_padding,
                                       label_h)
            no_track_label_w = 200
            fixed_container.put(self.no_track_label,
                                (SCREEN_WIDTH - no_track_label_w) / 2,
                                150)
            self.no_track_label.set_size_request(no_track_label_w, 32)
            # buttons
            # image is 100x100; button padding takes it to 112x110
            # (on macOS, at least)
            #   SPC  IMG  2xSPC  IMG  2xSPC  IMG  SPC
            # 6xSPC + 3xIMG = SCREEN_WIDTH
            # => SPC = (SCREEN_WIDTH - 3*IMG) / 6
            img_button_w = 112
            img_button_h = 110
            y1_padding = 20
            button_y0 = SCREEN_HEIGHT - y1_padding - img_button_h
            button_x_padding = (SCREEN_WIDTH - 3 * img_button_w) / 6
            fixed_container.put(self.prev_button, button_x_padding, button_y0)
            fixed_container.put(self.play_pause_button, (SCREEN_WIDTH - img_button_w) / 2, button_y0)
            fixed_container.put(self.next_button, SCREEN_WIDTH - button_x_padding - img_button_w, button_y0)

            fixed_container.put(self.scanning_indicator_icon, SCREEN_WIDTH - 20, 4)

            self.add(fixed_container)
        else:
            self.no_track_label = self.artist_label

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
            bottom_row_container.set_valign(Gtk.Align.START)

            child_container = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
            child_container.pack_start(top_row_container, expand=True, fill=True, padding=10)
            child_container.pack_end(bottom_row_container, expand=True, fill=False, padding=10)

            if show_close_button:
                overlay = Gtk.Overlay()
                overlay.add(child_container)

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
        self.apiclient.next()

    def on_play_pause(self, *args):
        if self.play_pause_action:
            self.play_pause_action()

    def on_previous(self, *args):
        self.apiclient.previous()

    def on_quit(self, *args):
        Gtk.main_quit()

    def on_realized(self, *args):
        if self.hide_mouse_pointer:
            self.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.BLANK_CURSOR))
        logging.debug("Main window realized: allocated size %ux%u",
                      self.get_allocated_width(), self.get_allocated_height())
        icon_size = 200 if (self.get_allocated_width() > 1000) else 100
        self.pause_icon = load_local_image('pause-solid', icon_size)
        self.play_icon = load_local_image('play-solid', icon_size)
        prev_icon = load_local_image('backward-solid', icon_size)
        self.prev_button.set_image(prev_icon)
        next_icon = load_local_image('forward-solid', icon_size)
        self.next_button.set_image(next_icon)

    def show_connection_error(self):
        self.artist_label.hide()
        self.track_name_label.hide()
        self.artwork.hide()
        self.no_track_label.show()
        self.no_track_label.set_label("Connection error")
        self.scanning_indicator_icon.hide()
        self.play_pause_button.set_image(self.play_icon)
        self.prev_button.set_sensitive(False)
        self.play_pause_button.set_sensitive(False)
        self.next_button.set_sensitive(False)

    def show_now_playing_artist_and_track(self, now_playing: NowPlaying):
        if now_playing.is_track:
            self.no_track_label.hide()
            self.artist_label.set_label(now_playing.artist_name or 'Unknown artist')
            self.track_name_label.set_label(now_playing.track_name or 'Unknown track')
            self.artist_label.show()
            self.track_name_label.show()
        elif now_playing.stream_name:
            self.no_track_label.hide()
            self.track_name_label.set_label(now_playing.stream_name)
            self.track_name_label.show()
            self.artist_label.hide()
        else:
            self.artist_label.hide()
            self.track_name_label.hide()
            self.no_track_label.set_label('No track')
            self.no_track_label.show()

    def show_now_playing_image_inner(self, now_playing: NowPlaying):
        """
        Returns True if successful
        """
        if not now_playing.image:
            return False
        loader = GdkPixbuf.PixbufLoader()
        try:
            loader.write(now_playing.image)
        except gi.repository.GLib.GError as exc:
            logging.error(f"Error loading image into pixbuf: {exc}")
            return False
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
        return True

    def show_now_playing_image(self, now_playing: NowPlaying):
        if now_playing.image_uri == self.current_image_uri:
            # Nothing to do
            return
        logging.debug("Updating image display")
        if not self.show_now_playing_image_inner(now_playing):
            self.artwork.hide()
        self.current_image_uri = now_playing.image_uri

    def show_now_playing_play_pause_icon(self, now_playing: NowPlaying):
        if now_playing.current_state == 'playing':
            self.play_pause_button.set_image(self.pause_icon)
            self.play_pause_action = self.apiclient.pause
        else:
            self.play_pause_button.set_image(self.play_icon)
            self.play_pause_action = self.apiclient.resume

    def show_now_playing_prev_next(self, now_playing: NowPlaying):
        have_track_number = bool(now_playing.track_number)
        self.prev_button.set_sensitive(have_track_number and now_playing.track_number > 1)
        self.play_pause_button.set_sensitive(have_track_number)
        self.next_button.set_sensitive(have_track_number
                                       and (now_playing.album_tracks is not None)
                                       and (now_playing.track_number < now_playing.album_tracks))

    def show_now_playing(self, connection_error: bool, now_playing: NowPlaying):
        if connection_error:
            self.show_connection_error()
            return

        self.show_now_playing_artist_and_track(now_playing)
        self.show_now_playing_image(now_playing)
        self.show_now_playing_play_pause_icon(now_playing)
        self.show_now_playing_prev_next(now_playing)

        self.scanning_indicator_icon.set_visible(now_playing.scanning_active)
